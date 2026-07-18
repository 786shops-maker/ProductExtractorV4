"""
color_detector.py
Detects the color of the product from HTML text robustly.
"""
import re
from bs4 import BeautifulSoup

class ColorDetector:
    def __init__(self):
        self.colors = [
            "Green", "Blue", "Red", "Black", "White", "Pink", "Peach", 
            "Yellow", "Purple", "Grey", "Gray", "Brown", "Maroon", 
            "Navy", "Teal", "Mint", "Cream", "Beige", "Gold", "Golden", "Silver",
            "Olive", "Rust", "Coral", "Lavender", "Turquoise", "Mustard", "Emerald",
            "Ivory", "Off-White", "Multi", "Magenta", "Fuchsia", "Crimson", "Indigo", "Charcoal"
        ]

    def detect_color(self, html: str, image_path: str = None) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # 1. Look for explicit "Color: [Color]" or "Colour: [Color]"
        color_match = re.search(r'(?:color|colour)\s*[:\-]?\s*([a-zA-Z\-]+)', text, re.IGNORECASE)
        if color_match:
            color_word = color_match.group(1).strip().capitalize()
            if color_word in self.colors:
                return color_word
            # Fallback: if it's a short word right after "Color:", it's likely the color
            if len(color_word) <= 12:
                return color_word

        # 2. Look for "[Color] Suit" or "[Color] Shirt" or "[Color] Fabric"
        text_lower = text.lower()
        for color in self.colors:
            pattern = rf'\b{color.lower()}\b\s+(?:suit|shirt|dress|fabric|lawn|silk|embroidered)'
            if re.search(pattern, text_lower):
                return color

        # 3. Fallback: Just find any color word in the text
        for color in self.colors:
            if re.search(rf'\b{color.lower()}\b', text_lower):
                return color

        return ""