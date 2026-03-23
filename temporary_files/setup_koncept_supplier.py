from db_manager.queries import insert_supplier, insert_external_supplier, insert_category
from pipeline.loader.loader import loader
from utils.logger import logger


def setup_koncept():
    try:
        logger.info("Creating Koncept supplier...")
        loader.execute(
            insert_supplier,
            params=("Koncept", "external")
        )

        loader.execute(
            insert_external_supplier,
            params=(2, "https://koncept.ge", "+995 XXX XXX XXX", "info@koncept.ge")
        )

        logger.info("✓ Koncept supplier created (id=2)")

        logger.info("Creating Furniture parent category...")
        loader.execute(
            insert_category,
            params=("Furniture", None, "furniture", None)
        )

        logger.info("✓ Furniture category created (id=2)")
        logger.info("Setup complete!")

    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)


if __name__ == "__main__":
    setup_koncept()
