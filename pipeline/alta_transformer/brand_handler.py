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


def clear_brand_cache():
    get_or_create_brand.cache_clear()
    print("✓ Brand cache cleared")


def extract_brand(product: dict) -> str | None:
    try:
        if "brandName" in product and product["brandName"]:
            return product["brandName"]

        if "brand" in product and product["brand"]:
            return product["brand"]

        spec_groups = product.get("specificationGroup", [])
        if not spec_groups:
            print(f"⚠️  No specificationGroup found for product: {product.get('name', 'Unknown')}")
            return None

        for spec_group in spec_groups:
            specifications = spec_group.get("specifications", [])
            if not specifications:
                continue

            for spec in specifications:
                if spec.get("specificationName") == "ბრენდი":
                    brand = spec.get("specificationMeaning")
                    if brand:
                        print(f"✓ Found brand: {brand} for product: {product.get('name', 'Unknown')}")
                        return brand

        print(f"⚠️  No brand found in specifications for product: {product.get('name', 'Unknown')}")
        return None

    except (KeyError, IndexError, TypeError) as e:
        print(f"❌ Error extracting brand: {e} for product: {product.get('name', 'Unknown')}")
        return None
