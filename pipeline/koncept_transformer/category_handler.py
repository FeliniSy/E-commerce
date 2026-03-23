from functools import lru_cache
from db_manager.queries import insert_category, select_category
from pipeline.loader.loader import loader
from utils.helper import slugify


_collection_cache = {}


@lru_cache(maxsize=512)
def get_or_create_category(name: str, parent_id: int | None, image_url: str | None) -> int:
    loader.execute(insert_category, params=(name, parent_id, slugify(name), image_url))
    result = check_category(name)
    if result is None:
        raise ValueError(f"Failed to insert/find category: {name}")
    return result


def check_category(name: str) -> int | None:
    result = loader.fetch(select_category, params=(name,))
    return result[0][0] if result else None


def register_collection(collection_data: dict) -> None:
    handle = collection_data.get("handle")
    title = collection_data.get("title", "Unknown")
    image_data = collection_data.get("image")
    image_url = image_data.get("src") if image_data else None

    category_id = get_or_create_category(
        name=title,
        parent_id=161,
        image_url=image_url
    )

    _collection_cache[handle] = category_id


def get_or_create_collection_category(collection_handle: str) -> int:

    if collection_handle in _collection_cache:
        return _collection_cache[collection_handle]

    category_id = get_or_create_category(
        name=collection_handle,
        parent_id=161,
        image_url=None
    )
    _collection_cache[collection_handle] = category_id
    return category_id
