"""
product_id.py

Production Product ID / SKU extractor for ProductExtractor V4.

Features
--------
* JSON-LD SKU detection
* Product JSON detection
* Meta tag detection
* HTML table detection
* Visible text detection
* URL fallback
* Candidate scoring
* SKU normalization
* Brand prefix generation
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("ProductExtractor")


# ---------------------------------------------------------
# Candidate
# ---------------------------------------------------------

@dataclass(order=True)
class SKUCandidate:
    score: int
    sku: str
    source: str


# ---------------------------------------------------------
# Extractor
# ---------------------------------------------------------

class ProductIDExtractor:

    # labels found on Pakistani fashion websites
    SKU_LABELS = (

        "sku",

        "product id",

        "product code",

        "style",

        "style no",

        "style number",

        "style code",

        "design code",

        "design no",

        "article",

        "article no",

        "article code",

        "reference",

        "reference no",

        "item code",

        "item no",

        "product number",

        "code"

    )

    # characters converted into '-'
    NORMALIZE_CHARS = r"[\/\\._\s]+"

    # reject pure numbers
    NUMERIC_ONLY = re.compile(r"^\d+$")

    def __init__(self):

        self.candidates: List[SKUCandidate] = []

        # generic sku patterns

        self.regex_patterns = [

            re.compile(r"\b[A-Za-z]{1,5}[-_/.\s]?\d{2,8}[A-Za-z]?\b"),

            re.compile(r"\b[A-Za-z]{1,5}(?:[-_/.\s][A-Za-z0-9]{1,8}){1,8}\b"),

            re.compile(
                r"\b(?:SKU|STYLE\s*NO|STYLE\s*CODE|PRODUCT\s*CODE|ARTICLE|DESIGN\s*NO|REFERENCE)\s*[:#-]?\s*([A-Za-z0-9/_\-. ]{3,60})",
                re.I,
            ),
        ]
            # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _normalize_sku(self, sku: str) -> str:
        """
        Normalize SKU to our standard format.

        Examples

        AJ_24_108   -> aj-24-108
        AJ/24/108   -> aj-24-108
        AJ 24 108   -> aj-24-108
        AJ.24.108   -> aj-24-108
        """

        if not sku:
            return ""

        sku = sku.strip()

        sku = re.sub(self.NORMALIZE_CHARS, "-", sku)

        sku = re.sub(r"-+", "-", sku)

        sku = sku.strip("-")

        return sku.lower()


    def _brand_slug(self, brand: str) -> str:
        """
        Gul Ahmed -> gulahmed
        Maria B -> mariab
        Sana Safinaz -> sanasafinaz
        """

        if not brand:
            return ""

        brand = brand.lower()

        brand = re.sub(r"[^a-z0-9]+", "", brand)

        return brand


    def _make_product_id(self, brand: str, sku: str) -> str:
        """
        Create final ProductID

        gulahmed-w-fb-sb-26-456904
        """

        sku = self._normalize_sku(sku)

        brand_slug = self._brand_slug(brand)

        if not sku:
            return ""

        # avoid duplicate brand prefix

        if brand_slug and sku.startswith(brand_slug + "-"):
            return sku

        if brand_slug:
            return f"{brand_slug}-{sku}"

        return sku


    def _is_valid_sku(self, sku: str) -> bool:

        if not sku:
            return False

        sku = sku.strip()

        if len(sku) < 3:
            return False

        if self.NUMERIC_ONLY.match(sku):
            return False

        # must contain at least one letter
        if not re.search(r"[A-Za-z]", sku):
            return False

        # reject obvious non-skus

        reject = {

            "sale",

            "new",

            "summer",

            "winter",

            "lawn",

            "cotton",

            "chiffon",

            "organza",

            "silk",

            "green",

            "blue",

            "red",

            "pink",

            "black",

            "white",

            "cream",

            "beige",

            "small",

            "medium",

            "large",

            "xl",

            "xxl",

            "pkr"

        }

        if sku.lower() in reject:
            return False

        return True


    def _add_candidate(self, sku: str, score: int, source: str):

        if not sku:
            return

        sku = sku.strip()

        if not self._is_valid_sku(sku):
            return

        sku = self._normalize_sku(sku)

        for existing in self.candidates:

            if existing.sku == sku:

                if score > existing.score:
                    existing.score = score
                    existing.source = source

                return

        self.candidates.append(

            SKUCandidate(

                score=score,

                sku=sku,

                source=source

            )

        )


    def _best_candidate(self) -> Optional[SKUCandidate]:

        if not self.candidates:
            return None

        self.candidates.sort(reverse=True)

        return self.candidates[0]

    # ---------------------------------------------------------
    # JSON-LD
    # ---------------------------------------------------------

    def _extract_from_json_ld(self, html: str):

        patterns = [

            r'"sku"\s*:\s*"([^"]+)"',

            r'"productID"\s*:\s*"([^"]+)"',

            r'"productId"\s*:\s*"([^"]+)"',

            r'"mpn"\s*:\s*"([^"]+)"'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I):

                self._add_candidate(

                    match.group(1),

                    100,

                    "json_ld"

                )


    # ---------------------------------------------------------
    # Embedded Product JSON
    # ---------------------------------------------------------

    def _extract_from_product_json(self, html: str):

        patterns = [

            r'"sku"\s*:\s*"([^"]+)"',

            r'"product_code"\s*:\s*"([^"]+)"',

            r'"style"\s*:\s*"([^"]+)"',

            r'"style_no"\s*:\s*"([^"]+)"',

            r'"style_number"\s*:\s*"([^"]+)"'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I):

                self._add_candidate(

                    match.group(1),

                    98,

                    "product_json"

                )


    # ---------------------------------------------------------
    # Meta Tags
    # ---------------------------------------------------------

    def _extract_from_meta(self, html: str):

        patterns = [

            r'itemprop=["\']sku["\'][^>]*content=["\']([^"\']+)',

            r'property=["\']product:sku["\'][^>]*content=["\']([^"\']+)',

            r'name=["\']sku["\'][^>]*content=["\']([^"\']+)'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I):

                self._add_candidate(

                    match.group(1),

                    95,

                    "meta"

                )

    # ---------------------------------------------------------
    # HTML Specification Tables
    # ---------------------------------------------------------

    def _extract_from_tables(self, html: str):

        for label in self.SKU_LABELS:

            pattern = rf"{label}\s*</[^>]+>\s*<[^>]+>\s*([^<]+)"

            for match in re.finditer(pattern, html, re.I):

                self._add_candidate(

                    match.group(1),

                    92,

                    "table"

                )

    # ---------------------------------------------------------
    # Visible Text
    # ---------------------------------------------------------

    def _extract_from_visible_text(self, html: str):

        text = re.sub(r"<[^>]+>", " ", html)

        text = re.sub(r"\s+", " ", text)

        for label in self.SKU_LABELS:

            pattern = rf"{label}\s*[:#-]?\s*([A-Za-z0-9/_\-. ]{{3,60}})"

            for match in re.finditer(pattern, text, re.I):

                self._add_candidate(

                    match.group(1),

                    90,

                    "text"

                )

        # Generic SKU regexes

        for regex in self.regex_patterns:

            for match in regex.finditer(text):

                value = match.group(1) if match.lastindex else match.group(0)

                self._add_candidate(

                    value,

                    70,

                    "regex"

                )

    # ---------------------------------------------------------
    # URL
    # ---------------------------------------------------------

    def _extract_from_url(self, url: str):

        if not url:

            return

        parsed = urlparse(url)

        slug = parsed.path.strip("/").split("/")[-1]

        slug = slug.split("?")[0]

        if len(slug) < 2:

            return

        self._add_candidate(

            slug,

            60,

            "url"

        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clear(self):

        self.candidates.clear()


    def extract(
        self,
        html: str,
        url: str = "",
        brand: str = ""
    ) -> dict:
        """
        Returns

        {
            "sku": "w-fb-sb-26-456904",
            "product_id": "gulahmed-w-fb-sb-26-456904",
            "confidence": 100,
            "source": "json_ld"
        }
        """

        self.clear()

        if html:

            self._extract_from_json_ld(html)

            self._extract_from_product_json(html)

            self._extract_from_meta(html)

            self._extract_from_tables(html)

            self._extract_from_visible_text(html)

        if url:

            self._extract_from_url(url)

        best = self._best_candidate()

        if best is None:

            logger.warning("No SKU detected.")

            return {

                "sku": "",

                "product_id": "",

                "confidence": 0,

                "source": ""

            }

        product_id = self._make_product_id(

            brand,

            best.sku

        )

        logger.info(

            "SKU=%s Source=%s Score=%s",

            best.sku,

            best.source,

            best.score

        )

        return {

            "sku": best.sku,

            "product_id": product_id,

            "confidence": best.score,

            "source": best.source

        }


# ---------------------------------------------------------
# Convenience Function
# ---------------------------------------------------------

_default_extractor = ProductIDExtractor()


def extract_product_id(
    html: str,
    url: str = "",
    brand: str = ""
):

    return _default_extractor.extract(

        html=html,

        url=url,

        brand=brand

    )
