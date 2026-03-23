import asyncio
from urllib.parse import quote
from pipeline.extractor.scrapper import page_scrapper
from pipeline.loader.product_loader import insert_product_to_db
from pipeline.koncept_transformer.data_parser import parse_koncept_product
from pipeline.koncept_transformer.spec_handler import parse_koncept_specifications
from pipeline.koncept_transformer.image_handler import parse_koncept_images
from pipeline.koncept_transformer.category_handler import register_collection
from utils.logger import logger
from utils.settings import settings


async def fetch_and_register_collections():

    logger.info("Fetching Koncept collections...")
    try:
        data = await page_scrapper(settings.FURNITURE_CAT_API)
        collections = data.get("collections", [])

        logger.info(f"Found {len(collections)} collections")

        for collection in collections:
            collection_handle = collection.get("handle")
            collection_title = collection.get("title")
            products_count = collection.get("products_count", 0)

            if products_count > 0:
                register_collection(collection)
                logger.info(f"Registered collection: {collection_title} ({collection_handle}) - {products_count} products")

        return collections

    except Exception as e:
        logger.error(f"Failed to fetch collections: {e}", exc_info=True)
        return []


async def process_koncept_product(product_data: dict, collection_handle: str):

    product_id = product_data.get("id")
    try:
        logger.info(f"Processing Koncept product {product_id}")

        parsed = parse_koncept_product(product_data, collection_handle)
        logger.info(f"Product {product_id} — parsed: '{parsed.title}' | brand_id={parsed.brand_id}")

        db_product_id = insert_product_to_db(parsed)
        if db_product_id is None:
            logger.warning(f"Product {product_id} — insert returned None")
            return

        logger.info(f"Product {product_id} — inserted with db_id={db_product_id}")

        parse_koncept_images(product_data, db_product_id)
        parse_koncept_specifications(product_data, db_product_id, parsed.category_id)

        logger.info(f"Product {product_id} — done")

    except Exception as e:
        logger.error(f"Product {product_id} — FAILED: {e}", exc_info=True)


async def process_koncept_collection(collection: dict, product_semaphore: asyncio.Semaphore):

    collection_handle = collection.get("handle")
    collection_title = collection.get("title")
    products_count = collection.get("products_count", 0)

    if products_count == 0:
        logger.info(f"Collection {collection_title} has no products, skipping")
        return

    logger.info(f"Starting collection: {collection_title} ({collection_handle})")

    try:
        for page_num in range(1, 100):  # Max 100 pages
            logger.info(f"Collection {collection_handle} | Page {page_num}")

            encoded_handle = quote(collection_handle, safe='')
            url = settings.FURNITURE_PROD_API.format(encoded_handle, page_num)
            data = await page_scrapper(url)

            products = data.get("products", [])
            if not products:
                logger.info(f"Collection {collection_handle} | Page {page_num} — no products")
                break

            logger.info(f"Collection {collection_handle} | Page {page_num} — {len(products)} products")

            async def process_with_semaphore(product):
                async with product_semaphore:
                    await process_koncept_product(product, collection_handle)

            await asyncio.gather(*[process_with_semaphore(product) for product in products])

        logger.info(f"Completed collection: {collection_title}")

    except Exception as e:
        logger.error(f"Collection {collection_handle} — FAILED: {e}", exc_info=True)
