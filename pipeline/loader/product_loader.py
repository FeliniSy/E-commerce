from db_manager.queries import select_product, insert_product, insert_product_image
from pipeline.loader.loader import loader
from pipeline.alta_transformer.data_parser import ParsedProduct


def insert_product_to_db(parsed: ParsedProduct) -> int | None:
    result = loader.fetch(insert_product, params=(
        parsed.category_id,
        parsed.supplier_id,
        parsed.brand_id,
        parsed.cover_image_url,
        parsed.title,
        parsed.description,
        parsed.price,
        parsed.cost_price or 0,
        parsed.sku or parsed.original_url,
        parsed.stock_quantity,
        parsed.original_url,
        parsed.sell_type,
        True
    ))
    return result[0][0] if result else None


def parse_images(product_data: dict, product_id: int):
    images = product_data.get("product", {}).get("images", [])
    if not images:
        return
    batch = [(product_id, url) for url in images]
    loader.execute_many(insert_product_image, batch)


