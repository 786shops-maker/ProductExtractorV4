"""
image_finder.py
Locate high-quality product images from an HTML page.
Prioritizes main product images over related products and accessories.
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class ImageFinder:
    MIN_WIDTH = 400
    MIN_HEIGHT = 500
    
    # Words that indicate NON-clothing products (perfumes, accessories, etc.)
    EXCLUDE_CATEGORIES = (
        "perfume", "fragrance", "cologne", "parfum", "scent", "attar",
        "watch", "jewelry", "jewellery", "bracelet", "necklace", "ring",
        "shoe", "footwear", "bag", "purse", "wallet", "belt",
        "cosmetic", "makeup", "lipstick", "foundation"
    )
    
    # Words that indicate UI/irrelevant images
    IGNORE_WORDS = (
        "logo", "icon", "sprite", "banner", "payment", "facebook", 
        "instagram", "twitter", "youtube", "pinterest", "whatsapp",
        "share", "cart", "menu", "nav", "footer", "header", "thumb",
        "avatar", "profile", "user", "search", "close", "arrow",
        "loading", "spinner", "placeholder"
    )
    
    # Words that indicate GOOD product gallery images
    PREFER_WORDS = (
        "product", "detail", "zoom", "main", "gallery", "image",
        "front", "back", "side", "flat", "lay", "model-wearing",
        " unstitched", "3-piece", "suit", "dress", "shirt", "trouser"
    )

    def find(self, html: str, page_url: str):
        soup = BeautifulSoup(html, "lxml")
        found = []
        
        # 1. First, try to find OpenGraph images (usually the main product)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            src = urljoin(page_url, og_image["content"])
            if not self._is_excluded_category(src, ""):
                found.append({
                    "url": src,
                    "width": 1200,
                    "height": 1200,
                    "score": 1000000,
                    "is_main": True
                })
        
        # 2. Find images in product-specific containers ONLY
        # Look for common product gallery selectors
        gallery_selectors = [
            ".product-gallery", ".product-media", ".product-images",
            ".product__media", ".product__gallery", ".product-detail-images",
            "[data-product-gallery]", "[data-product-images]",
            ".woocommerce-product-gallery", ".product-big-img",
            ".product-slider", ".product-carousel", ".zoomContainer"
        ]
        
        # First, prioritize images inside product galleries
        for selector in gallery_selectors:
            gallery = soup.select(selector)
            for container in gallery:
                for img in container.find_all("img"):
                    img_data = self._extract_image_data(img, page_url)
                    if img_data and not self._is_excluded_category(img_data["url"], img_data.get("alt", "")):
                        img_data["score"] += 500000  # Boost gallery images
                        found.append(img_data)
        
        # 3. Find all other img tags (but be more selective)
        for img in soup.find_all("img"):
            # Skip if already found in gallery
            src = img.get("src") or img.get("data-src") or ""
            if any(f["url"] == urljoin(page_url, src) for f in found):
                continue
            
            img_data = self._extract_image_data(img, page_url)
            if img_data and not self._is_excluded_category(img_data["url"], img_data.get("alt", "")):
                found.append(img_data)
        
        # 4. Look for images in JSON-LD structured data
        script_tags = soup.find_all("script", type="application/ld+json")
        for script in script_tags:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and "image" in data:
                    images = data["image"] if isinstance(data["image"], list) else [data["image"]]
                    for img_url in images:
                        if isinstance(img_url, str):
                            full_url = urljoin(page_url, img_url)
                            if not self._is_excluded_category(full_url, ""):
                                found.append({
                                    "url": full_url,
                                    "width": 1200,
                                    "height": 1200,
                                    "score": 900000,
                                    "is_structured": True
                                })
            except:
                pass
        
        # Remove duplicates
        unique = {}
        for item in found:
            unique[item["url"]] = item
        
        images = list(unique.values())
        images.sort(key=lambda x: x["score"], reverse=True)
        
        return images[:10]

    def _extract_image_data(self, img, page_url):
        """Extract image URL and metadata from an img tag."""
        # Try multiple source attributes in priority order
        src = (
            img.get("data-zoom") or
            img.get("data-large") or
            img.get("data-original") or
            img.get("data-srcset") or
            img.get("data-src") or
            img.get("src")
        )
        
        if not src:
            return None
        
        # Handle srcset - get the largest image
        if "data-srcset" in img.attrs or "srcset" in img.attrs:
            srcset = img.get("data-srcset") or img.get("srcset")
            src = self._get_largest_from_srcset(srcset, page_url) or src
        
        src = urljoin(page_url, src)
        alt_text = (img.get("alt") or "").lower()
        
        # Get dimensions
        width = self._to_int(img.get("width"))
        height = self._to_int(img.get("height"))
        
        # Calculate score
        score = self._calculate_score(src, width, height, alt_text, img)
        
        return {
            "url": src,
            "width": width or 800,
            "height": height or 1000,
            "score": score,
            "alt": alt_text
        }

    def _is_excluded_category(self, url, alt_text):
        """Check if image belongs to excluded categories (perfume, accessories, etc.)."""
        url_lower = url.lower()
        alt_lower = alt_text.lower()
        combined = url_lower + " " + alt_lower
        
        # Check for excluded product categories
        if any(word in combined for word in self.EXCLUDE_CATEGORIES):
            return True
        
        # Check for UI/irrelevant images
        if any(word in url_lower for word in self.IGNORE_WORDS):
            return True
        
        # Skip SVGs and tiny icons
        if any(ext in url_lower for ext in [".svg", ".gif"]):
            return True
        
        return False

    def _get_largest_from_srcset(self, srcset, base_url):
        """Extract the largest image from srcset attribute."""
        if not srcset:
            return None
        
        try:
            candidates = srcset.split(",")
            largest = None
            max_width = 0
            
            for candidate in candidates:
                parts = candidate.strip().split()
                if len(parts) >= 2:
                    url = parts[0]
                    width_match = re.search(r'(\d+)w', parts[1])
                    if width_match:
                        width = int(width_match.group(1))
                        if width > max_width:
                            max_width = width
                            largest = url
            
            return urljoin(base_url, largest) if largest else None
        except:
            return None

    def _calculate_score(self, src, width, height, alt_text, img_tag):
        """Calculate a score for image quality and relevance."""
        score = 0
        src_lower = src.lower()
        
        # Base score from dimensions
        score += (width or 800) * (height or 1000)
        
        # Boost for portrait images (clothing/product shots)
        if height and width:
            ratio = height / width
            if 1.2 <= ratio <= 2.5:  # Ideal clothing photo ratio
                score += 400000
            elif ratio > 2.5:  # Very tall, might be model shot
                score += 200000
        
        # Boost for high-resolution images
        if (width or 0) >= 1000 and (height or 0) >= 1200:
            score += 200000
        
        # Check for quality indicators in URL
        if any(word in src_lower for word in ["large", "zoom", "original", "high-res", "hd"]):
            score += 150000
        
        # Prefer product detail images
        if any(word in src_lower for word in self.PREFER_WORDS):
            score += 100000
        
        # Check alt text for clothing keywords
        clothing_keywords = ["dress", "suit", "shirt", "trouser", "fabric", "unstitched", "3-piece"]
        if any(word in alt_text for word in clothing_keywords):
            score += 150000
        
        # Check if it's in a product gallery container
        parent_classes = " ".join(img_tag.parent.get("class", []))
        if any(word in parent_classes.lower() for word in ["product", "gallery", "zoom", "media"]):
            score += 200000
        
        return score

    def _to_int(self, value):
        try:
            return int(str(value).replace("px", ""))
        except Exception:
            return 0