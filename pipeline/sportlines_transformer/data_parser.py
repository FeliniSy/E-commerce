import re
from html import unescape
from dataclasses import dataclass
from pipeline.alta_transformer.brand_handler import get_or_create_brand
from pipeline.sportlines_transformer.category_handler import get_or_create_sportlines_category


@dataclass
class ParsedProduct:
    category_id: int
    supplier_id: int
    brand_id: int
    cover_image_url: str
    title: str
    description: str
    price: float
    stock_quantity: int
    original_url: str
    sell_type: str
    cost_price: float = None
    sku: str = None


def clean_description(html_text: str) -> str:

    if not html_text:
        return ""

    text = unescape(html_text)

    text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'\s*data-[a-z-]+="[^"]*"', '', text)

    english_patterns = [
        r'\bstrong\b',
        r'\bbr\b',
        r'\bspan\b',
        r'\bdata-start\b',
        r'\bdata-end\b',
        r'\bdata-is-last-node\b',
        r'\bdata-is-only-node\b',
        r'\baria-hidden\b',
        r'\bscreen-reader-text\b',
    ]

    for pattern in english_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    text = re.sub(r'[^\u10A0-\u10FF\s.,;:!?—–\-\n()0-9]+', '', text)

    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    return text.strip()


def parse_sportlines_product(product_data: dict) -> ParsedProduct:

    categories = product_data.get("categories", [])
    category_id = get_or_create_sportlines_category(categories[0] if categories else None)

    brands = product_data.get("brands", [])
    brand_name = None

    if brands and len(brands) > 0:
        brand_name = brands[0].get("name")

    if not brand_name:
        product_title = product_data.get("name", "")
        if product_title:
            first_word = product_title.split()[0] if product_title.split() else None
            if first_word and len(first_word) > 2:
                print(f"⚠️  Sportlines: Using first word as brand: '{first_word}' from title: {product_title}")
                brand_name = first_word

    brand_id = get_or_create_brand(brand_name if brand_name else "Unknown")

    prices = product_data.get("prices", {})
    try:
        raw_price = prices.get("price", "0")
        clean_price = float(str(raw_price)) / 100 if raw_price else 0.0
    except (ValueError, TypeError):
        clean_price = 0.0

    is_in_stock = product_data.get("is_in_stock", False)
    stock_quantity = 1 if is_in_stock else 0

    images = product_data.get("images", [])
    cover_image = images[0].get("src") if images else None

    sku = product_data.get("sku") or str(product_data.get("id", ""))

    original_url = product_data.get("permalink", "")

    raw_description = product_data.get("description", "")
    description = clean_description(raw_description)

    return ParsedProduct(
        category_id=category_id,
        supplier_id=5,
        brand_id=brand_id,
        cover_image_url=cover_image,
        title=product_data.get("name", "Unknown"),
        description=description,
        price=clean_price,
        stock_quantity=stock_quantity,
        original_url=original_url,
        sell_type="retail",
        sku=sku
    )
