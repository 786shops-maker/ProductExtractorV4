"""
ProductExtractorV4
------------------

Production quality fashion description parser.

Purpose:
    Convert raw fashion product descriptions from Pakistani clothing
    websites into standardized structured descriptions.

Supported sources:
    - Shopify
    - WooCommerce
    - Magento
    - Classic ASP
    - Custom ecommerce systems

Design principles:
    - No site-specific rules
    - No brand-specific parsing
    - Prefer structured data first
    - Normalize fashion terminology
    - Remove marketing noise
    - Keep only useful production information

Output example:

Shirt:
Fabric: Lawn
Embroidery: Front, Back, Sleeves, Neckline

Trouser:
Fabric: Cambric

Dupatta:
Fabric: Chiffon
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterable, Any

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


# ============================================================
# Data Models
# ============================================================


@dataclass
class ComponentDescription:
    """
    Represents one clothing component.
    """

    name: str

    fabrics: List[str] = field(default_factory=list)

    colors: List[str] = field(default_factory=list)

    embroidery_locations: List[str] = field(default_factory=list)

    styles: List[str] = field(default_factory=list)


@dataclass
class ParsedDescription:
    """
    Complete normalized product description.
    """

    shirt: ComponentDescription = field(
        default_factory=lambda: ComponentDescription("Shirt")
    )

    trouser: ComponentDescription = field(
        default_factory=lambda: ComponentDescription("Trouser")
    )

    dupatta: ComponentDescription = field(
        default_factory=lambda: ComponentDescription("Dupatta")
    )

    raw_text: str = ""



# ============================================================
# Normalization Dictionaries
# ============================================================


FABRIC_MAP: Dict[str, str] = {

    # Lawn
    "lawn": "Lawn",
    "premium lawn": "Premium Lawn",
    "swiss lawn": "Swiss Lawn",
    "digital lawn": "Digital Lawn",
    "slub lawn": "Slub Lawn",

    # Cotton
    "cotton": "Cotton",
    "pure cotton": "Cotton",
    "cambric": "Cambric",
    "paper cotton": "Paper Cotton",

    # Silk
    "silk": "Silk",
    "raw silk": "Raw Silk",
    "rawsilk": "Raw Silk",
    "tissue silk": "Tissue Silk",
    "tissue": "Tissue Silk",
    "russian silk": "Russian Silk",
    "italian silk": "Italian Silk",
    "poly silk": "Poly Silk",

    # Chiffon
    "chiffon": "Chiffon",
    "crinkle chiffon": "Crinkle Chiffon",
    "bamber chiffon": "Bamber Chiffon",

    # Organza / Net
    "organza": "Organza",
    "net": "Net",
    "khaddi net": "Khaddi Net",
    "rocket net": "Rocket Net",
    "poly net": "Poly Net",

    # Velvet
    "velvet": "Velvet",

    # Linen
    "linen": "Linen",
    "irish linen": "Irish Linen",

    # Khaddar
    "khaddar": "Khaddar",
    "slub khaddar": "Slub Khaddar",
    "karandi": "Karandi",

    # Other Pakistani fabrics
    "jacquard": "Jacquard",
    "self jacquard": "Self Jacquard",
    "viscose": "Viscose",
    "grip": "Grip",
    "monark": "Monark",
    "banarsi": "Banarsi",
    "boski": "Boski",
    "dobby": "Dobby",
    "habotai": "Habotai",
    "wash and wear": "Wash & Wear",
    "wash & wear": "Wash & Wear",
}



COMPONENT_MAP: Dict[str, str] = {

    "shirt": "Shirt",
    "kurta": "Shirt",
    "top": "Shirt",
    "kameez": "Shirt",
    "qameez": "Shirt",

    "trouser": "Trouser",
    "trousers": "Trouser",
    "pant": "Trouser",
    "pants": "Trouser",
    "shalwar": "Trouser",
    "bottom": "Trouser",

    "dupatta": "Dupatta",
    "dupatta": "Dupatta",
    "scarf": "Dupatta",
    "stole": "Dupatta",
    "shawl": "Dupatta",
}



EMBROIDERY_LOCATION_MAP: Dict[str, str] = {

    "neck": "Neckline",
    "neckline": "Neckline",

    "front": "Front",
    "back": "Back",

    "sleeve": "Sleeves",
    "sleeves": "Sleeves",

    "cuff": "Cuffs",
    "cuffs": "Cuffs",

    "panel": "Front Panel",
    "front panel": "Front Panel",

    "center panel": "Front Center Panel",

    "side panel": "Side Panels",

    "daman": "Daman",
    "hem": "Hem",

    "pallu": "Pallu",
}



# Terms removed completely from output

IGNORED_TERMS = {

    # accessories
    "patch",
    "patches",
    "lace",
    "border",
    "borders",
    "patti",
    "tassel",
    "tassels",
    "button",
    "buttons",
    "belt",
    "accessory",
    "accessories",

    # embroidery techniques
    "sequin",
    "sequins",
    "dabka",
    "naqshi",
    "naqqashi",
    "kora",
    "cut dana",
    "beads",
    "pearls",
    "diamante",
    "diamantes",
    "crystal",
    "mirror",
    "stones",
    "tilla",
    "zari",

}

# ============================================================
# Text Cleaning Utilities
# ============================================================


class TextCleaner:
    """
    Responsible for removing HTML noise and normalizing text.
    """

    UNIT_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:meters?|meter|yards?|yard|yds?|"
        r"pcs?|pieces?|piece|pc|"
        r"cm|cms|mm|inch|inches|in)\b",
        flags=re.IGNORECASE,
    )

    MULTI_SPACE_PATTERN = re.compile(r"\s+")


    @classmethod
    def clean(cls, text: str) -> str:
        """
        General text cleaner.
        """

        if not text:
            return ""

        text = str(text)

        text = text.replace("\xa0", " ")
        text = text.replace("’", "'")
        text = text.replace("–", "-")
        text = text.replace("—", "-")

        text = cls.UNIT_PATTERN.sub(" ", text)

        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        text = cls.MULTI_SPACE_PATTERN.sub(
            " ",
            text
        )

        return text.strip(
            " -:;,.|"
        )


    @classmethod
    def normalize_case(cls, text: str) -> str:

        if not text:
            return ""

        return text.strip()



# ============================================================
# JSON-LD Extraction
# ============================================================


class StructuredDataExtractor:
    """
    Extracts product information from JSON-LD.

    Most modern ecommerce systems expose:
        - Shopify
        - WooCommerce
        - Magento

    through schema.org Product objects.
    """

    def __init__(self, soup: BeautifulSoup):

        self.soup = soup



    def extract_json_ld(self) -> List[Dict[str, Any]]:
        """
        Extract all JSON-LD objects.
        """

        results = []


        scripts = self.soup.find_all(
            "script",
            {
                "type": "application/ld+json"
            }
        )


        for script in scripts:

            try:

                if not script.string:
                    continue


                data = json.loads(
                    script.string.strip()
                )


                if isinstance(data, list):

                    results.extend(data)

                elif isinstance(data, dict):

                    results.append(data)


            except Exception:

                logger.debug(
                    "Invalid JSON-LD block ignored"
                )


        return results



    def extract_product_objects(self) -> List[Dict[str, Any]]:
        """
        Return only Product schema objects.
        """

        products = []


        for item in self.extract_json_ld():

            if not isinstance(item, dict):
                continue


            item_type = item.get(
                "@type",
                ""
            )


            if isinstance(item_type, list):

                if "Product" in item_type:
                    products.append(item)


            elif item_type == "Product":

                products.append(item)



        return products



    def extract_description_text(self) -> str:
        """
        Extract description from JSON-LD.
        """

        texts = []


        for product in self.extract_product_objects():

            description = product.get(
                "description"
            )

            if description:

                texts.append(
                    TextCleaner.clean(
                        description
                    )
                )


        return " ".join(texts)



# ============================================================
# HTML Content Extraction
# ============================================================


class HTMLContentExtractor:
    """
    Generic ecommerce HTML extractor.

    Does not rely on:
        - Shopify classes
        - WooCommerce classes
        - Magento classes

    It reads semantic HTML only.
    """

    TAGS = [
        "p",
        "li",
        "span",
        "div",
        "td",
        "th",
        "h1",
        "h2",
        "h3",
        "h4",
    ]


    def __init__(self, soup: BeautifulSoup):

        self.soup = soup



    def extract_visible_text(self) -> List[str]:

        lines = []


        for tag in self.soup.find_all(
            self.TAGS
        ):

            text = tag.get_text(
                " ",
                strip=True
            )


            text = TextCleaner.clean(
                text
            )


            if text:

                lines.append(
                    text
                )


        return self._deduplicate(
            lines
        )



    def extract_tables(self) -> List[str]:

        rows = []


        for table in self.soup.find_all(
            "table"
        ):

            for row in table.find_all(
                "tr"
            ):

                cells = [
                    c.get_text(
                        " ",
                        strip=True
                    )
                    for c in row.find_all(
                        [
                            "td",
                            "th"
                        ]
                    )
                ]


                if cells:

                    rows.append(
                        " ".join(cells)
                    )


        return rows



    def extract_all(self) -> List[str]:

        content = []

        content.extend(
            self.extract_visible_text()
        )

        content.extend(
            self.extract_tables()
        )


        return self._deduplicate(
            content
        )



    @staticmethod
    def _deduplicate(items: List[str]) -> List[str]:

        seen = set()

        output = []


        for item in items:

            key = item.lower()

            if key not in seen:

                seen.add(key)

                output.append(item)


        return output

# ============================================================
# Main Description Parser Foundation
# ============================================================


class DescriptionParser:
    """
    Main production description parser.

    Responsibilities:

        - Collect raw description sources
        - Normalize content
        - Prepare data for component extraction
        - Produce structured description

    This class intentionally does NOT:
        - Extract price
        - Extract SKU
        - Extract images
        - Extract brand

    Those belong to separate modules.
    """

    def __init__(self):

        self.cleaner = TextCleaner


    # --------------------------------------------------------
    # Public Entry Point
    # --------------------------------------------------------

    def parse(
        self,
        html: str
    ) -> ParsedDescription:
        """
        Parse complete product HTML.
        """

        soup = BeautifulSoup(
            html or "",
            "html.parser"
        )


        raw_text = self.collect_description_text(
            soup
        )


        result = ParsedDescription()

        result.raw_text = raw_text


        return result



    # --------------------------------------------------------
    # Description Source Collector
    # --------------------------------------------------------

    def collect_description_text(
        self,
        soup: BeautifulSoup
    ) -> str:
        """
        Combine all possible description sources.

        Priority:

        1. JSON-LD description
        2. HTML visible text
        3. Tables
        4. Meta descriptions
        """

        parts = []


        # JSON-LD

        structured = StructuredDataExtractor(
            soup
        )

        json_description = (
            structured.extract_description_text()
        )


        if json_description:

            parts.append(
                json_description
            )



        # HTML text

        html_extractor = HTMLContentExtractor(
            soup
        )


        html_lines = (
            html_extractor.extract_all()
        )


        parts.extend(
            html_lines
        )



        # Meta descriptions

        parts.extend(
            self.extract_meta_descriptions(
                soup
            )
        )



        cleaned = []

        for item in parts:

            value = self.cleaner.clean(
                item
            )

            if value:

                cleaned.append(
                    value
                )



        return " ".join(
            self.unique(
                cleaned
            )
        )



    # --------------------------------------------------------
    # Meta Extraction
    # --------------------------------------------------------

    def extract_meta_descriptions(
        self,
        soup: BeautifulSoup
    ) -> List[str]:

        output = []


        selectors = [

            {
                "name": "description"
            },

            {
                "property": "og:description"
            },

            {
                "name": "twitter:description"
            }

        ]


        for attrs in selectors:

            tag = soup.find(
                "meta",
                attrs=attrs
            )


            if tag and tag.get(
                "content"
            ):

                output.append(
                    tag.get(
                        "content"
                    )
                )


        return output



    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def unique(
        items: Iterable[str]
    ) -> List[str]:

        seen = set()

        output = []


        for item in items:

            key = item.lower().strip()


            if key not in seen:

                seen.add(
                    key
                )

                output.append(
                    item
                )


        return output

# ============================================================
# Fashion Intelligence Layer
# Component + Fabric Detection
# ============================================================


class FashionAnalyzer:
    """
    Converts raw description text into fashion components.

    This layer contains generalized fashion rules only.

    No:
        - brand rules
        - website rules
        - XPath rules
        - Shopify rules
    """


    def __init__(self):

        self.fabric_map = FABRIC_MAP

        self.component_map = COMPONENT_MAP

        self.ignored_terms = IGNORED_TERMS



    # --------------------------------------------------------
    # Component Detection
    # --------------------------------------------------------

    def detect_component(
        self,
        text: str
    ) -> Optional[str]:
        """
        Detect whether text belongs to:

            Shirt
            Trouser
            Dupatta
        """

        if not text:
            return None


        lower = text.lower()



        for keyword, component in (
            self.component_map.items()
        ):

            if keyword in lower:

                return component



        return None



    # --------------------------------------------------------
    # Fabric Detection
    # --------------------------------------------------------

    def detect_fabrics(
        self,
        text: str
    ) -> List[str]:
        """
        Extract normalized fabrics.
        """

        if not text:

            return []


        lower = text.lower()


        found = []


        # longest match first

        fabrics = sorted(
            self.fabric_map.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )


        for keyword, canonical in fabrics:

            if keyword in lower:

                if canonical not in found:

                    found.append(
                        canonical
                    )



        return found



    # --------------------------------------------------------
    # Remove unwanted content
    # --------------------------------------------------------

    def remove_ignored_terms(
        self,
        text: str
    ) -> str:
        """
        Removes:

            - patches
            - borders
            - lace
            - accessories
            - embroidery techniques

        """

        if not text:

            return ""



        result = text



        for term in self.ignored_terms:

            result = re.sub(
                rf"\b{re.escape(term)}\b",
                " ",
                result,
                flags=re.IGNORECASE
            )



        result = re.sub(
            r"\s+",
            " ",
            result
        )


        return result.strip()



    # --------------------------------------------------------
    # Sentence splitting
    # --------------------------------------------------------

    def split_sentences(
        self,
        text: str
    ) -> List[str]:

        if not text:

            return []


        text = text.replace(
            "\n",
            "."
        )


        parts = re.split(
            r"[.!;|]",
            text
        )


        output = []


        for part in parts:

            clean = TextCleaner.clean(
                part
            )


            if clean:

                output.append(
                    clean
                )


        return output

# ============================================================
# Color + Embroidery Intelligence
# ============================================================


COLOR_MAP: Dict[str, str] = {

    # Whites / neutrals

    "white": "White",
    "off white": "Off White",
    "ivory": "Ivory",
    "cream": "Cream",
    "pearl white": "Pearl White",


    # Pink shades

    "pink": "Pink",
    "light pink": "Light Pink",
    "baby pink": "Baby Pink",
    "tea pink": "Tea Pink",
    "dusty pink": "Dusty Pink",
    "blush": "Blush",
    "peach": "Peach",
    "coral": "Coral",


    # Green shades

    "green": "Green",
    "mint green": "Mint Green",
    "sea green": "Sea Green",
    "sage green": "Sage Green",
    "pista": "Pista",
    "pistachio": "Pistachio",
    "olive": "Olive",
    "bottle green": "Bottle Green",


    # Blue shades

    "blue": "Blue",
    "sky blue": "Sky Blue",
    "ice blue": "Ice Blue",
    "powder blue": "Powder Blue",
    "royal blue": "Royal Blue",
    "navy blue": "Navy Blue",
    "firozi": "Firozi",
    "ferozi": "Ferozi",
    "turquoise": "Turquoise",


    # Purple

    "purple": "Purple",
    "lavender": "Lavender",
    "lilac": "Lilac",
    "mauve": "Mauve",
    "plum": "Plum",


    # Red / Maroon

    "red": "Red",
    "maroon": "Maroon",
    "wine": "Wine",
    "burgundy": "Burgundy",
    "rust": "Rust",


    # Yellow / Gold

    "yellow": "Yellow",
    "mustard": "Mustard",
    "gold": "Gold",
    "golden": "Golden",


    # Brown / Beige

    "brown": "Brown",
    "beige": "Beige",
    "camel": "Camel",
    "skin": "Skin",
    "nude": "Nude",


    # Black

    "black": "Black",

}



class EmbroideryAnalyzer:
    """
    Extracts only embroidery placement.

    IMPORTANT:

    It intentionally removes:

        sequins
        dabka
        naqshi
        beads
        stones
        pearls
        crystals

    because these are techniques, not product structure.

    Allowed output:

        Neckline
        Front
        Back
        Sleeves
        Cuffs
        Panels
        Daman
        Hem
        Pallu
    """



    def __init__(self):

        self.locations = EMBROIDERY_LOCATION_MAP


        self.techniques = [

            "sequin",
            "sequins",
            "dabka",
            "naqshi",
            "naqqashi",
            "kora",
            "bead",
            "beads",
            "pearls",
            "stone",
            "stones",
            "crystal",
            "diamante",
            "mirror",
            "tilla",
            "zari",
            "thread work"

        ]



    def extract_locations(
        self,
        text: str
    ) -> List[str]:

        if not text:

            return []


        lower = text.lower()


        found = []



        for keyword, location in (
            self.locations.items()
        ):

            if keyword in lower:

                if location not in found:

                    found.append(
                        location
                    )


        return found



    def remove_techniques(
        self,
        text: str
    ) -> str:

        result = text



        for technique in self.techniques:

            result = re.sub(

                rf"\b{re.escape(technique)}\b",

                " ",

                result,

                flags=re.IGNORECASE

            )


        return re.sub(
            r"\s+",
            " ",
            result
        ).strip()

# ============================================================
# Component Description Builder
# ============================================================


class ComponentBuilder:
    """
    Builds structured clothing components.

    Converts raw sentences into:

        Shirt:
            Fabric
            Colors
            Embroidery locations

        Trouser:
            Fabric
            Colors

        Dupatta:
            Fabric
            Colors
            Embroidery locations
    """



    def __init__(self):

        self.fashion = FashionAnalyzer()

        self.embroidery = EmbroideryAnalyzer()



    # --------------------------------------------------------
    # Color extraction
    # --------------------------------------------------------

    def extract_colors(
        self,
        text: str
    ) -> List[str]:

        if not text:

            return []


        lower = text.lower()


        colors = []


        # longest first

        ordered = sorted(
            COLOR_MAP.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )


        for keyword, value in ordered:

            if keyword in lower:

                if value not in colors:

                    colors.append(
                        value
                    )


        return colors



    # --------------------------------------------------------
    # Add sentence to component
    # --------------------------------------------------------

    def process_sentence(
        self,
        component: ComponentDescription,
        sentence: str
    ):

        if not sentence:

            return



        sentence = self.fashion.remove_ignored_terms(
            sentence
        )


        sentence = self.embroidery.remove_techniques(
            sentence
        )



        # Fabric

        fabrics = self.fashion.detect_fabrics(
            sentence
        )


        for fabric in fabrics:

            if fabric not in component.fabrics:

                component.fabrics.append(
                    fabric
                )



        # Colors

        colors = self.extract_colors(
            sentence
        )


        for color in colors:

            if color not in component.colors:

                component.colors.append(
                    color
                )



        # Embroidery locations

        locations = (
            self.embroidery.extract_locations(
                sentence
            )
        )


        for location in locations:

            if location not in component.embroidery_locations:

                component.embroidery_locations.append(
                    location
                )



    # --------------------------------------------------------
    # Main build
    # --------------------------------------------------------

    def build(
        self,
        text: str
    ) -> ParsedDescription:


        result = ParsedDescription()

        result.raw_text = text



        sentences = (
            self.fashion.split_sentences(
                text
            )
        )



        for sentence in sentences:


            component_name = (
                self.fashion.detect_component(
                    sentence
                )
            )



            if component_name == "Shirt":

                self.process_sentence(
                    result.shirt,
                    sentence
                )



            elif component_name == "Trouser":

                self.process_sentence(
                    result.trouser,
                    sentence
                )



            elif component_name == "Dupatta":

                self.process_sentence(
                    result.dupatta,
                    sentence
                )



            else:

                # Generic sentences without component
                # are usually shirt information

                self.process_sentence(
                    result.shirt,
                    sentence
                )



        return self.normalize_components(
            result
        )



    # --------------------------------------------------------
    # Component cleanup
    # --------------------------------------------------------

    def normalize_components(
        self,
        result: ParsedDescription
    ) -> ParsedDescription:


        for component in [

            result.shirt,
            result.trouser,
            result.dupatta

        ]:


            component.fabrics = (
                self.unique(
                    component.fabrics
                )
            )


            component.colors = (
                self.unique(
                    component.colors
                )
            )


            component.embroidery_locations = (
                self.unique(
                    component.embroidery_locations
                )
            )



        return result



    @staticmethod
    def unique(
        values: List[str]
    ) -> List[str]:

        output = []

        seen = set()


        for value in values:

            if value not in seen:

                seen.add(
                    value
                )

                output.append(
                    value
                )


        return output

# ============================================================
# Output Formatter
# ============================================================


class DescriptionFormatter:
    """
    Converts structured description into
    ProductExtractorV4 output format.

    Rules:

        - No embroidery techniques
        - No accessories
        - No marketing text
        - Only useful production details
    """



    def format_component(
        self,
        component: ComponentDescription
    ) -> str:

        lines = []


        # Fabric

        if component.fabrics:

            lines.append(
                "Fabric: "
                +
                ", ".join(
                    component.fabrics
                )
            )



        # Embroidery locations

        if component.embroidery_locations:

            lines.append(
                "Embroidery: "
                +
                ", ".join(
                    component.embroidery_locations
                )
            )



        # Colors

        if component.colors:

            lines.append(
                "Color: "
                +
                ", ".join(
                    component.colors
                )
            )



        if not lines:

            lines.append(
                "Not detected"
            )


        return "\n".join(
            lines
        )



    def format(
        self,
        description: ParsedDescription
    ) -> str:


        output = []


        output.append(
            "Shirt:"
        )


        output.append(
            self.format_component(
                description.shirt
            )
        )



        output.append(
            ""
        )


        output.append(
            "Trouser:"
        )


        output.append(
            self.format_component(
                description.trouser
            )
        )



        output.append(
            ""
        )


        output.append(
            "Dupatta:"
        )


        output.append(
            self.format_component(
                description.dupatta
            )
        )



        return "\n".join(
            output
        )





# ============================================================
# Production Parser API
# ============================================================


class ProductionDescriptionParser:
    """
    High level parser used by ProductExtractorV4.

    Usage:

        parser = ProductionDescriptionParser()

        result = parser.parse(html)

        text = parser.format(result)
    """



    def __init__(self):

        self.base_parser = DescriptionParser()

        self.builder = ComponentBuilder()

        self.formatter = DescriptionFormatter()



    def parse(
        self,
        html: str
    ) -> ParsedDescription:


        collected = (
            self.base_parser.collect_description_text(
                BeautifulSoup(
                    html or "",
                    "html.parser"
                )
            )
        )


        return self.builder.build(
            collected
        )



    def format(
        self,
        parsed: ParsedDescription
    ) -> str:

        return self.formatter.format(
            parsed
        )



    def parse_and_format(
        self,
        html: str
    ) -> str:


        parsed = self.parse(
            html
        )


        return self.format(
            parsed
        )

# ============================================================
# Backward Compatibility Layer
# ============================================================


class LegacyDescriptionParser:
    """
    Compatibility wrapper.

    Keeps existing ProductExtractorV4 imports working.

    Existing usage:

        parser = DescriptionParser()

        parser.final_description(
            html,
            brand
        )

    continues to work.
    """



    def __init__(self):

        self.parser = ProductionDescriptionParser()



    def final_description(
        self,
        html: str,
        brand: str = ""
    ) -> str:


        try:

            description = (
                self.parser.parse_and_format(
                    html
                )
            )


            if brand:

                return (
                    "Designer/Brand:\n"
                    f"{brand}\n\n"
                    +
                    description
                )


            return description



        except Exception as exc:

            logger.exception(
                "Description parsing failed: %s",
                exc
            )

            return ""



    def get_shirt_fabric(
        self,
        html: str
    ) -> str:


        try:

            parsed = (
                self.parser.parse(
                    html
                )
            )


            if parsed.shirt.fabrics:

                return (
                    parsed.shirt.fabrics[0]
                )


        except Exception as exc:

            logger.exception(
                "Fabric extraction failed: %s",
                exc
            )


        return ""





# ============================================================
# Module Level Convenience Functions
# ============================================================


def parse_description(
    html: str
) -> ParsedDescription:
    """
    Simple parser interface.
    """

    parser = ProductionDescriptionParser()

    return parser.parse(
        html
    )





def format_description(
    html: str
) -> str:
    """
    Parse and directly return formatted output.
    """

    parser = ProductionDescriptionParser()

    return parser.parse_and_format(
        html
    )





# ============================================================
# Final Compatibility Alias
# ============================================================


# Existing project code expects:
#
# from extractor.description_parser import DescriptionParser
#
# Therefore expose the production wrapper.


OriginalDescriptionParser = DescriptionParser


DescriptionParser = LegacyDescriptionParser
