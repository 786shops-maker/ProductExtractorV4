"""
image_finder.py
Locate high-quality product images from an HTML page.
STRICTLY targets main product galleries and ignores related/recommended items.
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class ImageFinder:
    # Words that indicate NON-clothing products
    EXCLUDE_CATEGORIES = (
        "perfume", "fragrance", "cologne", "parfum", "scent", "attar",
        "watch", "jewelry", "jewellery", "bracelet", "necklace", "ring",
        "shoe", "footwear", "bag", "purse", "wallet", "belt", "handbag",
        "cosmetic", "makeup", "lipstick", "foundation", "powder"
    )

    # Words that indicate UI/irrelevant images
    IGNORE_WORDS = (
        "logo", "icon", "sprite", "banner", "payment", "facebook",
        "instagram", "twitter", "youtube", "pinterest", "whatsapp",
        "share", "cart", "menu", "nav", "footer", "header", "thumb",
        "avatar", "profile", "user", "search", "close", "arrow",
        "loading", "spinner", "placeholder"
    )

    # Selectors for MAIN product galleries (ignores related products)
    GALLERY_SELECTORS = (
        ".product__media", ".product-gallery", ".product-images",
        ".product-media-gallery", ".main-product-image", ".product-detail-images",
        "[data-product-gallery]", "[data-product-images]",
        ".woocommerce-product-gallery", ".product-big-img",
        ".product-slider", ".product-carousel", ".zoomContainer",
        ".product-media", ".product-form__media"
    )

    # Selectors for RELATED/RECOMMENDED products (to explicitly IGNORE)
    RELATED_SELECTORS = (
        ".product-recommendations", ".related-products", ".cross-sell",
        ".upsell-products", ".you-may-also-like", ".recently-viewed",
        ".recommended-products", ".similar-products"
    )

    def find(self, html: str, page_url: str):
        soup = BeautifulSoup(html, "lxml")
        found = []

        # 1. First, try to find OpenGraph image (usually the main product)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            src = urljoin(page_url, og_image["content"])
            if not self._is_excluded(src, ""):
                found.append({"url": src, "width": 1200, "height": 1200, "score": 1000000})

        # 2. STRICTLY search ONLY inside main product gallery containers
        gallery_found = False
        for selector in self.GALLERY_SELECTORS:
            galleries = soup.select(selector)
            for gallery in galleries:
                # Ensure this gallery is NOT inside a related products section
                if any(gallery.find_parent(sel) for sel in self.RELATED_SELECTORS):
                    continue
                
                gallery_found = True
                for img in gallery.find_all("img"):
                    img_data = self._extract_image_data(img, page_url)
                    if img_data and not self._is_excluded(img_data["url"], img_data.get("alt", "")):
                        img_data["score"] += 500000  # Massive boost for main gallery
                        found.append(img_data)

        # 3. If NO gallery found, fall back to JSON-LD (structured data)
        if not gallery_found:
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
                                if not self._is_excluded(full_url, ""):
                                    found.append({"url": full_url, "width": 1200, "height": 1200, "score": 900000})
                except:
                    pass

        # 4. CRITICAL: Do NOT fall back to soup.find_all("img") as it grabs related products.
        # If we only have OG or JSON-LD, that's safer than grabbing random page images.

        # Remove duplicates
        unique = {}
        for item in found:
            unique[item["url"]] = item
        
        images = list(unique.values())
        images.sort(key=lambda x: x["score"], reverse=True)
        
        return images[:10]

    def _extract_image_data(self, img, page_url):
        src = (
            img.get("data-zoom") or img.get("data-large") or img.get("data-original") or
            img.get("data-srcset") or img.get("data-src") or img.get("src")
        )
        if not src:
            return None
        
        if "data-srcset" in img.attrs or "srcset" in img.attrs:
            srcset = img.get("data-srcset") or img.get("srcset")
            src = self._get_largest_from_srcset(srcset, page_url) or src

        src = urljoin(page_url, src)
        alt_text = (img.get("alt") or "").lower()
        width = self._to_int(img.get("width"))
        height = self._to_int(img.get("height"))
        
        score = (width or 800) * (height or 1000)
        if height and width and (height / width) > 1.2:
            score += 400000  # Boost portrait images
            
        return {"url": src, "width": width or 800, "height": height or 1000, "score": score, "alt": alt_text}

    def _is_excluded(self, url, alt_text):
        combined = (url + " " + alt_text).lower()
        if any(word in combined for word in self.EXCLUDE_CATEGORIES):
            return True
        if any(word in url.lower() for word in self.IGNORE_WORDS):
            return True
        if any(word in url.lower() for word in ["related", "recommend", "cross-sell", "upsell"]):
            return True
        if any(ext in url.lower() for ext in [".svg", ".gif"]):
            return True
        return False

    def _get_largest_from_srcset(self, srcset, base_url):
        if not srcset:
            return None
        try:
            candidates = srcset.split(",")
            largest = None
            max_width = 0
            for candidate in candidates:
                parts = candidate.strip().split()
                if len(parts) >= 2:
                    width_match = re.search(r'(\d+)w', parts[1])
                    if width_match:
                        width = int(width_match.group(1))
                        if width > max_width:
                            max_width = width
                            largest = parts[0]
            return urljoin(base_url, largest) if largest else None
        except:
            return None

    def _to_int(self, value):
        try:
            return int(str(value).replace("px", ""))
        except Exception:
            return 0