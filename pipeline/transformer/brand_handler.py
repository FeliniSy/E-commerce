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
    try:
        spec_groups = product.get("specificationGroup", [])
        if not spec_groups:
            return None

        specifications = spec_groups[0].get("specifications", [])
        if not specifications:
            return None

        brand = specifications[0].get("specificationMeaning")
        return brand if brand else None

    except (KeyError, IndexError, TypeError):
        return None

