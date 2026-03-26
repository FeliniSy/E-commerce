import html
import re
from db_manager.parsed_product import ParsedProduct


def clean_html_description(description: str) -> str:
    if not description:
        return ""

    decoded = html.unescape(description)

    cleaned = re.sub(r'<[^>]+>', '', decoded)

    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()


def extract_brand_from_specs(variations: list) -> str | None:
    if not variations:
        return None

    for variation in variations:
        specs = variation.get("specs", [])
        for spec in specs:
            element = spec.get("element", {})
            label = element.get("label", "")
            value = spec.get("value", "")

            if label == "ბრენდი" and value and value.lower() != "null":
                return value

    return None


def parse_biblusi_product(book_data: dict) -> ParsedProduct:

    category_id = book_data.get("category_id")

    book_id = book_data.get("id")
    title = book_data.get("name", "Unknown")

    variations = book_data.get("variations", [])
    if variations:
        first_variation = variations[0]
        try:
            price = float(first_variation.get("price", 0))
        except (ValueError, TypeError):
            price = 0.0

        try:
            stock_str = first_variation.get("stock_count", "0")
            stock_quantity = int(stock_str) if stock_str and stock_str != "" else 0
        except (ValueError, TypeError):
            stock_quantity = 0
    else:
        price = 0.0
        stock_quantity = 0

    pictures = book_data.get("pictures", [])
    cover_image_url = pictures[0] if pictures else None

    original_url = f"https://biblusi.ge/products/{book_id}"

    raw_description = book_data.get("description", "")
    description = clean_html_description(raw_description)

    sku = str(book_id)

    brand_name = extract_brand_from_specs(variations)

    return ParsedProduct(
        category_id=category_id,
        supplier_id=6,
        brand_id=1,
        cover_image_url=cover_image_url,
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        original_url=original_url,
        sell_type="retail",
        sku=sku
    )
