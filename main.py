import asyncio
from datetime import datetime

from main.alta_process import process_category
from pipeline.extractor.scrapper import  close_browser

from utils.logger import logger




async def main():
    try:
        product_semaphore = asyncio.Semaphore(30)
        category_semaphore = asyncio.Semaphore(10)

        #process alta
        async def process_category_with_semaphore(category_id):
            async with category_semaphore:
                await process_category(category_id, product_semaphore)

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