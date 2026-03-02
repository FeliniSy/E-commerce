from functools import lru_cache

from db_manager.queries import select_brand, insert_brand
from pipeline.loader.loader import loader


@lru_cache(maxsize=256)
def get_or_create_brand(name: str) -> int:
    result = loader.fetch(select_brand, params=(name,))
    if result:
        return result[0][0]
    result = loader.fetch(insert_brand, params=(name,))
    return result[0][0]
def extract_brand(product: dict) -> str | None:
    data = product["specificationGroup"][0]["specifications"][0]["specificationMeaning"]
    return data

