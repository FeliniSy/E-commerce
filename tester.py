import asyncio
import json
from pipeline.extractor.scrapper import page_scrapper


def extract_category(category, parent_id=None):
    result = {
        "id": category.get("id"),
        "parent_id": parent_id,
        "name": category.get("name"),
        "image": category.get("image"),
        "children": []
    }

    for child in category.get("children", []):
        result["children"].append(extract_category(child, parent_id=category.get("id")))

    return result


async def main():
    data = await page_scrapper("https://apiv1.biblusi.ge/api/category")
    categories = data.get("data", [])

    cleaned = [extract_category(cat) for cat in categories]

    with open("biblus_cat.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print("Done:", len(cleaned))


asyncio.run(main())