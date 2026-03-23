from pipeline.loader.loader import loader
from db_manager.queries import insert_product_image
from utils.logger import logger


def parse_koncept_images(product_data: dict, db_product_id: int) -> None:

    try:
        images = product_data.get("images", [])

        for image in images:
            image_url = image.get("src")

            if image_url:
                loader.execute(
                    insert_product_image,
                    params=(db_product_id, image_url)
                )

        logger.info(f"Product {db_product_id} — saved {len(images)} images")

    except Exception as e:
        logger.error(f"Failed to parse images for product {db_product_id}: {e}", exc_info=True)
