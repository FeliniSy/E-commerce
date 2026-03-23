from pipeline.loader.loader import loader
from db_manager.queries import insert_supplier, insert_external_supplier
from utils.logger import logger


def setup_sportlines_supplier():

    supplier_name = "Sportlines"
    supplier_type = "external"
    website_url = "https://sportlines.ge"
    contact_phone = "568 427 427"
    contact_email = None

    logger.info(f"Setting up supplier: {supplier_name}")

    try:
        loader.execute(insert_supplier, (supplier_name, supplier_type))
        logger.info(f"Supplier '{supplier_name}' inserted/updated")

        query = "SELECT id FROM suppliers WHERE name = %s"
        result = loader.fetch(query, (supplier_name,))

        if not result or len(result) == 0:
            logger.error(f"Failed to retrieve supplier ID for '{supplier_name}'")
            return

        supplier_id = result[0][0]
        logger.info(f"Supplier ID: {supplier_id}")

        loader.execute(
            insert_external_supplier,
            (supplier_id, website_url, contact_phone, contact_email)
        )
        logger.info(f"External supplier details inserted for '{supplier_name}'")

        logger.info("Sportlines supplier setup completed successfully!")

    except Exception as e:
        logger.error(f"Failed to setup Sportlines supplier: {e}", exc_info=True)


if __name__ == "__main__":
    setup_sportlines_supplier()
