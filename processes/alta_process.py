import asyncio

from pipeline.extractor.scrapper import page_scrapper
from pipeline.loader.product_loader import insert_product_to_db, parse_images
from pipeline.alta_transformer.address_handler import parse_addresses
from pipeline.alta_transformer.data_parser import parse_data
from pipeline.alta_transformer.spec_handler import parse_specifications
from utils.helper import get_data_id
from utils.logger import logger
from utils.settings import settings

async def process_product(item: int):
    try:
        logger.info(f"Processing product {item}")
        product_info = await page_scrapper(settings.ALTA_PRODUCT_URL, item)

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
    main_page_url = settings.ALTA_CAT_URL
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
