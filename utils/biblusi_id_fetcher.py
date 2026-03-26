import asyncio
from pipeline.extractor.scrapper import page_scrapper
from utils.settings import settings
from utils.logger import logger


async def fetch_all_biblusi_ids() -> list[int]:
    all_ids = []

    logger.info("Starting to fetch all Biblusi book IDs from pages 1-367")

    for page_num in range(1, 318):
        try:
            logger.info(f"Fetching IDs from page {page_num}")

            data = await page_scrapper(settings.BIBLUSI_API, page_num)

            books = data.get("data", [])

            if not books:
                logger.warning(f"Page {page_num} - no books found")
                continue

            page_ids = [book.get("id") for book in books if book.get("id") is not None]
            all_ids.extend(page_ids)

            logger.info(f"Page {page_num} - collected {len(page_ids)} IDs (total: {len(all_ids)})")

        except Exception as e:
            logger.error(f"Page {page_num} - FAILED: {e}", exc_info=True)
            continue

    logger.info(f"Completed fetching all IDs. Total: {len(all_ids)} book IDs")
    return all_ids


async def main():
    ids = await fetch_all_biblusi_ids()
    print(f"Total IDs collected: {len(ids)}")
    print(f"First 10 IDs: {ids[:10]}")
    return ids

#
# if __name__ == "__main__":
#     asyncio.run(main())
