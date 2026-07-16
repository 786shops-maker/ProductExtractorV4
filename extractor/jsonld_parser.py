"""
jsonld_parser.py
Extract product information from JSON-LD blocks.
"""

import json
from extractor.models import Product


class JsonLDParser:

    def parse(self, html: str) -> Product:
        product = Product()

        start = 0
        while True:
            idx = html.find('application/ld+json', start)
            if idx == -1:
                break

            tag_start = html.rfind("<script", 0, idx)
            tag_end = html.find("</script>", idx)
            if tag_start == -1 or tag_end == -1:
                break

            block = html[html.find(">", tag_start)+1:tag_end].strip()

            try:
                data = json.loads(block)
            except Exception:
                start = tag_end + 9
                continue

            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                t = item.get("@type", "")
                if isinstance(t, list):
                    t = ",".join(t)

                if "Product" not in str(t):
                    continue

                product.title = item.get("name", "")
                product.description = item.get("description", "")
                product.sku = item.get("sku", "")

                brand = item.get("brand", "")
                if isinstance(brand, dict):
                    product.brand = brand.get("name", "")
                elif isinstance(brand, str):
                    product.brand = brand

                img = item.get("image", [])
                if isinstance(img, str):
                    product.image_urls = [img]
                elif isinstance(img, list):
                    product.image_urls = img

                offers = item.get("offers", {})
                if isinstance(offers, dict):
                    product.price = str(offers.get("price", ""))
                    product.currency = offers.get("priceCurrency", "")

                return product

            start = tag_end + 9

        return product
