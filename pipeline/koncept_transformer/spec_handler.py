from db_manager.queries import (
    select_field_group, insert_field_group,
    select_field, insert_field,
    select_option, insert_option,
    select_category_field, insert_category_field,
    insert_pfv
)
from pipeline.loader.loader import loader
from utils.logger import logger


def parse_koncept_specifications(product_data: dict, db_product_id: int, category_id: int) -> None:

    try:
        pfv_batch = []
        group_name = "Koncept Product Info"
        group_id = get_or_create_field_group(group_name)

        product_type = product_data.get("product_type")
        if product_type:
            field_id = get_or_create_field("Product Type", group_id)
            option_id = get_or_create_option(product_type, field_id)
            get_or_create_category_field(category_id, field_id, option_id)
            pfv_batch.append((db_product_id, field_id, option_id))

        options = product_data.get("options", [])
        for option in options:
            option_name = option.get("name", "")
            option_values = option.get("values", [])
            if option_name and option_values and option_name != "Title":
                field_id = get_or_create_field(option_name, group_id)
                value_str = ", ".join(str(v) for v in option_values)
                option_id = get_or_create_option(value_str, field_id)
                get_or_create_category_field(category_id, field_id, option_id)
                pfv_batch.append((db_product_id, field_id, option_id))

        tags = product_data.get("tags", [])
        if tags:
            field_id = get_or_create_field("Tags", group_id)
            tags_str = ", ".join(tags)
            option_id = get_or_create_option(tags_str, field_id)
            get_or_create_category_field(category_id, field_id, option_id)
            pfv_batch.append((db_product_id, field_id, option_id))

        if pfv_batch:
            loader.execute_many(insert_pfv, pfv_batch)

        logger.info(f"Product {db_product_id} — saved {len(pfv_batch)} specifications")

    except Exception as e:
        logger.error(f"Failed to parse specifications for product {db_product_id}: {e}", exc_info=True)


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
