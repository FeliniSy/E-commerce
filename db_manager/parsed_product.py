from dataclasses import dataclass


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
