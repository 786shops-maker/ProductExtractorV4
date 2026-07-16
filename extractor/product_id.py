"""
product_id.py
Extracts product IDs, SKUs, or style codes.
Priority: 1. Page Meta/JSON-LD/Specific Elements -> 2. URL Slug -> 3. General HTML scan.
"""
import re
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger("ProductExtractor")

class ProductIDExtractor:
    def __init__(self):
        # Strict patterns for labeled SKUs (e.g., "SKU: EC43-26-YELLOW")
        self.labeled_sku_patterns = [
            r'(?:SKU|Style\s*Code|Product\s*Code|Article\s*No|Model)\s*[:\-]\s*([A-Z0-9\-]{4,20})',
        ]
        # General SKU patterns for absolute last resort
        self.general_sku_patterns = [
            r'\b([A-Z]{2,4}-\d{2,4}-\d{2}-[A-Z]+)\b',  # e.g., EC43-26-YELLOW
            r'\b([A-Z]{2,4}-\d{2,4}-[A-Z]+)\b',         # e.g., RTS-EC43-YELLOW
            r'\b([A-Z]{1,4}-\d{3,6})\b',                # e.g., PM-62005, BB-301
        ]

    def extract(self, html: str, url: str = "") -> str:
        soup = BeautifulSoup(html, "lxml")

        # ==========================================
        # PRIORITY 1: Look for SKU on the page (HTML)
        # ==========================================

        # 1.1 Check Meta Tags (Most reliable for e-commerce)
        meta_selectors = [
            {"property": "product:sku"},
            {"name": "product_id"},
            {"name": "sku"},
            {"itemprop": "sku"}
        ]
        for attrs in meta_selectors:
            meta = soup.find("meta", attrs=attrs)
            if meta and meta.get("content"):
                sku = meta["content"].strip().upper()
                if sku and len(sku) > 2:
                    logger.info(f"Extracted product ID from Meta tag: {sku}")
                    return sku

        # 1.2 Check JSON-LD (Hidden structured data)
        jsonld_match = re.search(r'"sku"\s*:\s*"([^"]{3,20})"', html, re.IGNORECASE)
        if jsonld_match:
            sku = jsonld_match.group(1).strip().upper()
            logger.info(f"Extracted product ID from JSON-LD: {sku}")
            return sku

        # 1.3 Check Specific HTML Elements (Classes/IDs where SKUs usually live)
        sku_selectors = [
            ".product-sku", ".sku", ".variant-sku", ".product__sku",
            "[data-variant-sku]", "[itemprop='sku']", ".pdp-product-sku"
        ]
        for sel in sku_selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True).upper()
                # Clean up any "SKU:" prefix if the element contains it
                text = re.sub(r'^(SKU|STYLE\s*CODE|PRODUCT\s*CODE)\s*[:\-]\s*', '', text)
                if text and len(text) > 2 and len(text) < 25:
                    logger.info(f"Extracted product ID from HTML element ({sel}): {text}")
                    return text

        # 1.4 Check Labeled Text Patterns (e.g., "SKU: XYZ-123")
        # We search the whole text but require a strict label prefix to avoid footer noise
        text = soup.get_text(" ", strip=True).upper()
        for pattern in self.labeled_sku_patterns:
            match = re.search(pattern, text)
            if match:
                sku = match.group(1).strip()
                if sku and len(sku) > 2:
                    logger.info(f"Extracted product ID from labeled text: {sku}")
                    return sku

        # ==========================================
        # PRIORITY 2: Look at URL Slug
        # ==========================================
        if url:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                slug = path_parts[-1].split('?')[0].upper()
                
                # Pattern 1: XXX-##-COLOR (e.g., EC43-26-YELLOW)
                match = re.search(r'([A-Z]{2,4}-\d{2,4}-\d{2}-[A-Z]+)', slug)
                if match:
                    logger.info(f"Extracted product ID from URL slug (Pattern 1): {match.group(1)}")
                    return match.group(1)
                
                # Pattern 2: XXX-##-XXX (e.g., RTS-EC43-YELLOW)
                match = re.search(r'([A-Z]{2,4}-\d{2,4}-[A-Z]+)', slug)
                if match:
                    logger.info(f"Extracted product ID from URL slug (Pattern 2): {match.group(1)}")
                    return match.group(1)
                
                # Pattern 3: General alphanumeric slug
                if re.search(r'\d', slug) and len(slug) < 40:
                    logger.info(f"Using full URL slug as product ID: {slug}")
                    return slug

        # ==========================================
        # PRIORITY 3: General HTML Fallback (Last resort)
        # ==========================================
        for pattern in self.general_sku_patterns:
            match = re.search(pattern, text)
            if match:
                sku = match.group(1) if match.lastindex else match.group(0)
                logger.info(f"Extracted product ID from general HTML scan: {sku}")
                return sku.strip()

        logger.warning("Could not find a specific product ID, using 'UNKNOWN-ID'")
        return "UNKNOWN-ID"