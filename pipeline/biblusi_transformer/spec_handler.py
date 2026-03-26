from db_manager.queries import (
    select_field_group, insert_field_group,
    select_field, insert_field,
    select_option, insert_option,
    select_category_field, insert_category_field,
    insert_pfv
)
from pipeline.loader.loader import loader
from utils.logger import logger


def parse_biblusi_specifications(book_data: dict, db_product_id: int, category_id: int) -> None:

    try:
        pfv_batch = []
        group_name = "Book Specifications"
        group_id = get_or_create_field_group(group_name)

        variations = book_data.get("variations", [])
        if variations:
            first_variation = variations[0]
            specs = first_variation.get("specs", [])

            for spec in specs:
                value = spec.get("value", "")
                element = spec.get("element", {})
                label = element.get("label", "")

                if not label or not value or value.lower() == "null" or value.strip() == "":
                    continue

                field_id = get_or_create_field(label, group_id)
                option_id = get_or_create_option(str(value), field_id)
                get_or_create_category_field(category_id, field_id, option_id)
                pfv_batch.append((db_product_id, field_id, option_id))

        is_new = book_data.get("is_new", 0)
        if is_new:
            field_id = get_or_create_field("ახალია", group_id)
            option_id = get_or_create_option("კი", field_id)
            get_or_create_category_field(category_id, field_id, option_id)
            pfv_batch.append((db_product_id, field_id, option_id))

        is_bestseller = book_data.get("is_bestseller", 0)
        if is_bestseller:
            field_id = get_or_create_field("ბესტსელერი", group_id)
            option_id = get_or_create_option("კი", field_id)
            get_or_create_category_field(category_id, field_id, option_id)
            pfv_batch.append((db_product_id, field_id, option_id))

        if pfv_batch:
            loader.execute_many(insert_pfv, pfv_batch)

        logger.info(f"Book {db_product_id} — saved {len(pfv_batch)} specifications")

    except Exception as e:
        logger.error(f"Failed to parse specifications for book {db_product_id}: {e}", exc_info=True)


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
