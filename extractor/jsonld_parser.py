"""
Production JSON-LD parser.

Supports

- Shopify
- WooCommerce
- Magento
- Custom schema.org Product

Extracts

- title
- description
- brand
- sku
- price
- currency
- images
- url
- color
- material
- category

"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from extractor.models import Product


logger = logging.getLogger(__name__)


class JsonLDParser:

    def parse(self, html: str) -> Product:

        product = Product()

        if not html:
            return product

        soup = BeautifulSoup(html, "html.parser")

        scripts = soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        )

        product_nodes: List[Dict[str, Any]] = []

        for script in scripts:

            text = script.string or script.get_text()

            if not text:
                continue

            try:
                data = json.loads(text)

            except Exception:
                continue

            self._collect_products(
                data,
                product_nodes,
            )

        if not product_nodes:
            return product

        self._merge_products(
            product,
            product_nodes,
        )

        return product

    # ---------------------------------------------------------

    def _collect_products(
        self,
        node: Any,
        output: List[Dict[str, Any]],
    ) -> None:

        if isinstance(node, list):

            for item in node:
                self._collect_products(
                    item,
                    output,
                )

            return

        if not isinstance(node, dict):
            return

        if "@graph" in node:

            self._collect_products(
                node["@graph"],
                output,
            )

        node_type = node.get("@type", "")

        if isinstance(node_type, list):

            if "Product" in node_type:
                output.append(node)

        elif node_type == "Product":

            output.append(node)

        for value in node.values():

            if isinstance(value, (dict, list)):
                self._collect_products(
                    value,
                    output,
                )

    # ---------------------------------------------------------

    def _merge_products(
        self,
        product: Product,
        nodes: List[Dict[str, Any]],
    ) -> None:

        for node in nodes:

            self._merge_single(
                product,
                node,
            )

    # ---------------------------------------------------------

    def _merge_single(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        product.title = (
            product.title
            or node.get("name", "")
        )

        product.description = (
            product.description
            or node.get("description", "")
        )

        product.sku = (
            product.sku
            or node.get("sku", "")
        )

        product.url = (
            getattr(product, "url", "")
            or node.get("url", "")
        )

        product.category = (
            getattr(product, "category", "")
            or node.get("category", "")
        )

        self._parse_brand(
            product,
            node,
        )

        self._parse_images(
            product,
            node,
        )

        self._parse_offers(
            product,
            node,
        )

    # ---------------------------------------------------------

    def _parse_brand(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        if getattr(product, "brand", ""):
            return

        brand = node.get("brand")

        if isinstance(brand, dict):

            product.brand = (
                brand.get("name")
                or brand.get("@id")
                or ""
            )

        elif isinstance(brand, str):

            product.brand = brand

    # ---------------------------------------------------------

    def _parse_images(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        images = node.get("image")

        if not images:
            return

        if isinstance(images, str):

            images = [images]

        elif isinstance(images, dict):

            url = (
                images.get("url")
                or images.get("contentUrl")
            )

            images = [url] if url else []

        normalized = []

        for img in images:

            if not img:
                continue

            if img not in normalized:
                normalized.append(img)

        if hasattr(product, "images"):

            existing = getattr(product, "images", [])

            for img in normalized:

                if img not in existing:
                    existing.append(img)

            product.images = existing

    # ---------------------------------------------------------

    def _parse_offers(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        offers = node.get("offers")

        if not offers:
            return

        if isinstance(offers, list):

            for offer in offers:

                self._parse_offer(
                    product,
                    offer,
                )

            return

        if isinstance(offers, dict):

            offer_type = offers.get("@type", "")

            if offer_type == "AggregateOffer":

                low = offers.get("lowPrice")
                high = offers.get("highPrice")

                if not getattr(product, "price", ""):
                    product.price = low or high or ""

                currency = offers.get("priceCurrency")

                if hasattr(product, "currency"):

                    product.currency = (
                        getattr(product, "currency", "")
                        or currency
                    )

                return

            self._parse_offer(
                product,
                offers,
            )

    # ---------------------------------------------------------

    def _parse_offer(
        self,
        product: Product,
        offer: Dict[str, Any],
    ) -> None:

        if not getattr(product, "price", ""):

            product.price = (
                offer.get("price")
                or ""
            )

        if hasattr(product, "currency"):

            product.currency = (
                getattr(product, "currency", "")
                or offer.get("priceCurrency", "")
            )

        availability = offer.get("availability")

        if hasattr(product, "availability"):

            product.availability = (
                getattr(product, "availability", "")
                or availability
            )

        url = offer.get("url")

        if url and not getattr(product, "url", ""):

            product.url = url

    # ---------------------------------------------------------

    def extract_additional_fields(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        #
        # Color
        #

        if hasattr(product, "color"):

            product.color = (
                getattr(product, "color", "")
                or node.get("color", "")
            )

        #
        # Material
        #

        if hasattr(product, "material"):

            product.material = (
                getattr(product, "material", "")
                or node.get("material", "")
            )

        #
        # MPN
        #

        if hasattr(product, "mpn"):

            product.mpn = (
                getattr(product, "mpn", "")
                or node.get("mpn", "")
            )

        #
        # GTIN
        #

        for key in (

            "gtin",

            "gtin8",

            "gtin12",

            "gtin13",

            "gtin14",

        ):

            if hasattr(product, "gtin"):

                if not getattr(product, "gtin", ""):

                    value = node.get(key)

                    if value:

                        product.gtin = value
                        break

        #
        # Product ID
        #

        if hasattr(product, "product_id"):

            product.product_id = (

                getattr(product, "product_id", "")

                or node.get("productID", "")

            )

        #
        # additionalProperty
        #

        props = node.get(
            "additionalProperty"
        )

        if isinstance(props, list):

            for prop in props:

                if not isinstance(prop, dict):
                    continue

                name = str(
                    prop.get("name", "")
                ).lower()

                value = prop.get(
                    "value"
                )

                if not value:
                    continue

                if name == "color":

                    if hasattr(product, "color"):

                        if not product.color:

                            product.color = value

                elif name == "material":

                    if hasattr(product, "material"):

                        if not product.material:

                            product.material = value

                elif name in (

                    "fabric",

                    "fabric type",

                ):

                    if hasattr(product, "material"):

                        if not product.material:

                            product.material = value

    # ---------------------------------------------------------

    def _merge_single(
        self,
        product: Product,
        node: Dict[str, Any],
    ) -> None:

        product.title = (
            product.title
            or node.get("name", "")
        )

        product.description = (
            product.description
            or node.get("description", "")
        )

        product.sku = (
            product.sku
            or node.get("sku", "")
        )

        product.url = (
            getattr(product, "url", "")
            or node.get("url", "")
        )

        product.category = (
            getattr(product, "category", "")
            or node.get("category", "")
        )

        self._parse_brand(product, node)
        self._parse_images(product, node)
        self._parse_offers(product, node)
        self.extract_additional_fields(product, node)
