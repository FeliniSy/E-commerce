import importlib
from typing import Callable, Any
from config.sources import SourceConfig
from utils.logger import logger


class SourceFactory:
    """Factory to dynamically load source-specific modules and functions"""

    @staticmethod
    def get_process_function(config: SourceConfig) -> Callable:
        """Dynamically import and return the main process function for a source"""
        try:
            module = importlib.import_module(config.process_module)
            function = getattr(module, config.process_function)
            logger.info(f"Loaded process function: {config.process_module}.{config.process_function}")
            return function
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Failed to load process function for {config.name}: "
                f"{config.process_module}.{config.process_function} - {e}"
            )

    @staticmethod
    def get_transformer_function(config: SourceConfig, function_path: str) -> Callable:
        """
        Dynamically import transformer function
        function_path example: 'data_parser.parse_data'
        """
        try:
            full_module_path = f"{config.transformer_module}.{function_path.rsplit('.', 1)[0]}"
            function_name = function_path.rsplit('.', 1)[1]

            module = importlib.import_module(full_module_path)
            function = getattr(module, function_name)
            logger.info(f"Loaded transformer: {full_module_path}.{function_name}")
            return function
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Failed to load transformer for {config.name}: "
                f"{full_module_path}.{function_name} - {e}"
            )

    @staticmethod
    def get_data_parser(config: SourceConfig) -> Callable:
        """Get data parser function"""
        return SourceFactory.get_transformer_function(config, config.data_parser_function)

    @staticmethod
    def get_spec_handler(config: SourceConfig) -> Callable:
        """Get specification handler function"""
        return SourceFactory.get_transformer_function(config, config.spec_handler_function)

    @staticmethod
    def get_image_handler(config: SourceConfig) -> Callable:
        """Get image handler function"""
        if config.image_handler_function.startswith('loader.'):
            # Special case for shared loader functions
            module_path = config.image_handler_function.rsplit('.', 1)[0].replace('loader.', 'pipeline.loader.')
            function_name = config.image_handler_function.rsplit('.', 1)[1]
            module = importlib.import_module(module_path)
            return getattr(module, function_name)
        else:
            return SourceFactory.get_transformer_function(config, config.image_handler_function)

    @staticmethod
    def get_additional_handlers(config: SourceConfig) -> dict:
        """Get any additional handlers (like brand_handler, address_handler for Alta)"""
        handlers = {}

        if config.extra_config.get('has_brand_handler'):
            try:
                module = importlib.import_module(f"{config.transformer_module}.brand_handler")
                handlers['brand_handler'] = module
                logger.info(f"Loaded brand handler for {config.name}")
            except ImportError:
                logger.warning(f"Brand handler not found for {config.name}")

        if config.extra_config.get('has_address_handler'):
            try:
                module = importlib.import_module(f"{config.transformer_module}.address_handler")
                handlers['address_handler'] = module
                logger.info(f"Loaded address handler for {config.name}")
            except ImportError:
                logger.warning(f"Address handler not found for {config.name}")

        return handlers

    @staticmethod
    def get_helper_functions(config: SourceConfig) -> dict:
        """Get helper functions specific to a source's scraping type"""
        helpers = {}

        if config.scraping_type == 'collection':
            try:
                module = importlib.import_module(config.process_module)
                helpers['fetch_collections'] = getattr(module, 'fetch_and_register_collections')
                logger.info(f"Loaded collection fetcher for {config.name}")
            except (ImportError, AttributeError):
                logger.warning(f"Collection fetcher not found for {config.name}")

        elif config.scraping_type == 'id_based':
            try:
                from utils.biblusi_id_fetcher import fetch_all_biblusi_ids
                helpers['fetch_ids'] = fetch_all_biblusi_ids
                logger.info(f"Loaded ID fetcher for {config.name}")
            except ImportError:
                logger.warning(f"ID fetcher not found for {config.name}")

        return helpers
