from functools import lru_cache

from db_manager.queries import insert_category, select_category
from pipeline.loader.loader import loader
from utils.helper import slugify


@lru_cache(maxsize=512)
def get_or_create_category(name: str, parent_id: int | None, image_url: str | None) -> int:
    result = check_category(name)
    if result is not None:
        return result

    loader.execute(insert_category, params=(name, parent_id, slugify(name), image_url))
    result = check_category(name)
    if result is None:
        raise ValueError(f"Failed to insert/find category: {name}")
    return result

def check_category(name: str) -> int | None:
    result = loader.fetch(select_category, params=(name,))
    return result[0][0] if result else None

