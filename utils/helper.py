import json
import re
import uuid

_CATEGORY_ICON_CACHE = None


def get_data_id(data: list) -> list:
    all_product = []
    for products in data:
        all_product.append(products["id"])

    return all_product


def slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^\w\-]', '', slug, flags=re.UNICODE)
    return slug or str(uuid.uuid4())[:8]


def get_json_for_icon():
    global _CATEGORY_ICON_CACHE
    if _CATEGORY_ICON_CACHE is None:
        with open("categories.json", "r") as f:
            data = json.loads(f.read())
        categories = data.get("categories", [])
        _CATEGORY_ICON_CACHE = {cat["name"]: cat["iconUrl"] for cat in categories}
    return _CATEGORY_ICON_CACHE


def get_images_url(name):
    icon_cache = get_json_for_icon()
    return icon_cache.get(name)


import io
import requests
import numpy as np
from PIL import Image
from utils.logger import logger


def png_to_svg(url):
    COLOR = "#3e5ad8"
    logger.info(f"Converting PNG to SVG mosaic: {url}")

    resp = requests.get(url)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")

    img.thumbnail((128, 128))
    px = np.array(img)
    h, w, _ = px.shape

    rects = []
    for y in range(h):
        for x in range(w):
            pr, pg, pb, a = px[y, x]
            if a > 10:
                brightness = (0.299 * pr + 0.587 * pg + 0.114 * pb) / 255
                op = round((a / 255) * (1 - brightness * 0.5), 2)
                if op > 0.05:
                    rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{COLOR}" opacity="{op}"/>')

    svg_content = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" shape-rendering="crispEdges">\n'
            + "".join(rects) +
            "\n</svg>"
    )

    return svg_content
