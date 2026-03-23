from pipeline.loader.loader import loader
from db_manager.queries import insert_product_image
from utils.logger import logger


def parse_sportlines_images(product_data: dict, product_id: int):

    images = product_data.get("images", [])

    if not images:
        logger.debug(f"No images found for product {product_id}")
        return

    image_urls = []
    for img in images:
        src = img.get("src")
        if src:
            image_urls.append(src)

    if not image_urls:
        logger.debug(f"No valid image URLs for product {product_id}")
        return

    batch = [(product_id, url) for url in image_urls]

    try:
        loader.execute_many(insert_product_image, batch)
        logger.debug(f"Inserted {len(batch)} images for product {product_id}")
    except Exception as e:
        logger.error(f"Failed to insert images for product {product_id}: {e}")
