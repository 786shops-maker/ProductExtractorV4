"""
color_detector.py
Analyzes product pages and images to determine the dress color.
First checks page text for color mentions, then falls back to image analysis.
"""
import re
import logging
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np

logger = logging.getLogger("ProductExtractor")

# Color names to search for in page text
COLOR_NAMES = [
    "yellow", "black", "white", "grey", "gray", "navy", "blue", "royal blue",
    "sky blue", "teal", "green", "olive", "mint", "mustard", "gold", "orange",
    "peach", "coral", "red", "maroon", "burgundy", "pink", "hot pink", "rose",
    "purple", "lavender", "beige", "cream", "brown", "tan", "cyan", "turquoise",
    "emerald", "lime", "magenta", "violet", "indigo", "scarlet", "crimson",
    "silver", "bronze", "copper", "champagne", "ivory", "charcoal", "wine",
    "fuchsia", "aqua", "turquoise", "mauve", "plum", "rust", "salmon"
]

# Named color palette in HSV for image analysis (H: 0-180, S: 0-255, V: 0-255)
COLOR_PALETTE = {
    "Black":        ((0, 0, 0), (180, 255, 50)),
    "White":        ((0, 0, 230), (180, 30, 255)),
    "Grey":         ((0, 0, 80), (180, 30, 200)),
    "Navy Blue":    ((100, 80, 50), (130, 255, 150)),
    "Royal Blue":   ((100, 80, 150), (130, 255, 255)),
    "Sky Blue":     ((90, 40, 150), (120, 180, 255)),
    "Blue":         ((95, 60, 100), (135, 255, 255)),
    "Teal":         ((75, 60, 100), (95, 255, 220)),
    "Green":        ((35, 60, 80), (85, 255, 220)),
    "Olive":        ((20, 50, 60), (45, 180, 180)),
    "Mint":         ((60, 30, 180), (90, 150, 255)),
    "Yellow":       ((20, 80, 180), (35, 255, 255)),
    "Light Yellow": ((18, 40, 200), (28, 150, 255)),
    "Mustard":      ((18, 80, 120), (30, 220, 200)),
    "Gold":         ((18, 100, 150), (32, 255, 230)),
    "Orange":       ((5, 100, 150), (18, 255, 255)),
    "Peach":        ((0, 40, 200), (15, 130, 255)),
    "Coral":        ((0, 60, 180), (12, 200, 240)),
    "Red":          ((0, 100, 100), (8, 255, 255)),
    "Maroon":       ((0, 100, 50), (10, 255, 160)),
    "Burgundy":     ((0, 80, 50), (175, 200, 150)),
    "Pink":         ((150, 40, 180), (175, 180, 255)),
    "Hot Pink":     ((150, 80, 180), (175, 255, 255)),
    "Rose":         ((165, 40, 160), (178, 150, 240)),
    "Purple":       ((130, 60, 100), (160, 255, 230)),
    "Lavender":     ((125, 20, 180), (150, 120, 255)),
    "Beige":        ((15, 20, 180), (30, 80, 230)),
    "Cream":        ((18, 15, 220), (35, 60, 255)),
    "Brown":        ((5, 60, 60), (20, 200, 180)),
    "Tan":          ((12, 40, 140), (25, 140, 210)),
}

class ColorDetector:
    def __init__(self):
        self.palette = COLOR_PALETTE

    def detect_color(self, html: str, image_path: str = None) -> str:
        """
        Detect color by first checking page text, then falling back to image analysis.
        """
        # 1. FIRST: Check page text for color mentions
        color_from_text = self._extract_color_from_text(html)
        if color_from_text:
            logger.info(f"Detected color from page text: {color_from_text}")
            return color_from_text
        
        # 2. FALLBACK: Analyze image if no color found in text
        if image_path:
            try:
                color_from_image = self._detect_color_from_image(image_path)
                if color_from_image:
                    logger.info(f"Detected color from image: {color_from_image}")
                    return color_from_image
            except Exception as e:
                logger.warning(f"Image color detection failed: {e}")
        
        return ""

    def _extract_color_from_text(self, html: str) -> str:
        """Extract color name from page text (variants, options, descriptions)."""
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True).lower()
        
        # Look for color in specific contexts
        color_patterns = [
            r'color[:\s]+(\w+)',
            r'colour[:\s]+(\w+)',
            r'select\s+color[:\s]+(\w+)',
            r'variant[:\s]+(\w+)',
            r'options?[:\s]+(\w+)',
            r'available\s+in[:\s]+(\w+)',
        ]
        
        # Check specific patterns first
        for pattern in color_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                color_word = match.group(1).lower()
                # Check if it's a valid color name
                if color_word in COLOR_NAMES:
                    return color_word.title()
        
        # Search for color names in the text
        for color in COLOR_NAMES:
            # Look for the color name as a whole word
            if re.search(rf'\b{color}\b', text, re.IGNORECASE):
                return color.title()
        
        return ""

    def _detect_color_from_image(self, image_path: str) -> str:
        """Analyze an image and return the dominant dress color name."""
        try:
            img = Image.open(image_path).convert("RGB")
            # Downsample for speed
            img = img.resize((100, 100))
            
            # Convert to HSV
            hsv_img = img.convert("HSV")
            hsv_pixels = np.array(hsv_img)
            
            h = hsv_pixels[:, :, 0]
            s = hsv_pixels[:, :, 1]
            v = hsv_pixels[:, :, 2]
            
            # Skin tone filter (PIL HSV H range is 0-255)
            skin_mask = (
                ((h < 35) | (h > 215)) &
                (s > 30) & (s < 140) &
                (v > 100) & (v < 235)
            )
            
            # Filter out very dark and very bright pixels
            brightness_mask = (v > 40) & (v < 240)
            saturation_mask = s > 20
            
            # Combine masks - exclude skin tones
            valid_mask = ~skin_mask & brightness_mask & saturation_mask
            
            valid_pixels = hsv_pixels[valid_mask]
            
            if len(valid_pixels) < 50:
                # Fallback: use all pixels
                valid_pixels = hsv_pixels.reshape(-1, 3)
            
            # Find dominant color by averaging
            avg_h = np.mean(valid_pixels[:, 0])
            avg_s = np.mean(valid_pixels[:, 1])
            avg_v = np.mean(valid_pixels[:, 2])
            
            # Map to named color
            return self._match_color(avg_h, avg_s, avg_v)
            
        except Exception as e:
            logger.warning(f"Color detection failed for {image_path}: {e}")
            return ""

    def _match_color(self, h, s, v) -> str:
        """Match HSV values to the closest named color."""
        # PIL HSV: H is 0-255 (scale from OpenCV's 0-180)
        # Convert PIL's H (0-255) to OpenCV's H (0-180) for our palette
        h_cv = (h / 255.0) * 180.0
        
        best_match = "Unknown"
        best_distance = float("inf")
        
        for name, (low, high) in self.palette.items():
            h_low, s_low, v_low = low
            h_high, s_high, v_high = high
            
            # Check if color falls in this range
            # Handle hue wrap-around for reds
            if h_low <= h_high:
                h_in_range = h_low <= h_cv <= h_high
            else:
                h_in_range = h_cv >= h_low or h_cv <= h_high
            
            if h_in_range and s_low <= s <= s_high and v_low <= v <= v_high:
                # Calculate distance to center of range
                h_center = (h_low + h_high) / 2
                s_center = (s_low + s_high) / 2
                v_center = (v_low + v_high) / 2
                distance = ((h_cv - h_center)**2 + (s - s_center)**2 + (v - v_center)**2) ** 0.5
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = name
        
        return best_match