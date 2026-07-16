"""
image_selector.py
Selects the best clothing/dress product images.
Aggressively filters out unrelated products like perfumes, accessories, etc.
"""
import re

class ImageSelector:
    def __init__(self):
        self.max_images = 5
        self.min_width = 400
        self.min_height = 500
        
        # Words that indicate NON-clothing products
        self.exclude_categories = [
            "perfume", "fragrance", "cologne", "parfum", "scent", "attar",
            "watch", "jewelry", "jewellery", "bracelet", "necklace", "ring", "earring",
            "shoe", "footwear", "bag", "purse", "wallet", "belt", "handbag",
            "cosmetic", "makeup", "lipstick", "foundation", "powder", "soap", "lotion"
        ]
        
        # Words that indicate good clothing images
        self.clothing_keywords = [
            "dress", "suit", "shirt", "trouser", "pants", "shalwar", "kameez",
            "unstitched", "3-piece", "2-piece", "fabric", "lawn", "chiffon",
            "embroidered", "printed", "sleeve", "front", "back", "model-wearing",
            "kurti", "tunic", "abaya", "hijab", "scarf"
        ]

    def score(self, image):
        score = 0
        width = image.get("width", 0)
        height = image.get("height", 0)
        url = image["url"].lower()
        alt = image.get("alt", "").lower()
        combined = url + " " + alt
        
        # Base score from dimensions
        score += width * height
        
        # Strong preference for portrait images (clothing shots)
        if height > width:
            ratio = height / width
            if 1.2 <= ratio <= 2.5:
                score += 500000
            elif ratio > 2.5:
                score += 300000
        
        # Boost clothing-related keywords
        for word in self.clothing_keywords:
            if word in combined:
                score += 200000
        
        # Prefer high-resolution images
        if width >= 1000 and height >= 1200:
            score += 300000
        elif width >= 600 and height >= 800:
            score += 100000
            
        return score

    def is_clothing_image(self, image):
        """Strictly determine if an image is a clothing/dress image."""
        url = image["url"].lower()
        alt = image.get("alt", "").lower()
        combined = url + " " + alt
        
        # 1. Immediate rejection for excluded categories
        for word in self.exclude_categories:
            if word in combined:
                return False
                
        # 2. Immediate rejection for related product URLs
        if any(word in url for word in ["related", "recommend", "cross-sell", "upsell", "you-may-also-like"]):
            return False
        
        # 3. Accept if it has explicit clothing keywords
        for word in self.clothing_keywords:
            if word in combined:
                return True
        
        # 4. Fallback: If it's a high-quality portrait image and NOT excluded, assume it's clothing
        width = image.get("width", 0)
        height = image.get("height", 0)
        if width >= 400 and height >= 500 and (height / width) > 1.2:
            return True
        
        return False

    def remove_duplicates(self, images):
        output = []
        seen = set()
        for img in images:
            base_url = img["url"].split("?")[0]
            if base_url in seen:
                continue
            seen.add(base_url)
            output.append(img)
        return output

    def remove_small(self, images):
        return [img for img in images if img.get("width", 0) >= self.min_width and img.get("height", 0) >= self.min_height]

    def filter_clothing_only(self, images):
        return [img for img in images if self.is_clothing_image(img)]

    def select(self, images):
        if not images:
            return []
        
        # Step 1: Remove duplicates
        images = self.remove_duplicates(images)
        
        # Step 2: Remove too-small images
        images = self.remove_small(images)
        if not images:
            return []
        
        # Step 3: CRITICAL - Filter out non-clothing items
        images = self.filter_clothing_only(images)
        if not images:
            return []
        
        # Step 4: Sort by score and return top images
        images.sort(key=self.score, reverse=True)
        return images[:self.max_images]