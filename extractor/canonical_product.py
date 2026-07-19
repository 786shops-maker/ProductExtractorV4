"""
Canonical Product Model
ProductExtractorV4

Every website is converted into this structure before output generation.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class CanonicalProduct:

    # -----------------------------
    # Basic Information
    # -----------------------------
    title: str = ""
    brand: str = ""
    sku: str = ""

    # -----------------------------
    # Pricing
    # -----------------------------
    price: str = ""
    sale_price: str = ""
    currency: str = ""

    # -----------------------------
    # Product
    # -----------------------------
    category: str = ""
    subcategory: str = ""
    collection: str = ""

    stitched: str = ""
    pieces: str = ""
    occasion: str = ""

    # -----------------------------
    # Colours
    # -----------------------------
    color: str = ""
    colors: List[str] = field(default_factory=list)

    # -----------------------------
    # Fabrics
    # -----------------------------
    fabric: str = ""

    shirt_fabric: str = ""
    trouser_fabric: str = ""
    dupatta_fabric: str = ""
    lining_fabric: str = ""

    # -----------------------------
    # Embroidery
    # -----------------------------
    embroidery_types: List[str] = field(default_factory=list)

    neckline_work: List[str] = field(default_factory=list)
    front_work: List[str] = field(default_factory=list)
    back_work: List[str] = field(default_factory=list)
    sleeve_work: List[str] = field(default_factory=list)
    border_work: List[str] = field(default_factory=list)
    dupatta_work: List[str] = field(default_factory=list)
    trouser_work: List[str] = field(default_factory=list)

    # -----------------------------
    # Components
    # -----------------------------
    package: List[str] = field(default_factory=list)

    # -----------------------------
    # Description
    # -----------------------------
    short_description: str = ""
    long_description: str = ""

    # -----------------------------
    # SEO
    # -----------------------------
    seo_keywords: List[str] = field(default_factory=list)

    # -----------------------------
    # Raw
    # -----------------------------
    raw_description: str = ""
    cleaned_description: str = ""

    metadata: Dict = field(default_factory=dict)
