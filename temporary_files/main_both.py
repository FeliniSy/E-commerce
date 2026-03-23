# import asyncio
# from datetime import datetime
#
# from main.alta_process import process_category as
# from main.koncept_process import fetch_and_register_collections, process_koncept_collection
# from pipeline.extractor.scrapper import close_browser
#
# from utils.logger import logger
#
#
# async def main():
#     try:
#         product_semaphore = asyncio.Semaphore(30)
#         category_semaphore = asyncio.Semaphore(10)
#
#         logger.info("=" * 50)
#         logger.info("STARTING ALTA PROCESSING")
#         logger.info("=" * 50)
#
#         async def process_alta_with_semaphore(category_id):
#             async with category_semaphore:
#                 await process_alta_category(category_id, product_semaphore)
#
#         await asyncio.gather(*[
#             process_alta_with_semaphore(i) for i in range(1, 295)
#         ])
#
#         logger.info("✓ Alta processing complete")
#
#         logger.info("=" * 50)
#         logger.info("STARTING KONCEPT PROCESSING")
#         logger.info("=" * 50)
#
#         collections = await fetch_and_register_collections()
#
#         collections_with_products = [
#             c for c in collections if c.get("products_count", 0) > 0
#         ]
#
#         logger.info(f"Processing {len(collections_with_products)} collections")
#
#         async def process_koncept_with_semaphore(collection):
#             async with category_semaphore:
#                 await process_koncept_collection(collection, product_semaphore)
#
#         await asyncio.gather(*[
#             process_koncept_with_semaphore(c) for c in collections_with_products
#         ])
#
#         logger.info("✓ Koncept processing complete")
#
#     except Exception as e:
#         logger.critical(f"Pipeline crashed: {e}", exc_info=True)
#     finally:
#         await close_browser()
#
#
# if __name__ == "__main__":
#     start = datetime.now()
#     print(f"Started at: {start}")
#     asyncio.run(main())
#     end = datetime.now()
#     print(f"Finished at: {end}")
#     print(f"Total time: {end - start}")
