"""
brand_detector.py

Production Brand Detector

Features
--------
* JSON-LD Brand
* Shopify Vendor
* WooCommerce
* Magento
* Breadcrumb
* Meta Tags
* Product Title
* Logo Alt
* Domain Detection
* Candidate Scoring
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("ProductExtractor")


@dataclass(order=True)
class BrandCandidate:
    score: int
    brand: str
    source: str


class BrandDetector:

    def __init__(self):

        self.candidates: List[BrandCandidate] = []

        self.brand_alias = {

            "asim jofa": "Asim Jofa",
            "azure": "Azure",
            "baroque": "Baroque",
            "bin saeed": "Bin Saeed",
            "charizma": "Charizma",
            "cross stitch": "Cross Stitch",
            "edenrobe": "Edenrobe",
            "elan": "Elan",
            "ethnic": "Ethnic",
            "faiza saqlain": "Faiza Saqlain",
            "gul ahmed": "Gul Ahmed",
            "ideas": "Gul Ahmed",
            "imrozia": "Imrozia",
            "iznik": "Iznik",
            "j.": "Junaid Jamshed",
            "jj": "Junaid Jamshed",
            "junaid jamshed": "Junaid Jamshed",
            "kanwal malik": "Kanwal Malik",
            "khaadi": "Khaadi",
            "limelight": "Limelight",
            "maria b": "Maria B",
            "mariab": "Maria B",
            "nishat linen": "Nishat Linen",
            "noor by saadia asad": "Noor by Saadia Asad",
            "qalamkar": "Qalamkar",
            "ramsha": "Ramsha",
            "rang rasiya": "Rang Rasiya",
            "sana safinaz": "Sana Safinaz",
            "sapphire": "Sapphire",
            "so kamal": "So Kamal",
            "zellbury": "Zellbury",
        }

        def clear(self):
        self.candidates.clear()

    def normalize(self, brand: str) -> str:

        if not brand:
            return ""

        brand = brand.strip()

        key = brand.lower()

        return self.brand_alias.get(key, brand.title())

    def brand_slug(self, brand: str) -> str:

        brand = brand.lower()

        brand = re.sub(r"[^a-z0-9]+", "", brand)

        return brand

    def add_candidate(self, brand, score, source):

        if not brand:
            return

        brand = self.normalize(brand)

        for c in self.candidates:

            if c.brand == brand:

                if score > c.score:
                    c.score = score
                    c.source = source

                return

        self.candidates.append(

            BrandCandidate(

                score,

                brand,

                source

            )

        )

    def best(self):

        if not self.candidates:
            return None

        self.candidates.sort(reverse=True)

        return self.candidates[0]
    
       # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def detect(self, html: str = "", url: str = "") -> dict:

        self.clear()

        if html:

            self._extract_from_jsonld(html)

            self._extract_from_product_json(html)

            self._extract_from_meta(html)

            self._extract_from_title(html)

            self._extract_from_logo(html)

        if url:

            self._extract_from_domain(url)

        best = self.best()

        if best is None:

            logger.warning("Brand not detected.")

            return {

                "brand": "",

                "brand_slug": "",

                "confidence": 0,

                "source": ""

            }

        logger.info(

            "Brand=%s Source=%s Score=%s",

            best.brand,

            best.source,

            best.score

        )

        return {

            "brand": best.brand,

            "brand_slug": self.brand_slug(best.brand),

            "confidence": best.score,

            "source": best.source

        }

    # ---------------------------------------------------------
    # JSON-LD
    # ---------------------------------------------------------

    def _extract_from_jsonld(self, html: str):

        patterns = [

            r'"brand"\s*:\s*\{\s*"@type"\s*:\s*"Brand"\s*,\s*"name"\s*:\s*"([^"]+)"',

            r'"brand"\s*:\s*"([^"]+)"'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I | re.S):

                self.add_candidate(

                    match.group(1),

                    100,

                    "json_ld"

                )


    # ---------------------------------------------------------
    # Product JSON
    # ---------------------------------------------------------

    def _extract_from_product_json(self, html: str):

        patterns = [

            r'"vendor"\s*:\s*"([^"]+)"',

            r'"manufacturer"\s*:\s*"([^"]+)"',

            r'"brand"\s*:\s*"([^"]+)"'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I):

                self.add_candidate(

                    match.group(1),

                    98,

                    "product_json"

                )


    # ---------------------------------------------------------
    # Meta Tags
    # ---------------------------------------------------------

    def _extract_from_meta(self, html: str):

        patterns = [

            r'property=["\']product:brand["\'][^>]*content=["\']([^"\']+)',

            r'name=["\']brand["\'][^>]*content=["\']([^"\']+)',

            r'name=["\']manufacturer["\'][^>]*content=["\']([^"\']+)'

        ]

        for pattern in patterns:

            for match in re.finditer(pattern, html, re.I):

                self.add_candidate(

                    match.group(1),

                    90,

                    "meta"

                )


    # ---------------------------------------------------------
    # HTML Title
    # ---------------------------------------------------------

    def _extract_from_title(self, html: str):

        m = re.search(

            r"<title>(.*?)</title>",

            html,

            re.I | re.S

        )

        if not m:
            return

        title = re.sub(r"\s+", " ", m.group(1))

        title_lower = title.lower()

        for alias, official in self.brand_alias.items():

            if alias in title_lower:

                self.add_candidate(

                    official,

                    85,

                    "title"

                )


    # ---------------------------------------------------------
    # Logo ALT
    # ---------------------------------------------------------

    def _extract_from_logo(self, html: str):

        for alias, official in self.brand_alias.items():

            pattern = rf'alt=["\'][^"\']*{re.escape(alias)}[^"\']*logo'

            if re.search(pattern, html, re.I):

                self.add_candidate(

                    official,

                    83,

                    "logo"

                )


    # ---------------------------------------------------------
    # Domain
    # ---------------------------------------------------------

    def _extract_from_domain(self, url: str):

        if not url:

            return

        domain = urlparse(url).netloc.lower()

        for alias, official in self.brand_alias.items():

            key = alias.replace(" ", "")

            if key in domain.replace("-", "").replace(".", ""):

                self.add_candidate(

                    official,

                    80,

                    "domain"

                )
_default_detector = BrandDetector()


def detect_brand(html="", url=""):

    return _default_detector.detect(

        html=html,

        url=url

    )

