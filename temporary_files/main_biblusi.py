import asyncio
from datetime import datetime

from processes.biblusi_process import process_biblusi
from pipeline.extractor.scrapper import close_browser

from utils.logger import logger


async def main():
    try:
        product_semaphore = asyncio.Semaphore(10)

        await process_biblusi(product_semaphore)

    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}", exc_info=True)
    finally:
        await close_browser()


if __name__ == "__main__":
    start = datetime.now()
    print(f"Started at: {start}")
    asyncio.run(main())
    end = datetime.now()
    print(f"Duration: {end - start}")
