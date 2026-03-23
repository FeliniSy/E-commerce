import re
from html import unescape
from pipeline.loader.loader import loader
from utils.logger import logger


def clean_koncept_description(html_text: str) -> str:
    """
    Remove HTML tags and English words, keeping only Georgian text.
    """
    if not html_text:
        return ""

    # Decode HTML entities
    text = unescape(html_text)

    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove HTML attributes like data-start, data-end, etc.
    text = re.sub(r'\s*data-[a-z-]+="[^"]*"', '', text)

    # Remove common English words and phrases
    english_patterns = [
        r'\bKoncept\b',
        r'\bstrong\b',
        r'\bbr\b',
        r'\bspan\b',
        r'\bdata-start\b',
        r'\bdata-end\b',
        r'\bdata-is-last-node\b',
        r'\bdata-is-only-node\b',
    ]

    for pattern in english_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Remove emojis and special symbols (keep Georgian unicode range)
    # Georgian unicode range: \u10A0-\u10FF
    # Keep Georgian, spaces, punctuation, and line breaks
    text = re.sub(r'[^\u10A0-\u10FF\s.,;:!?—–\-\n()]+', '', text)

    # Clean up multiple spaces and line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    return text.strip()


def update_koncept_descriptions():
    """
    Fetch all Koncept products and update their descriptions.
    """
    logger.info("Starting Koncept description cleanup...")

    # Fetch all products from Koncept supplier (supplier_id = 2)
    query = """
        SELECT id, title, description
        FROM products
        WHERE supplier_id = 2
        AND description IS NOT NULL
        AND description != ''
    """

    products = loader.fetch(query)

    if not products:
        logger.info("No Koncept products found with descriptions")
        return

    logger.info(f"Found {len(products)} Koncept products with descriptions")

    updated_count = 0
    skipped_count = 0

    for product in products:
        product_id = product[0]
        title = product[1]
        old_description = product[2]

        # Clean the description
        new_description = clean_koncept_description(old_description)

        if new_description and new_description != old_description:
            # Update the database
            update_query = """
                UPDATE products
                SET description = %s
                WHERE id = %s
            """

            try:
                loader.execute(update_query, (new_description, product_id))
                updated_count += 1
                logger.info(f"Updated product {product_id}: {title}")
                logger.debug(f"Old: {old_description[:100]}...")
                logger.debug(f"New: {new_description[:100]}...")
            except Exception as e:
                logger.error(f"Failed to update product {product_id}: {e}")
        else:
            skipped_count += 1
            logger.debug(f"Skipped product {product_id}: {title} (no changes or empty result)")

    logger.info(f"Cleanup complete: {updated_count} updated, {skipped_count} skipped")


if __name__ == "__main__":
    update_koncept_descriptions()
