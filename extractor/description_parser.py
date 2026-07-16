"""
description_parser.py
Intelligent description formatter for Pakistani clothing brands.
"""
import re
import logging

logger = logging.getLogger("ProductExtractor")

class DescriptionParser:
    def __init__(self):
        # FIXED: Removed trailing spaces
        self.fabrics = [
            "lawn", "cambric", "dobby", "cotton", "jacquard", 
            "chiffon", "organza", "silk", "poly cotton", "rocket net", 
            "net", "poly silk", "rawsilk"
        ]
        self.patterns = [
            "digital printed", "embroidered", "printed", "dyed", 
            "plain", "woven", "sequin"
        ]

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\b\d+(?:\.\d+)?\s*(?:meters?|m|yards?|yd|pcs?|pieces?)\b', '', text, flags=re.IGNORECASE)
        noise_patterns = [
            r'(?i)note\s*:.*',
            r'(?i)\*\s*the stitch style.*',
            r'(?i)base component consumption per suit',
            r'(?i)add-on:.*',
            r'(?i)sku:.*',
            r'(?i)availability:.*',
            r'(?i)product description',
            r'(?i)fabric:\s*lawn\s*season:.*',
            r'(?i)refer to product description.*'
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _find_fabric(self, text: str) -> str:
        text_lower = text.lower()
        for fabric in self.fabrics:
            if fabric in text_lower:
                return fabric.title()
        return "Lawn"

    def _find_pattern(self, text: str) -> str:
        text_lower = text.lower()
        found = [pattern.title() for pattern in self.patterns if pattern in text_lower]
        
        if "Digital Printed" in found and "Embroidered" in found:
            return "Digital Printed and Embroidered"
        if "Embroidered" in found:
            return "Embroidered"
        if "Digital Printed" in found:
            return "Digital Printed"
        if "Printed" in found:
            return "Printed"
        if "Dyed" in found:
            return "Dyed"
        return "Plain"

    def _find_parts(self, text: str) -> list:
        text_lower = text.lower()
        parts = []
        if "front" in text_lower or "panel" in text_lower or "kali" in text_lower:
            parts.append("front panels")
        if "back" in text_lower:
            parts.append("back panel")
        if "sleeve" in text_lower:
            parts.append("sleeves")
        if "neckline" in text_lower or "neck" in text_lower:
            parts.append("neckline")
        return list(dict.fromkeys(parts))

    def format_shirt(self, text: str) -> str:
        shirt_keywords = ["shirt", "front", "back", "sleeve", "kali", "motif"]
        lines = text.split('.')
        relevant_lines = [line for line in lines if any(kw in line.lower() for kw in shirt_keywords)]
        
        if not relevant_lines:
            relevant_lines = [text]
        
        relevant_text = " ".join(relevant_lines)
        fabric = self._find_fabric(relevant_text)
        pattern = self._find_pattern(relevant_text)
        parts = self._find_parts(relevant_text)
        parts_str = f" {', '.join(parts)}" if parts else ""
        
        if "Digital Printed" in pattern and "Embroidered" in pattern:
            return f"Fabric: Digital Printed {fabric} Shirt with embroidered{parts_str}."
        elif "Embroidered" in pattern:
            return f"Fabric: {fabric} Shirt with embroidered{parts_str}."
        elif "Printed" in pattern or "Digital Printed" in pattern:
            return f"Fabric: {pattern} {fabric} Shirt{parts_str}."
        else:
            return f"Fabric: {pattern} {fabric} Shirt{parts_str}."

    def format_trouser(self, text: str) -> str:
        trouser_keywords = ["trouser", "pants", "shalwar"]
        lines = text.split('.')
        relevant_lines = [line for line in lines if any(kw in line.lower() for kw in trouser_keywords)]
        
        if not relevant_lines:
            return "Fabric: Dyed Lawn Trousers."
        
        relevant_text = " ".join(relevant_lines).lower()
        fabric = self._find_fabric(relevant_text)
        
        # FIXED: ONLY mention embroidery if explicitly stated
        has_embroidery = "embroidered" in relevant_text
        
        if has_embroidery:
            return f"Fabric: Embroidered {fabric} Trousers."
        else:
            pattern = self._find_pattern(relevant_text)
            if pattern == "Plain":
                return f"Fabric: {fabric} Trousers."
            return f"Fabric: {pattern} {fabric} Trousers."

    def format_dupatta(self, text: str) -> str:
        lines = text.split('.')
        relevant_lines = [line for line in lines if "dupatta" in line.lower()]
        
        if not relevant_lines:
            return "Fabric: Lawn Dupatta."
        
        relevant_text = " ".join(relevant_lines).lower()
        fabric = self._find_fabric(relevant_text)
        
        has_embroidery = "embroidered" in relevant_text
        has_pallu = "pallu" in relevant_text or "pallo" in relevant_text
        
        if has_pallu:
            if has_embroidery:
                return f"Fabric: Embroidered {fabric} Dupatta with embroidered pallu."
            else:
                return f"Fabric: {fabric} Dupatta with pallu."
        elif has_embroidery:
            return f"Fabric: Embroidered {fabric} Dupatta."
        else:
            pattern = self._find_pattern(relevant_text)
            if pattern == "Plain":
                return f"Fabric: {fabric} Dupatta."
            return f"Fabric: {pattern} {fabric} Dupatta."

    def final_description(self, raw_text: str, brand: str = "Unknown") -> str:
        cleaned = self.clean_text(raw_text)
        shirt_desc = self.format_shirt(cleaned)
        trouser_desc = self.format_trouser(cleaned)
        dupatta_desc = self.format_dupatta(cleaned)
        
        output = f"Designer/Brand:\n{brand}.\n\n"
        output += f"Shirt:\n{shirt_desc}\n\n"
        output += f"Trousers:\n{trouser_desc}\n\n"
        output += f"Dupatta:\n{dupatta_desc}"
        
        return output
