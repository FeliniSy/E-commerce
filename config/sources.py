from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SourceConfig:
    name: str
    supplier_id: int
    process_module: str
    process_function: str
    transformer_module: str
    data_parser_function: str
    spec_handler_function: str
    image_handler_function: str
    scraping_type: str  # 'category', 'collection', 'id_based', 'paginated'
    urls: Dict[str, str]
    extra_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_config is None:
            self.extra_config = {}


SOURCES = {
    'alta': SourceConfig(
        name='alta',
        supplier_id=1,
        process_module='processes.alta_process',
        process_function='process_category',
        transformer_module='pipeline.alta_transformer',
        data_parser_function='data_parser.parse_data',
        spec_handler_function='spec_handler.parse_specifications',
        image_handler_function='loader.product_loader.parse_images',
        scraping_type='category',
        urls={
            'category': 'https://api.alta.ge/v1/Products/v4?CategoryId={0}&Limit=200&Page={1}',
            'product': 'https://api.alta.ge/v1/Products/details?productId={0}'
        },
        extra_config={
            'category_range': (1, 295),
            'product_semaphore': 30,
            'category_semaphore': 10,
            'has_brand_handler': True,
            'has_address_handler': True
        }
    ),

    'koncept': SourceConfig(
        name='koncept',
        supplier_id=2,
        process_module='processes.koncept_process',
        process_function='process_koncept_collection',
        transformer_module='pipeline.koncept_transformer',
        data_parser_function='data_parser.parse_koncept_product',
        spec_handler_function='spec_handler.parse_koncept_specifications',
        image_handler_function='image_handler.parse_koncept_images',
        scraping_type='collection',
        urls={
            'collections': 'https://koncept.ge/collections.json?limit=100',
            'products': 'https://koncept.ge/collections/{0}/products.json?limit=250&page={1}'
        },
        extra_config={
            'product_semaphore': 10,
            'max_pages_per_collection': 100
        }
    ),

    'biblusi': SourceConfig(
        name='biblusi',
        supplier_id=3,
        process_module='processes.biblusi_process',
        process_function='process_biblusi_book',
        transformer_module='pipeline.biblusi_transformer',
        data_parser_function='data_parser.parse_biblusi_product',
        spec_handler_function='spec_handler.parse_biblusi_specifications',
        image_handler_function='image_handler.parse_biblusi_images',
        scraping_type='id_based',
        urls={
            'product': 'https://apiv1.biblusi.ge/api/book/{0}?author=1&category=1&rate=1',
            'category': 'https://apiv1.biblusi.ge/api/category',
            'all_books': 'https://apiv1.biblusi.ge/api/book?page={0}'
        },
        extra_config={
            'product_semaphore': 20
        }
    ),

    'sportlines': SourceConfig(
        name='sportlines',
        supplier_id=4,
        process_module='processes.sportlines_process',
        process_function='process_sportlines_product',
        transformer_module='pipeline.sportlines_transformer',
        data_parser_function='data_parser.parse_sportlines_product',
        spec_handler_function='spec_handler.parse_sportlines_specifications',
        image_handler_function='image_handler.parse_sportlines_images',
        scraping_type='paginated',
        urls={
            'products': 'https://sportlines.ge/wp-json/wc/store/products?per_page=100&page={}'
        },
        extra_config={
            'product_semaphore': 10,
            'max_pages': 100
        }
    )
}


def get_source_config(source_name: str) -> SourceConfig:
    if source_name not in SOURCES:
        available = ', '.join(SOURCES.keys())
        raise ValueError(f"Unknown source '{source_name}'. Available sources: {available}")
    return SOURCES[source_name]


def get_all_sources():
    return list(SOURCES.keys())
