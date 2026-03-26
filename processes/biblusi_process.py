import asyncio
from pipeline.extractor.scrapper import page_scrapper
from pipeline.loader.product_loader import insert_product_to_db
from pipeline.biblusi_transformer.data_parser import parse_biblusi_product
from pipeline.biblusi_transformer.spec_handler import parse_biblusi_specifications
from pipeline.biblusi_transformer.image_handler import parse_biblusi_images
from utils.biblusi_id_fetcher import fetch_all_biblusi_ids
from utils.logger import logger
from utils.settings import settings


async def process_biblusi_book(book_id: int):

    try:
        logger.info(f"Processing Biblusi book {book_id}")

        url = settings.BIBLUSI_PROD_API.format(book_id)
        book_data = await page_scrapper(url)

        if not book_data or not book_data.get("id"):
            logger.warning(f"Book {book_id} — no data returned from API")
            return

        parsed = parse_biblusi_product(book_data)
        logger.info(f"Book {book_id} — parsed: '{parsed.title}' | category_id={parsed.category_id}")

        db_product_id = insert_product_to_db(parsed)
        if db_product_id is None:
            logger.warning(f"Book {book_id} — insert returned None")
            return

        logger.info(f"Book {book_id} — inserted with db_id={db_product_id}")

        parse_biblusi_images(book_data, db_product_id)
        parse_biblusi_specifications(book_data, db_product_id, parsed.category_id)

        logger.info(f"Book {book_id} — done")

    except Exception as e:
        logger.error(f"Book {book_id} — FAILED: {e}", exc_info=True)


async def process_biblusi(product_semaphore: asyncio.Semaphore):
    logger.info("Starting Biblusi scraping process")

    try:
        logger.info("Fetching all Biblusi product IDs...")
        all_ids = await fetch_all_biblusi_ids()
        logger.info(f"Found {len(all_ids)} product IDs to process")

        async def process_with_semaphore(book_id):
            async with product_semaphore:
                await process_biblusi_book(book_id)

        await asyncio.gather(*[process_with_semaphore(book_id) for book_id in all_ids])

        logger.info(f"Completed Biblusi scraping process - {len(all_ids)} products processed")

    except Exception as e:
        logger.error(f"Biblusi process FAILED: {e}", exc_info=True)
