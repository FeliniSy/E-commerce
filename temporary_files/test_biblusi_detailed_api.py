import asyncio
from pipeline.extractor.scrapper import page_scrapper, close_browser
from pipeline.biblusi_transformer.data_parser import parse_biblusi_product
from utils.settings import settings
from utils.logger import logger


async def test_detailed_api():
    """Test the detailed Biblusi API parsing"""

    try:
        # Test with product ID 27060
        book_id = 27060
        url = settings.BIBLUSI_PROD_API.format(book_id)

        logger.info(f"Fetching product {book_id} from: {url}")
        book_data = await page_scrapper(url)

        if not book_data:
            logger.error("No data returned from API")
            return

        logger.info(f"Received data for book: {book_data.get('name')}")

        # Test parsing
        parsed = parse_biblusi_product(book_data)

        logger.info("=" * 60)
        logger.info("PARSED PRODUCT:")
        logger.info(f"  ID (SKU): {parsed.sku}")
        logger.info(f"  Title: {parsed.title}")
        logger.info(f"  Category ID: {parsed.category_id}")
        logger.info(f"  Price: {parsed.price}")
        logger.info(f"  Stock: {parsed.stock_quantity}")
        logger.info(f"  Description: {parsed.description[:100]}..." if len(parsed.description) > 100 else f"  Description: {parsed.description}")
        logger.info(f"  Cover Image: {parsed.cover_image_url}")
        logger.info(f"  Original URL: {parsed.original_url}")
        logger.info("=" * 60)

        # Check specs
        variations = book_data.get("variations", [])
        if variations:
            specs = variations[0].get("specs", [])
            logger.info(f"\nFound {len(specs)} specifications:")
            for spec in specs:
                value = spec.get("value", "")
                element = spec.get("element", {})
                label = element.get("label", "")
                if value and value.lower() != "null":
                    logger.info(f"  {label}: {value}")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await close_browser()


if __name__ == "__main__":
    asyncio.run(test_detailed_api())
