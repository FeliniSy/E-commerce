import asyncio
from pipeline.extractor.scrapper import page_scrapper
from pipeline.loader.product_loader import insert_product_to_db
from pipeline.sportlines_transformer.data_parser import parse_sportlines_product
from pipeline.sportlines_transformer.spec_handler import parse_sportlines_specifications
from pipeline.sportlines_transformer.image_handler import parse_sportlines_images
from utils.logger import logger


SPORTLINES_API_URL = "https://sportlines.ge/wp-json/wc/store/products?per_page=100&page={}"


async def process_sportlines_product(product_data: dict):

    product_id = product_data.get("id")
    try:
        logger.info(f"Processing Sportlines product {product_id}")

        parsed = parse_sportlines_product(product_data)
        logger.info(f"Product {product_id} — parsed: '{parsed.title}' | brand_id={parsed.brand_id}")

        db_product_id = insert_product_to_db(parsed)
        if db_product_id is None:
            logger.warning(f"Product {product_id} — insert returned None")
            return

        logger.info(f"Product {product_id} — inserted with db_id={db_product_id}")

        parse_sportlines_images(product_data, db_product_id)
        parse_sportlines_specifications(product_data, db_product_id, parsed.category_id)

        logger.info(f"Product {product_id} — done")

    except Exception as e:
        logger.error(f"Product {product_id} — FAILED: {e}", exc_info=True)


async def process_sportlines_page(page_num: int, product_semaphore: asyncio.Semaphore):

    logger.info(f"Fetching Sportlines page {page_num}")

    try:
        url = SPORTLINES_API_URL.format(page_num)
        response = await page_scrapper(url)

        # Extract products list from response
        if isinstance(response, dict):
            products = response.get("data", [])
        elif isinstance(response, list):
            products = response
        else:
            products = []

        if not products:
            logger.info(f"Page {page_num} — no products or invalid response")
            return 0

        logger.info(f"Page {page_num} — {len(products)} products found")

        async def process_with_semaphore(product):
            async with product_semaphore:
                await process_sportlines_product(product)

        await asyncio.gather(*[process_with_semaphore(product) for product in products])

        return len(products)

    except Exception as e:
        logger.error(f"Page {page_num} — FAILED: {e}", exc_info=True)
        return 0


async def run_sportlines_scraper(max_pages: int = 100, max_concurrent_products: int = 10):

    logger.info("Starting Sportlines scraper...")

    product_semaphore = asyncio.Semaphore(max_concurrent_products)

    for page_num in range(1, max_pages + 1):
        products_count = await process_sportlines_page(page_num, product_semaphore)

        # If no products found, we've reached the end
        if products_count == 0:
            logger.info(f"No more products found at page {page_num}. Stopping.")
            break

    logger.info("Sportlines scraper completed!")
