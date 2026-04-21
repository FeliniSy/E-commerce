import asyncio
from config.sources import SourceConfig, get_source_config
from orchestrator.source_factory import SourceFactory
from utils.logger import logger
from pipeline.extractor.scrapper import close_browser


class PipelineRunner:
    """Unified orchestrator for running any source's scraping pipeline"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.config = get_source_config(source_name)
        self.factory = SourceFactory()

    async def run(self):
        """Main entry point - routes to appropriate scraping strategy"""
        logger.info(f"Starting pipeline for source: {self.source_name}")

        try:
            if self.config.scraping_type == 'category':
                await self._run_category_based()
            elif self.config.scraping_type == 'collection':
                await self._run_collection_based()
            elif self.config.scraping_type == 'id_based':
                await self._run_id_based()
            elif self.config.scraping_type == 'paginated':
                await self._run_paginated()
            else:
                raise ValueError(f"Unknown scraping type: {self.config.scraping_type}")

            logger.info(f"Completed pipeline for source: {self.source_name}")

        except Exception as e:
            logger.critical(f"Pipeline crashed for {self.source_name}: {e}", exc_info=True)
        finally:
            await close_browser()

    async def _run_category_based(self):
        """Run category-based scraping (Alta pattern)"""
        logger.info(f"Running category-based scraping for {self.source_name}")

        process_category = self.factory.get_process_function(self.config)

        # Clear brand cache if brand handler exists
        handlers = self.factory.get_additional_handlers(self.config)
        if 'brand_handler' in handlers:
            handlers['brand_handler'].clear_brand_cache()

        product_semaphore = asyncio.Semaphore(self.config.extra_config['product_semaphore'])
        category_semaphore = asyncio.Semaphore(self.config.extra_config['category_semaphore'])

        category_start, category_end = self.config.extra_config['category_range']

        async def process_category_with_semaphore(category_id):
            async with category_semaphore:
                await process_category(category_id, product_semaphore)

        await asyncio.gather(*[
            process_category_with_semaphore(i) for i in range(category_start, category_end)
        ])

    async def _run_collection_based(self):
        """Run collection-based scraping (Koncept pattern)"""
        logger.info(f"Running collection-based scraping for {self.source_name}")

        process_collection = self.factory.get_process_function(self.config)
        helpers = self.factory.get_helper_functions(self.config)

        product_semaphore = asyncio.Semaphore(self.config.extra_config['product_semaphore'])

        # Fetch and register collections
        fetch_collections = helpers.get('fetch_collections')
        if not fetch_collections:
            raise ValueError(f"Collection fetcher not found for {self.source_name}")

        collections = await fetch_collections()

        # Process each collection
        for collection in collections:
            if collection.get('products_count', 0) > 0:
                await process_collection(collection, product_semaphore)

    async def _run_id_based(self):
        """Run ID-based scraping (Biblusi pattern)"""
        logger.info(f"Running ID-based scraping for {self.source_name}")

        process_item = self.factory.get_process_function(self.config)
        helpers = self.factory.get_helper_functions(self.config)

        product_semaphore = asyncio.Semaphore(self.config.extra_config['product_semaphore'])

        # Fetch all IDs
        fetch_ids = helpers.get('fetch_ids')
        if not fetch_ids:
            raise ValueError(f"ID fetcher not found for {self.source_name}")

        all_ids = await fetch_ids()
        logger.info(f"Found {len(all_ids)} items to process for {self.source_name}")

        async def process_with_semaphore(item_id):
            async with product_semaphore:
                await process_item(item_id)

        await asyncio.gather(*[process_with_semaphore(item_id) for item_id in all_ids])

    async def _run_paginated(self):
        """Run paginated scraping (Sportlines pattern)"""
        logger.info(f"Running paginated scraping for {self.source_name}")

        # For sportlines, we need to use the run_sportlines_scraper function
        try:
            module = __import__(self.config.process_module, fromlist=['run_sportlines_scraper'])
            scraper_function = getattr(module, 'run_sportlines_scraper')

            max_pages = self.config.extra_config['max_pages']
            max_concurrent = self.config.extra_config['product_semaphore']

            await scraper_function(max_pages=max_pages, max_concurrent_products=max_concurrent)

        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load scraper for {self.source_name}: {e}")
            raise


async def run_pipeline(source_name: str):
    """Convenience function to run a pipeline for a source"""
    runner = PipelineRunner(source_name)
    await runner.run()


async def run_multiple_sources(source_names: list[str], sequential: bool = True):
    """Run pipelines for multiple sources"""
    if sequential:
        for source_name in source_names:
            logger.info(f"Starting source: {source_name}")
            await run_pipeline(source_name)
    else:
        # Run in parallel (each will have its own browser instance)
        await asyncio.gather(*[run_pipeline(source) for source in source_names])
