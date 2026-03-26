from db_manager.queries import insert_product_image
from pipeline.loader.loader import loader


def parse_biblusi_images(book_data: dict, product_id: int) -> None:
    pictures = book_data.get("pictures", [])

    if not pictures:
        return

    batch = [(product_id, url) for url in pictures if url]

    if batch:
        loader.execute_many(insert_product_image, batch)
