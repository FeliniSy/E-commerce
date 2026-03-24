from db_manager.queries import select_field_group, insert_field_group, select_field, insert_field, select_option, \
    insert_option, select_category_field, insert_category_field, insert_pfv
from pipeline.loader.loader import loader
from utils.logger import logger


def parse_specifications(product_data: dict, product_id: int, category_id: int):
    spec_groups = product_data.get("product", {}).get("specificationGroup", [])

    pfv_batch = []

    for group in spec_groups:
        group_name = group.get("groupName")
        if not group_name:
            continue

        group_id = get_or_create_field_group(group_name)

        for spec in group.get("specifications", []):
            spec_name = spec.get("specificationName")
            spec_value = spec.get("specificationMeaning")
            if not spec_name or not spec_value:
                continue

            field_id = get_or_create_field(spec_name, group_id)
            option_id = get_or_create_option(spec_value, field_id)
            get_or_create_category_field(category_id, field_id, option_id)
            pfv_batch.append((product_id, field_id, option_id))

    if pfv_batch:
        loader.execute_many(insert_pfv, pfv_batch)

def get_or_create_field_group(name: str) -> int:
    result = loader.fetch(select_field_group, params=(name,))
    if result:
        return result[0][0]
    loader.execute(insert_field_group, params=(name,))
    return loader.fetch(select_field_group, params=(name,))[0][0]


def get_or_create_field(name: str, group_id: int) -> int:
    result = loader.fetch(select_field, params=(name, group_id))
    if result:
        return result[0][0]
    loader.execute(insert_field, params=(name, group_id))
    return loader.fetch(select_field, params=(name, group_id))[0][0]


def get_or_create_option(value: str, field_id: int) -> int:
    result = loader.fetch(select_option, params=(field_id, value))
    if result:
        return result[0][0]
    loader.execute(insert_option, params=(field_id, value))
    return loader.fetch(select_option, params=(field_id, value))[0][0]

def get_or_create_category_field(category_id: int, field_id: int, option_id: int):
    result = loader.fetch(select_category_field, params=(category_id, field_id, option_id))
    if result:
        return result[0][0]
    loader.execute(insert_category_field, params=(category_id, field_id, option_id, False))
    return None

def insert_product_field_value(product_id: int, field_id: int, option_id: int):
    loader.execute(insert_pfv, params=(product_id, field_id, option_id))

