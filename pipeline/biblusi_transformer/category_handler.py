import json
import os
from utils.logger import logger


_category_id_mapping = {}


def load_category_mapping():
    global _category_id_mapping

    if _category_id_mapping:
        return

    mapping_file = 'biblusi_category_mapping.json'
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            str_mapping = json.load(f)
            _category_id_mapping = {int(k): v for k, v in str_mapping.items()}
        logger.info(f"Loaded category mapping with {len(_category_id_mapping)} entries")
    else:
        logger.warning(f"Category mapping file not found: {mapping_file}")


def get_biblusi_category_id(api_category_id: int) -> int:
    if not _category_id_mapping:
        load_category_mapping()

    if api_category_id in _category_id_mapping:
        return _category_id_mapping[api_category_id]
    else:
        logger.warning(f"API category ID {api_category_id} not found in mapping")
        return api_category_id
