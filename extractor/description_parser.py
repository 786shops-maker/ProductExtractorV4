"""
Description parser for fashion product pages.

This parser converts raw text/HTML from clothing websites into a structured
description format such as:

Designer/Brand:
Edenrobe.

Shirt:
Fabric: Chiffon shirt with embroidered neckline, front, back, sleeves, and borders.

Trousers:
Fabric: Rawsilk Plain Trouser.

Dupatta:
Fabric: Net Embroidered Dupatta.
"""

import re
from typing import List, Optional
from bs4 import BeautifulSoup


class DescriptionParser:
    def __init__(self):
        self.fabric_patterns = [
            ("raw silk", "Raw Silk"),
            ("rawsilk", "Raw Silk"),
            ("rocket net", "Rocket Net"),
            ("poly silk", "Poly Silk"),
            ("poly cotton", "Poly Cotton"),
            ("wash & wear", "Wash & Wear"),
            ("habotai", "Habotai"),
            ("lawn", "Lawn"),
            ("cotton", "Cotton"),
            ("silk", "Silk"),
            ("chiffon", "Chiffon"),
            ("organza", "Organza"),
            ("dobby", "Dobby"),
            ("cambric", "Cambric"),
            ("khaddar", "Khaddar"),
            ("velvet", "Velvet"),
            ("linen", "Linen"),
            ("jacquard", "Jacquard"),
            ("net", "Net"),
            ("siquence", "Sequin"),
            ("sequin", "Sequin"),
        ]

        self.component_keywords = {
            "shirt": ["shirt", "kurta", "neckline", "sleeve", "sleeves", "front", "back", "border", "embroidered"],
            "trouser": ["trouser", "shalwar", "pants", "pant"],
            "dupatta": ["dupatta", "pallu"],
        }

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("’", "'")
        text = text.replace("–", "-")
        text = text.replace("—", "-")
        text = text.replace("\xa0", " ")

        text = re.sub(
            r"\b\d+(?:\.\d+)?\s*(?:meters?|meter|yards?|yard|pcs?|pieces?|piece|pc|m|cm|cms|inch|inches)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\(\s*\d+(?:\.\d+)?\s*(?:meters?|meter|yards?|yard|pcs?|pieces?|piece|pc|m|cm|cms|inch|inches)\s*\)",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(r"\s+", " ", text)
        return text.strip(" -:;,.")

    def _dedup(self, items: List[str]) -> List[str]:
        seen = []
        result = []
        for item in items:
            clean = self._clean_text(item)
            if clean and clean not in seen:
                seen.append(clean)
                result.append(clean)
        return result

    def _is_relevant_line(self, line: str) -> bool:
        if not line:
            return False

        cleaned = self._clean_text(line)
        if not cleaned:
            return False

        lower = cleaned.lower()
        keywords = [
            "embroidered", "dupatta", "pallu", "trouser", "shalwar", "pants",
            "shirt", "kurta", "neckline", "sleeve", "sleeves", "front", "back",
            "border", "printed", "dyed", "plain", "fabric", "chiffon",
            "lawn", "cotton", "silk", "cambric", "organza", "dobby",
            "poly", "raw", "rocket", "khaddar"
        ]
        return any(k in lower for k in keywords)

    def _extract_page_lines(self, soup: BeautifulSoup) -> List[str]:
        lines: List[str] = []

        # Full page text
        full_text = soup.get_text("\n", strip=True)
        for raw_line in full_text.split("\n"):
            line = self._clean_text(raw_line)
            if self._is_relevant_line(line):
                lines.append(line)

        # Meta descriptions
        for attrs in [
            {"name": "description"},
            {"property": "og:description"},
            {"name": "twitter:description"},
        ]:
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                line = self._clean_text(tag["content"])
                if self._is_relevant_line(line):
                    lines.append(line)

        # Visible HTML text blocks
        for tag in soup.find_all(["p", "li", "div", "span", "h1", "h2", "h3"]):
            for raw_line in tag.get_text("\n", strip=True).split("\n"):
                line = self._clean_text(raw_line)
                if self._is_relevant_line(line):
                    lines.append(line)

        return self._dedup(lines)

    def _classify_line(self, line: str) -> Optional[str]:
        lower = line.lower()

        if "dupatta" in lower or "pallu" in lower:
            return "dupatta"

        if any(k in lower for k in ["trouser", "shalwar", "pants", "pant"]):
            return "trouser"

        if any(k in lower for k in ["shirt", "kurta", "neckline", "sleeve", "sleeves", "front", "back", "border", "embroidered"]):
            return "shirt"

        return None

    def _extract_fabric_from_line(self, line: str) -> Optional[str]:
        lower = line.lower()

        for pattern, canonical in self.fabric_patterns:
            if pattern in lower:
                return canonical

        return None

    def _extract_style_from_line(self, line: str) -> Optional[str]:
        lower = line.lower()

        if "floral" in lower and "printed" in lower:
            return "Floral Printed"
        if "digital" in lower and "printed" in lower:
            return "Digital Printed"
        if "printed" in lower and "plain" not in lower:
            return "Printed"
        if "plain" in lower:
            return "Plain"
        if "dyed" in lower:
            return "Dyed"

        return None

    def _extract_embroidery_features_from_line(self, line: str) -> List[str]:
        lower = line.lower()
        features = []

        if "neckline" in lower:
            features.append("neckline")
        if "front" in lower:
            features.append("front")
        if "back" in lower:
            features.append("back")
        if "sleeve" in lower or "sleeves" in lower:
            features.append("sleeves")
        if "border" in lower:
            features.append("borders")
        if "pallu" in lower:
            features.append("pallu")

        return features

    def _unique_features(self, features: List[str]) -> List[str]:
        seen = []
        result = []
        for item in features:
            if item not in seen:
                seen.append(item)
                result.append(item)
        return result

    def _format_embroidery_phrase(self, features: List[str]) -> str:
        if not features:
            return ""

        if len(features) == 1:
            return f"with embroidered {features[0]}"

        if len(features) == 2:
            return f"with embroidered {features[0]} and {features[1]}"

        return f"with embroidered {', '.join(features[:-1])}, and {features[-1]}"

    def format_shirt(self, lines: List[str]) -> str:
        shirt_lines = [line for line in lines if self._classify_line(line) == "shirt"]

        if not shirt_lines:
            return "Lawn shirt."

        # Prefer the most descriptive shirt lines
        shirt_lines = sorted(
            shirt_lines,
            key=lambda line: (
                len(self._extract_embroidery_features_from_line(line)),
                len(line),
            ),
            reverse=True,
        )

        fabric = self._extract_fabric_from_line(shirt_lines[0]) or "Lawn"
        style = self._extract_style_from_line(shirt_lines[0])
        features = self._unique_features(
            [feature for line in shirt_lines for feature in self._extract_embroidery_features_from_line(line)]
        )

        if features:
            if style and style.lower() not in ["plain", "dyed"]:
                return f"{style} {fabric} shirt {self._format_embroidery_phrase(features)}."
            return f"{fabric} shirt {self._format_embroidery_phrase(features)}."

        if style:
            return f"{style} {fabric} shirt."

        return f"{fabric} shirt."

    def format_trouser(self, lines: List[str]) -> str:
        trouser_lines = [line for line in lines if self._classify_line(line) == "trouser"]

        if not trouser_lines:
            return "Cotton."

        # Prefer the line that directly mentions Trouser
        best = sorted(
            trouser_lines,
            key=lambda line: (len(line), line.count(" ")),
            reverse=False,
        )[0]

        return self._clean_text(best)

    def format_dupatta(self, lines: List[str]) -> str:
        dupatta_lines = [line for line in lines if self._classify_line(line) == "dupatta"]

        if not dupatta_lines:
            return "Lawn."

        # Prefer the line that directly mentions Dupatta
        best = sorted(
            dupatta_lines,
            key=lambda line: (len(line), line.count(" ")),
            reverse=False,
        )[0]

        return self._clean_text(best)

    def _extract_brand(self, soup: BeautifulSoup) -> str:
        for attrs in [
            {"name": "brand"},
            {"property": "og:brand"},
            {"itemprop": "brand"},
            {"name": "author"},
            {"property": "og:site_name"},
            {"name": "application-name"},
        ]:
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                return tag["content"].strip()

        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        if title:
            return title.split("|")[0].strip()

        return "Unknown Brand"

    def final_description(self, html: str, brand: str) -> str:
        soup = BeautifulSoup(html or "", "html.parser")
        lines = self._extract_page_lines(soup)

        shirt_desc = self.format_shirt(lines)
        trouser_desc = self.format_trouser(lines)
        dupatta_desc = self.format_dupatta(lines)

        brand_name = (brand or "").strip() or self._extract_brand(soup) or "Unknown Brand"

        output = (
            f"Designer/Brand:\n"
            f"{brand_name}.\n\n"
            f"Shirt:\n"
            f"Fabric: {shirt_desc}\n\n"
            f"Trousers:\n"
            f"Fabric: {trouser_desc}\n\n"
            f"Dupatta:\n"
            f"Fabric: {dupatta_desc}"
        )

        return output.strip()

    def get_shirt_fabric(self, html: str) -> str:
        soup = BeautifulSoup(html or "", "html.parser")
        lines = self._extract_page_lines(soup)

        for line in lines:
            fabric = self._extract_fabric_from_line(line)
            if fabric:
                return fabric

        return "Lawn"
