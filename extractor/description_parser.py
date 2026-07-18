"""
================================================================================
VERSION 4.0 - REGEX FIX (NO LINE SPLITTING)
Uses regex context matching to ignore HTML formatting/line-break issues.
================================================================================
"""
import re
from bs4 import BeautifulSoup

class DescriptionParser:
    def __init__(self):
        # Order matters: more specific fabrics first
        self.fabrics = [
            "raw silk", "rocket net", "poly silk", "poly cotton", "wash & wear", 
            "habotai", "lawn", "cotton", "silk", "chiffon", "organza", "dobby", 
            "cambric", "khaddar", "velvet", "linen", "jacquard", "net", "siquence", "sequin"
        ]

    def _extract_fabric(self, text):
        text_lower = text.lower()
        for f in self.fabrics:
            if f in text_lower:
                if f == "raw silk": return "Raw Silk"
                if f == "rocket net": return "Rocket Net"
                if f == "poly silk": return "Poly Silk"
                if f == "poly cotton": return "Poly Cotton"
                if f == "wash & wear": return "Wash & Wear"
                return f.capitalize()
        return "Fabric"

    def format_shirt(self, text):
        text_lower = text.lower()
        fabric = self._extract_fabric(text_lower)
        if fabric == "Fabric": fabric = "Lawn" # Fallback
        
        attrs = []
        if 'floral printed' in text_lower: attrs.append('Floral Printed')
        elif 'digital printed' in text_lower: attrs.append('Digital Printed')
        elif 'printed' in text_lower: attrs.append('Printed')
        
        if 'dyed' in text_lower: attrs.append('Dyed')
        if 'plain' in text_lower: attrs.append('Plain')
        
        emb_parts = []
        if 'embroidered' in text_lower:
            if 'neckline' in text_lower: emb_parts.append('neckline')
            if 'front' in text_lower: emb_parts.append('front motifs')
            if 'back' in text_lower: emb_parts.append('back')
            if 'sleeves' in text_lower: emb_parts.append('sleeves')
            
        attr_str = " ".join(attrs)
        emb_str = ""
        if emb_parts:
            if len(emb_parts) == 1:
                emb_str = f" with embroidered {emb_parts[0]}"
            else:
                last = emb_parts.pop()
                emb_str = f" with embroidered {', '.join(emb_parts)} and {last}"
                
        base = f"{fabric} shirt"
        if attr_str: base = f"{attr_str} {fabric} shirt"
        
        if emb_str: return f"{base}{emb_str}."
        return f"{base}."

    def format_trouser(self, text):
        text_lower = text.lower()
        # Extract context around "trouser" to avoid picking up shirt fabrics
        match = re.search(r'([a-z\s&]{0,40}trouser[a-z\s&]{0,20})', text_lower)
        t_text = match.group(1) if match else text_lower
        
        fabric = self._extract_fabric(t_text)
        if fabric == "Fabric": fabric = "Cotton" # Fallback
        
        attrs = []
        if 'dyed' in t_text: attrs.append('Dyed')
        if 'printed' in t_text: attrs.append('Printed')
        if 'plain' in t_text: attrs.append('Plain')
        
        attr_str = " ".join(attrs)
        if attr_str: return f"{attr_str} {fabric}."
        return f"{fabric}."

    def format_dupatta(self, text):
        text_lower = text.lower()
        # Extract context around "dupatta" or "shawl"
        match = re.search(r'([a-z\s&]{0,40}(?:dupatta|shawl)[a-z\s&]{0,20})', text_lower)
        if match:
            d_text = match.group(1)
            item_name = "Shawl" if "shawl" in d_text else "Dupatta"
        else:
            d_text = text_lower
            item_name = "Dupatta"
            
        fabric = self._extract_fabric(d_text)
        if fabric == "Fabric": fabric = "Fabric" # Fallback
        
        if 'pallu' in d_text and 'embroidered' in d_text:
            return f"{fabric} with embroidered pallu."
            
        attrs = []
        if 'digital printed' in d_text: attrs.append('Digital Printed')
        elif 'printed' in d_text: attrs.append('Printed')
        if 'embroidered' in d_text: attrs.append('Embroidered')
            
        attr_str = " ".join(attrs)
        if attr_str:
            if attr_str == "Embroidered":
                return f"{fabric} {attr_str} {item_name}."
            return f"{attr_str} {fabric} {item_name}."
        return f"{fabric} {item_name}."

    def final_description(self, html: str, brand: str) -> str:
        # LOUD DEBUG MESSAGE TO VERIFY FILE IS LOADED
        print("\n" + "!" * 50)
        print("!!! RUNNING DESCRIPTION PARSER V4.0 - REGEX FIX !!!")
        print("!" * 50 + "\n")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get all text from the page
        raw_text = soup.get_text(separator=' ', strip=True)
        
        # Remove lengths, pieces, meters, yards, etc.
        cleaned_text = re.sub(r'\b\d+(\.\d+)?\s*(meters?|yards?|pcs?|pieces?|meter|yard|pc|piece)\b', '', raw_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Build the structured description using regex context matching
        shirt_desc = self.format_shirt(cleaned_text)
        trouser_desc = self.format_trouser(cleaned_text)
        dupatta_desc = self.format_dupatta(cleaned_text)
        
        final_output = f"""Designer/Brand:
{brand}.

Shirt:
Fabric: {shirt_desc}

Trouser:
Fabric: {trouser_desc}

Dupatta:
Fabric: {dupatta_desc}

------------------------"""
        return final_output.strip()

    def get_shirt_fabric(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True).lower()
        
        for fabric in self.fabrics:
            if re.search(rf'\b{fabric}\b', text):
                if fabric == "raw silk": return "Raw Silk"
                if fabric == "rocket net": return "Rocket Net"
                if fabric == "poly silk": return "Poly Silk"
                return fabric.capitalize()
        return "Lawn"