from pipeline.loader.loader import loader
from db_manager.queries import (
    select_field_group, insert_field_group,
    select_field, insert_field,
    select_option, insert_option,
    insert_pfv,
    select_category_field, insert_category_field
)
from utils.logger import logger


def parse_sportlines_specifications(product_data: dict, product_id: int, category_id: int):

    attributes = product_data.get("attributes", [])

    if not attributes:
        logger.debug(f"No attributes found for product {product_id}")
        return

    field_group_name = "ზოგადი მახასიათებლები"

    result = loader.fetch(select_field_group, (field_group_name,))
    if result and len(result) > 0:
        field_group_id = result[0][0]
    else:
        loader.execute(insert_field_group, (field_group_name,))
        result = loader.fetch(select_field_group, (field_group_name,))
        field_group_id = result[0][0] if result else None

    if not field_group_id:
        logger.error(f"Failed to create field group: {field_group_name}")
        return

    for attr in attributes:
        attr_name = attr.get("name")
        terms = attr.get("terms", [])

        if not attr_name or not terms:
            continue

        result = loader.fetch(select_field, (attr_name, field_group_id))
        if result and len(result) > 0:
            field_id = result[0][0]
        else:
            loader.execute(insert_field, (attr_name, field_group_id))
            result = loader.fetch(select_field, (attr_name, field_group_id))
            field_id = result[0][0] if result else None

        if not field_id:
            logger.error(f"Failed to create field: {attr_name}")
            continue

        for term in terms:
            term_name = term.get("name")
            if not term_name:
                continue

            result = loader.fetch(select_option, (field_id, term_name))
            if result and len(result) > 0:
                option_id = result[0][0]
            else:
                loader.execute(insert_option, (field_id, term_name))
                result = loader.fetch(select_option, (field_id, term_name))
                option_id = result[0][0] if result else None

            if not option_id:
                logger.error(f"Failed to create option: {term_name} for field {attr_name}")
                continue

            result = loader.fetch(select_category_field, (category_id, field_id, option_id))
            if not result or len(result) == 0:
                loader.execute(insert_category_field, (category_id, field_id, option_id, False))

            try:
                loader.execute(insert_pfv, (product_id, field_id, option_id))
                logger.debug(f"Product {product_id}: {attr_name} = {term_name}")
            except Exception as e:
                logger.error(f"Failed to insert product field value: {e}")

    logger.debug(f"Inserted {len(attributes)} attributes for product {product_id}")
