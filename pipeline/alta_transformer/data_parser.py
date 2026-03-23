from db_manager.parsed_product import ParsedProduct
from gcs_manager.gcs_client import gcs_client
from pipeline.alta_transformer.brand_handler import get_or_create_brand, extract_brand
from pipeline.alta_transformer.category_handler import get_or_create_category
from utils.helper import get_images_url



def parse_data(product_data: dict) -> ParsedProduct:
    product = product_data.get("product", {})
    parent_cat_name = product.get("parentCategoryName")

    parent_image_url = None
    try:
        if parent_cat_name:
            img_source_url = get_images_url(name=parent_cat_name)
            if img_source_url:
                parent_image_url = gcs_client.upload_image(img_source_url, parent_cat_name)
    except Exception as e:
        print(f"warning: the images is not uploaded for the category {parent_cat_name}: {e}")
        parent_image_url = None

    parent_cat_id = get_or_create_category(
        name=parent_cat_name,
        parent_id=1,
        image_url=parent_image_url
    )

    category_id = get_or_create_category(
        name=product.get("categoryName"),
        parent_id=parent_cat_id,
        image_url=None
    )

    brand_name = extract_brand(product)

    if not brand_name:
        product_name = product.get("name", "")
        if product_name:
            first_word = product_name.split()[0] if product_name.split() else None
            if first_word and len(first_word) > 2:
                print(f"⚠️  Using first word as brand: '{first_word}' from product: {product_name}")
                brand_name = first_word

    brand_id = get_or_create_brand(brand_name if brand_name else "Unknown")

    try:
        raw_price = product.get("price", 0)
        clean_price = float(str(raw_price).replace(',', '.').strip()) if raw_price else 0.0
    except ValueError:
        clean_price = 0.0

    return ParsedProduct(
        category_id=category_id,
        supplier_id=1,
        brand_id=brand_id,
        cover_image_url=product.get("imageUrl"),
        title=product.get("name", "Unknown"),
        description=product.get("description", ""),
        price=clean_price,
        stock_quantity=product.get("storageQuantity", 0),
        original_url=product.get("shareRoute"),
        sell_type=product.get("sellType", "retail"),
        sku=product.get("sku") or product.get("id")
    )
