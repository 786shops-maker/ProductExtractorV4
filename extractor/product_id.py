"""
product_id.py
Extracts product IDs, SKUs, or style codes from URLs or HTML content.
"""
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger("ProductExtractor")

class ProductIDExtractor:
    def __init__(self):
        # Common SKU patterns
        self.sku_patterns = [
            r'\b[A-Z]{1,4}-\d{3,6}\b',          
            r'\b[A-Z]{1,2}-[A-Z]{2}-[A-Z]{2}-\d{2}-\d{4,6}\b', 
            r'\b(?:SKU|Style\s*Code|Product\s*Code|Article)\s*[:-]?\s*([A-Z0-9\-]{4,15})\b', 
            r'\bModel\s*[:-]?\s*([A-Z0-9\-]{4,15})\b'
        ]

    def extract(self, html: str, url: str = "") -> str:
        if url:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) > 0:
                slug = path_parts[-1]
                if re.search(r'\d', slug) or len(slug) < 20:
                    clean_slug = slug.split('?')[0]
                    logger.info(f"Extracted product ID from URL slug: {clean_slug}")
                    return clean_slug.upper()

        html_upper = html.upper()
        for pattern in self.sku_patterns:
            match = re.search(pattern, html_upper)
            if match:
                product_id = match.group(1) if match.lastindex else match.group(0)
                logger.info(f"Extracted product ID from HTML: {product_id}")
                return product_id.strip()

        logger.warning("Could not find a specific product ID, using 'UNKNOWN-ID'")
        return "UNKNOWN-ID"
