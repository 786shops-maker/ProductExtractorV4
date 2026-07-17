"""
parser.py
Production orchestrator for ProductExtractor V4.
"""
import os
import logging
import re
import json
from bs4 import BeautifulSoup
from .fetcher import WebFetcher
from .html_cleaner import HTMLCleaner
from .website_detector import WebsiteDetector
from .brand_detector import BrandDetector
from .title_parser import TitleParser
from .description_parser import DescriptionParser
from .price_parser import PriceParser
from .image_finder import ImageFinder
from .image_selector import ImageSelector
from .image_downloader import ImageDownloader
from .image_processor import ImageProcessor
from .color_detector import ColorDetector
from .output_writer import OutputWriter
from .exceptions import ProductExtractorError

logger = logging.getLogger("ProductExtractor")

class Parser:
    def __init__(self, output_dir="downloads"):
        self.fetcher = WebFetcher()
        self.cleaner = HTMLCleaner()
        self.website_detector = WebsiteDetector()
        self.brand_detector = BrandDetector()
        self.title_parser = TitleParser()
        self.description_parser = DescriptionParser()
        self.price_parser = PriceParser()

        # Image pipeline
        self.image_finder = ImageFinder()
        self.image_selector = ImageSelector()
        self.downloader = ImageDownloader()
        self.processor = ImageProcessor()
        self.color_detector = ColorDetector()

        self.writer = OutputWriter(root_folder=output_dir)
        self.output_dir = output_dir

    def parse(self, url: str, progress_callback=None):
        logger.info("Processing %s", url)
        try:
            if progress_callback:
                progress_callback(10, "Fetching page...")

            # 1. Fetch raw HTML
            html = self.fetcher.download(url)
            soup = BeautifulSoup(html, 'html.parser')

            if progress_callback:
                progress_callback(25, "Extracting metadata...")

            # 2. Extract metadata
            brand = self.brand_detector.detect(url) or "Unknown"
            clean_text = self.cleaner.text(html)
            
            # ==========================================
            # SMART SKU EXTRACTION (Prioritizes reliable sources)
            # ==========================================
            raw_sku = None
            
            # Step 1: Look in JSON-LD (Structured Data) - Most reliable
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'sku' in data and data['sku']:
                        raw_sku = str(data['sku']).strip().upper()
                        break
                    elif isinstance(data, list):
                        for item in data:
                            if 'sku' in item and item['sku']:
                                raw_sku = str(item['sku']).strip().upper()
                                break
                        if raw_sku: break
                except Exception:
                    pass

            # Step 2: Look in Meta Tags
            if not raw_sku:
                meta_sku = soup.find('meta', property='product:retailer_item_id') or \
                           soup.find('meta', property='og:sku') or \
                           soup.find('meta', attrs={'name': 'sku'})
                if meta_sku and meta_sku.get('content'):
                    raw_sku = str(meta_sku['content']).strip().upper()

            # Step 3: Extract from URL slug (Highly reliable for fashion brands like Alkaram)
            # We do this BEFORE broad HTML regex to avoid false positives like "CLASS"
            if not raw_sku:
                slug = url.rstrip('/').split('/')[-1]
                parts = slug.split('-')
                if len(parts) >= 3:
                    # Heuristic: if the 3rd to last part has letters and numbers (like ec338 or 3p26)
                    third_to_last = parts[-3]
                    if re.search(r'[A-Za-z].*\d|\d.*[A-Za-z]', third_to_last) or len(third_to_last) >= 5:
                        raw_sku = "-".join(parts[-3:]).upper()
                    else:
                        raw_sku = "-".join(parts[-3:]).upper() # Fallback to last 3 anyway
                else:
                    raw_sku = slug.upper()

            # Step 4: Broad HTML regex fallback (Only if URL didn't yield a good result)
            if not raw_sku or len(raw_sku) < 5:
                patterns = [
                    r'(?:style\s*code|article\s*number|style\s*no)\s*[:\-]?\s*([A-Z0-9\-]{4,20})',
                    r'["\']sku["\']\s*:\s*["\']([A-Z0-9\-]{4,20})["\']'
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        raw_sku = match.group(1).strip().upper()
                        break

            # ==========================================
            # CLEAN THE EXTRACTED SKU
            # ==========================================
            clean_sku = raw_sku.replace(brand, "").strip("-").upper()
            
            # Remove generic words that pollute the SKU
            generic_words = [
                "RTS", "SHIRT", "TROUSER", "DUPATTA", "PRODUCTS", "PRODUCT", 
                "THE", "SUIT", "LAWN", "COTTON", "DIGITAL", "UNSTITCHED", 
                "CLASS", "CATEGORY", "TYPE", "COLLECTION", "NEW", "ARRIVAL"
            ]
            for word in generic_words:
                clean_sku = clean_sku.replace(word, "").strip("-")
                
            # If after cleaning it's empty, too short, or still generic, force URL extraction
            if len(clean_sku) < 5 or clean_sku in ["NO-ID", ""]:
                slug = url.rstrip('/').split('/')[-1]
                parts = slug.split('-')
                if len(parts) >= 3:
                    clean_sku = "-".join(parts[-3:]).upper()
                else:
                    clean_sku = slug.upper()
                    
            # Enforce Product ID format: Brandname-SKU/ID
            formatted_pid = f"{brand}-{clean_sku}"

            product = {
                "url": url,
                "website": self.website_detector.detect(url, html),
                "brand": brand,
                "product_id": formatted_pid,
                "title": self.title_parser.parse(html),
                "description": self.description_parser.final_description(clean_text, brand),
                "price_info": self.price_parser.parse(html),
            }

            if progress_callback:
                progress_callback(40, "Finding images...")

            # 3. Extract and process images
            images = self.image_finder.find(html, url)
            selected_images = self.image_selector.select(images)

            if progress_callback:
                progress_callback(55, "Downloading images...")

            temp_img_dir = os.path.join(self.output_dir, "temp_images")
            downloaded_files = self.downloader.download_images(selected_images, temp_img_dir)

            if progress_callback:
                progress_callback(70, "Processing images...")

            processed_images = []
            if downloaded_files:
                processed_images = self.processor.process(
                    downloaded_files,
                    self.output_dir,
                    brand,
                    clean_sku  # Pass clean_sku for cleaner image filenames
                )

            product["images"] = processed_images

            if progress_callback:
                progress_callback(85, "Detecting dress color...")

            # 4. Detect color - FIRST from page text/image
            dress_color = self.color_detector.detect_color(html, processed_images[0] if processed_images else None)
            
            # Fallback: if color detector fails, try to extract from URL slug (e.g., "-peach")
            if not dress_color:
                slug = url.rstrip('/').split('/')[-1]
                parts = slug.split('-')
                if len(parts) >= 3:
                    potential_color = parts[-1].capitalize()
                    if not potential_color.isdigit() and len(potential_color) > 2:
                        dress_color = potential_color

            # 5. Build the display title: "Brand Color Fabric Suit"
            shirt_fabric = self.description_parser.get_shirt_fabric(clean_text)
            display_title = f"{brand} {dress_color} {shirt_fabric} Suit".strip()
            # Clean up double spaces
            display_title = " ".join(display_title.split())
            
            product["display_title"] = display_title
            product["dress_color"] = dress_color

            if progress_callback:
                progress_callback(95, "Saving files...")

            # 6. Save output using the new writer (TXT only, flat structure, no HTML)
            self.writer.save_product(product)

            if progress_callback:
                progress_callback(100, "Done!")

            logger.info("Finished %s", url)
            return product

        except Exception as exc:
            logger.exception("Parser failed for %s", url)
            raise ProductExtractorError(f"Failed to parse {url}: {str(exc)}") from exc
