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


async def process_category(category_id: int, product_semaphore: asyncio.Semaphore):
    main_page_url = settings.MAIN_URL
    logger.info(f"Starting category {category_id}")

    try:
        for page_num in range(1, 10001):
            logger.info(f"Category {category_id} | Page {page_num}")
            data = await page_scrapper(main_page_url, category_id, page_num)

            if data.get('httpStatusCode') == 500:
                logger.warning(f"Category {category_id} | Page {page_num} — 500 error")
                break

            products = data.get('products', [])
            if not products:
                logger.info(f"Category {category_id} | Page {page_num} — no products")
                break

            product_ids = get_data_id(products)
            logger.info(f"Category {category_id} | Page {page_num} — {len(product_ids)} products")

            async def process_with_semaphore(item):
                async with product_semaphore:
                    await process_product(item)

            await asyncio.gather(*[process_with_semaphore(item) for item in product_ids])

        logger.info(f"Completed category {category_id}")
    except Exception as e:
        logger.error(f"Category {category_id} — FAILED: {e}", exc_info=True)


async def main():
    try:
        # Semaphore for concurrent products across all categories
        product_semaphore = asyncio.Semaphore(30)
        # Semaphore for concurrent categories
        category_semaphore = asyncio.Semaphore(10)

        async def process_category_with_semaphore(category_id):
            async with category_semaphore:
                await process_category(category_id, product_semaphore)

        # Process all categories in parallel
        await asyncio.gather(*[
            process_category_with_semaphore(i) for i in range(1, 295)
        ])

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