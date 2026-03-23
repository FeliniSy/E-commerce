
from db_manager.parsed_product import ParsedProduct
from pipeline.alta_transformer.brand_handler import get_or_create_brand
from pipeline.koncept_transformer.category_handler import get_or_create_collection_category



def parse_koncept_product(product_data: dict, collection_handle: str) -> ParsedProduct:
    category_id = get_or_create_collection_category(collection_handle)

    brand_name = product_data.get("vendor")

    if not brand_name:
        product_title = product_data.get("title", "")
        if product_title:
            first_word = product_title.split()[0] if product_title.split() else None
            if first_word and len(first_word) > 2:
                print(f"⚠️  Koncept: Using first word as brand: '{first_word}' from title: {product_title}")
                brand_name = first_word

    brand_id = get_or_create_brand(brand_name if brand_name else "Unknown")

    variants = product_data.get("variants", [])
    first_variant = variants[0] if variants else {}

    try:
        raw_price = first_variant.get("price", "0")
        clean_price = float(str(raw_price).replace(',', '.').strip()) if raw_price else 0.0
    except (ValueError, TypeError):
        clean_price = 0.0

    is_available = first_variant.get("available", False)
    stock_quantity = 1 if is_available else 0

    images = product_data.get("images", [])
    cover_image = images[0].get("src") if images else None

    sku = first_variant.get("sku") or str(product_data.get("id", ""))

    handle = product_data.get("handle", "")
    original_url = f"https://koncept.ge/products/{handle}" if handle else ""

    description = product_data.get("body_html", "")

    return ParsedProduct(
        category_id=category_id,
        supplier_id=2,
        brand_id=brand_id,
        cover_image_url=cover_image,
        title=product_data.get("title", "Unknown"),
        description=description,
        price=clean_price,
        stock_quantity=stock_quantity,
        original_url=original_url,
        sell_type="retail",
        sku=sku
    )
