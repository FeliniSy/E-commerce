import asyncio
from datetime import datetime

from processes.koncept_process import fetch_and_register_collections, process_koncept_collection
from pipeline.extractor.scrapper import close_browser
from pipeline.alta_transformer.brand_handler import clear_brand_cache

from utils.logger import logger


async def main():
    try:
        clear_brand_cache()

        product_semaphore = asyncio.Semaphore(30)
        category_semaphore = asyncio.Semaphore(10)

        logger.info("=" * 50)
        logger.info("STARTING KONCEPT PROCESSING")
        logger.info("=" * 50)

        collections = await fetch_and_register_collections()

        collections_with_products = [
            c for c in collections if c.get("products_count", 0) > 0
        ]

        logger.info(f"Processing {len(collections_with_products)} collections with products")

        async def process_with_semaphore(collection):
            async with category_semaphore:
                await process_koncept_collection(collection, product_semaphore)

        await asyncio.gather(*[
            process_with_semaphore(c) for c in collections_with_products
        ])

        logger.info("✓ Koncept processing complete")

    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}", exc_info=True)
    finally:
        await close_browser()


if __name__ == "__main__":
    start = datetime.now()
    print(f"Started at: {start}")
    asyncio.run(main())
    end = datetime.now()
    print(f"Finished at: {end}")
    print(f"Total time: {end - start}")
