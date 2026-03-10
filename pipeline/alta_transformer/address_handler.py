from db_manager.queries import insert_product_address
from pipeline.loader.loader import loader


def parse_addresses(product_data: dict, product_id: int):
    stores = product_data.get("availabilityInStores", [])
    batch = [
        (product_id, s["branchName"], "Georgia", s["city"], s["address"], s["phoneNumber"])
        for s in stores if s.get("inStock")
    ]
    if batch:
        loader.execute_many(insert_product_address, batch)