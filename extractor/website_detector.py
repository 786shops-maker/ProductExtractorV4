"""
website_detector.py

Detects the e-commerce platform used by a website.
"""

from urllib.parse import urlparse


class WebsiteDetector:

    def detect(self, url: str, html: str = "") -> str:

        html = html.lower()

        domain = urlparse(url).netloc.lower()

        # --------------------------
        # Shopify
        # --------------------------

        if (
            "cdn.shopify.com" in html
            or "shopify.theme" in html
            or "shopify-payment-button" in html
            or "shopify-section" in html
            or "/products/" in url
        ):
            return "shopify"

        # --------------------------
        # WooCommerce
        # --------------------------

        if (
            "woocommerce" in html
            or "wc-product" in html
            or "woocommerce-product" in html
            or "add-to-cart=" in html
        ):
            return "woocommerce"

        # --------------------------
        # Magento
        # --------------------------

        if (
            "mage/" in html
            or "magento" in html
            or "catalog/product" in html
        ):
            return "magento"

        # --------------------------
        # Salesforce Commerce Cloud
        # --------------------------

        if (
            "demandware" in html
            or "salesforce commerce cloud" in html
            or "__sfcc" in html
        ):
            return "salesforce"

        # --------------------------
        # BigCommerce
        # --------------------------

        if (
            "cdn.bc0a.com" in html
            or "bigcommerce" in html
        ):
            return "bigcommerce"

        # --------------------------
        # Wix
        # --------------------------

        if (
            "wixstatic" in html
            or "wix.com" in html
        ):
            return "wix"

        # --------------------------
        # Squarespace
        # --------------------------

        if (
            "squarespace" in html
            or "static.squarespace.com" in html
        ):
            return "squarespace"

        # --------------------------
        # Classic ASP
        # --------------------------

        if (
            ".asp" in url
            or ".asp?" in url
        ):
            return "classic_asp"

        # --------------------------
        # Custom PHP
        # --------------------------

        if (
            ".php" in url
            or ".php?" in url
        ):
            return "custom_php"

        # --------------------------
        # WordPress
        # --------------------------

        if (
            "wp-content" in html
            or "wp-includes" in html
        ):
            return "wordpress"

        # --------------------------
        # Generic
        # --------------------------

        return "generic"

    # -------------------------------------------------

    def is_shopify(self, url, html):

        return self.detect(url, html) == "shopify"

    # -------------------------------------------------

    def is_woocommerce(self, url, html):

        return self.detect(url, html) == "woocommerce"

    # -------------------------------------------------

    def is_magento(self, url, html):

        return self.detect(url, html) == "magento"

    # -------------------------------------------------

    def is_generic(self, url, html):

        return self.detect(url, html) == "generic"