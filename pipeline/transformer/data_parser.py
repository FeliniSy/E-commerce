import json
from dataclasses import dataclass

from gcs_manager.gcs_client import gcs_client
from pipeline.transformer.brand_handler import get_or_create_brand, extract_brand
from pipeline.transformer.category_handler import get_or_create_category
from utils.helper import get_images_url


@dataclass
class ParsedProduct:
    category_id: int
    supplier_id: int
    brand_id: int
    cover_image_url: str
    title: str
    description: str
    price: float
    stock_quantity: int
    original_url: str
    sell_type: str
    cost_price: float = None
    sku: str = None


def parse_data(product_data: dict) -> ParsedProduct:
    product = product_data.get("product", {})

    parent_cat_id = get_or_create_category(
        name=product["parentCategoryName"],
        parent_id=1,
        image_url=gcs_client.upload_image(get_images_url(name=product["parentCategoryName"]),
                                          product["parentCategoryName"])
    )
    category_id = get_or_create_category(
        name=product["categoryName"],
        parent_id=parent_cat_id,
        image_url=None
    )

    brand_name = extract_brand(product)
    brand_id = get_or_create_brand(brand_name) if brand_name else get_or_create_brand("Unknown")

    return ParsedProduct(
        category_id=category_id,
        supplier_id=1,
        brand_id=brand_id,
        cover_image_url=product["imageUrl"],
        title=product["name"],
        description=product["description"],
        price=product["price"],
        stock_quantity=product["storageQuantity"],
        original_url=product["shareRoute"],
        sell_type=product["sellType"],
    )
