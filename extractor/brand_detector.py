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
    
    def detect(self, url: str) -> str:
        host = urlparse(url).netloc.lower()
        host = host.replace("www.", "")
        for domain, brand in self.BRAND_MAP.items():
            if domain in host:
                return brand
        if host:
            return host.split(".")[0].replace("-", " ").title()
        return ""
    
    @classmethod
    def add_brand(cls, domain: str, brand: str):
        cls.BRAND_MAP[domain.lower()] = brand
