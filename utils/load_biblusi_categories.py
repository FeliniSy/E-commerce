import json
from pathlib import Path
from db_manager.queries import insert_category_with_id
from pipeline.loader.loader import loader
from utils.helper import slugify
from utils.logger import logger


def flatten_categories(categories, flattened=None):

    if flattened is None:
        flattened = []

    for category in categories:
        # Add current category
        flattened.append({
            'id': category['id'],
            'parent_id': category.get('parent_id'),
            'name': category['name'],
            'image': category.get('image')
        })

        children = category.get('children', [])
        if children:
            flatten_categories(children, flattened)

    return flattened


def load_biblusi_categories():

    logger.info("Loading biblus_cat.json...")

    try:
        project_root = Path(__file__).parent.parent
        json_file = project_root / 'biblus_cat.json'

        with open(json_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)

        logger.info(f"Loaded {len(categories_data)} root categories")

        flattened = flatten_categories(categories_data)
        logger.info(f"Flattened to {len(flattened)} total categories")


        category_mapping = {}
        inserted_count = 0
        failed_count = 0

        for cat in flattened:
            try:
                slug = f"{slugify(cat['name'])}-{cat['id']}"

                result = loader.fetch(
                    insert_category_with_id,
                    params=(
                        cat['id'],
                        cat['name'],
                        cat['parent_id'],
                        slug,
                        cat['image']
                    )
                )

                if result:
                    db_id = result[0][0]
                    category_mapping[cat['id']] = db_id
                    inserted_count += 1

                    if inserted_count % 50 == 0:
                        logger.info(f"Inserted {inserted_count}/{len(flattened)} categories")

            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to insert category {cat['id']} ({cat['name']}): {e}")

        logger.info(f"Successfully inserted {inserted_count} categories, failed: {failed_count}")

        mapping_file = project_root / 'biblusi_category_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(category_mapping, f, indent=2, ensure_ascii=False)

        logger.info(f"Category mapping saved to {mapping_file}")

        return category_mapping

    except FileNotFoundError:
        logger.error(f"biblus_cat.json not found at {json_file}!")
        raise
    except Exception as e:
        logger.error(f"Error loading categories: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("Starting Biblusi category loading...")
    mapping = load_biblusi_categories()
    logger.info(f"Done! Loaded {len(mapping)} categories")
