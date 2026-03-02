import asyncio
from datetime import datetime

from pipeline.extractor.scrapper import page_scrapper, close_browser
from pipeline.loader.product_loader import insert_product_to_db, parse_images
from pipeline.transformer.address_handler import parse_addresses
from pipeline.transformer.data_parser import parse_data
from pipeline.transformer.spec_handler import parse_specifications
from utils.helper import get_data_id
from utils.settings import settings
from utils.logger import logger


async def process_product(item: int):
    try:
        logger.info(f"Processing product {item}")
        product_info = await page_scrapper(settings.PRODUCT_URL, item)

        if not product_info.get("success"):
            logger.warning(f"Product {item} — success=False, skipping")
            return

        parsed = parse_data(product_info)
        logger.info(f"Product {item} — parsed: '{parsed.title}' | brand_id={parsed.brand_id}")

        db_product_id = insert_product_to_db(parsed)
        if db_product_id is None:
            logger.warning(f"Product {item} — insert returned None")
            return

        logger.info(f"Product {item} — inserted with db_id={db_product_id}")
        parse_images(product_info, db_product_id)
        parse_specifications(product_info, db_product_id, parsed.category_id)
        parse_addresses(product_info, db_product_id)
        logger.info(f"Product {item} — done")

    except Exception as e:
        logger.error(f"Product {item} — FAILED: {e}", exc_info=True)


async def main():
    main_page_url = settings.MAIN_URL
    try:
        for i in range(1, 295):
            logger.info(f"Starting category {i}")
            for j in range(1, 10001):
                logger.info(f"Category {i} | Page {j}")
                data = await page_scrapper(main_page_url, i, j)

                if data.get('httpStatusCode') == 500:
                    logger.warning(f"Category {i} | Page {j} — 500 error")
                    break

                products = data.get('products', [])
                if not products:
                    logger.info(f"Category {i} | Page {j} — no products")
                    break

                product_ids = get_data_id(products)
                logger.info(f"Category {i} | Page {j} — {len(product_ids)} products")

                semaphore = asyncio.Semaphore(5)

                async def process_with_semaphore(item):
                    async with semaphore:
                        await process_product(item)

                await asyncio.gather(*[process_with_semaphore(item) for item in product_ids])

                await asyncio.sleep(0.5)

    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}", exc_info=True)
    finally:
        await close_browser()


if __name__ == "__main__":
    start = datetime.now()
    print(start)
    asyncio.run(main())
    end = datetime.now()
    print(end-start)