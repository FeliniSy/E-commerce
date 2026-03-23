import asyncio
from processes.sportlines_process import run_sportlines_scraper
from pipeline.extractor.scrapper import close_browser
from utils.logger import logger


async def main():

    logger.info("=" * 60)
    logger.info("Starting Sportlines E-commerce Scraper")
    logger.info("=" * 60)

    try:

        await run_sportlines_scraper(max_pages=100, max_concurrent_products=10)

        logger.info("=" * 60)
        logger.info("Sportlines scraper finished successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Sportlines scraper failed: {e}", exc_info=True)
        logger.info("=" * 60)
    finally:
        # Clean up browser resources
        await close_browser()


if __name__ == "__main__":
    asyncio.run(main())
