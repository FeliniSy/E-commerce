from pipeline.loader.loader import loader
from db_manager.queries import select_category, insert_category
from utils.logger import logger

category_cache = {}

# Parent category ID for all Sportlines categories
SPORTLINES_PARENT_CATEGORY_ID = 372


def get_or_create_sportlines_category(category_data: dict | None) -> int:

    if not category_data:
        return get_or_create_category("სხვა", "sxva")

    category_name = category_data.get("name", "სხვა")
    category_slug = category_data.get("slug", "sxva")

    if category_name in category_cache:
        return category_cache[category_name]

    result = loader.fetch(select_category, (category_name,))

    if result and len(result) > 0:
        category_id = result[0][0]
        category_cache[category_name] = category_id
        logger.debug(f"Found existing category: {category_name} (ID: {category_id})")
        return category_id

    logger.info(f"Creating new category: {category_name} (slug: {category_slug})")
    result = loader.fetch(insert_category, (category_name, SPORTLINES_PARENT_CATEGORY_ID, category_slug, None))
    category_id = result[0][0] if result and len(result) > 0 else None

    if category_id:
        category_cache[category_name] = category_id
        logger.info(f"Created category: {category_name} (ID: {category_id})")

    return category_id


def get_or_create_category(name: str, slug: str) -> int:

    if name in category_cache:
        return category_cache[name]

    result = loader.fetch(select_category, (name,))

    if result and len(result) > 0:
        category_id = result[0][0]
        category_cache[name] = category_id
        return category_id

    logger.info(f"Creating new category: {name} (slug: {slug})")
    result = loader.fetch(insert_category, (name, SPORTLINES_PARENT_CATEGORY_ID, slug, None))
    category_id = result[0][0] if result and len(result) > 0 else None

    if category_id:
        category_cache[name] = category_id

    return category_id
