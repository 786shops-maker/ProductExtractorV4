"""
Universal Title Parser
"""

from bs4 import BeautifulSoup

class TitleParser:
    """Extract product title using common ecommerce patterns."""

    SELECTORS = [
        "h1.product-title",
        "h1.product__title",
        "h1.product-title__text",
        "h1.entry-title",
        "h1.product_name",
        "h1",
    ]

    def parse(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        for selector in self.SELECTORS:
            node = soup.select_one(selector)
            if node:
                text = node.get_text(" ", strip=True)
                if text:
                    return text

        if soup.title:
            return soup.title.get_text(" ", strip=True)

        return ""
