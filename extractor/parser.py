"""
parser.py
Production orchestrator for ProductExtractor V3.
"""
import os
import logging
from .fetcher import WebFetcher
from .html_cleaner import HTMLCleaner
from .website_detector import WebsiteDetector
from .brand_detector import BrandDetector
from .title_parser import TitleParser
from .description_parser import DescriptionParser
from .price_parser import PriceParser
from .product_id import ProductIDExtractor
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
        self.product_id = ProductIDExtractor()
        
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
            
            if progress_callback:
                progress_callback(25, "Extracting metadata...")
            
            # 2. Extract metadata
            brand = self.brand_detector.detect(url)
            clean_text = self.cleaner.text(html)
            
            product = {
                "url": url,
                "website": self.website_detector.detect(url, html),
                "brand": brand,
                "product_id": self.product_id.extract(html, url),
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
            
            safe_brand = brand or "Unknown"
            pid = product["product_id"] or "no-id"
            
            processed_images = []
            if downloaded_files:
                processed_images = self.processor.process(
                    downloaded_files, 
                    self.output_dir, 
                    safe_brand, 
                    pid
                )

            product["images"] = processed_images

            if progress_callback:
                progress_callback(85, "Detecting dress color...")
            
            # 4. Detect color - FIRST from page text, then from image
            dress_color = ""
            if processed_images:
                dress_color = self.color_detector.detect_color(html, processed_images[0])
            else:
                dress_color = self.color_detector.detect_color(html)
            
            # 5. Build the display title: "Brand Color Fabric Suit"
            shirt_fabric = self.description_parser.get_shirt_fabric(clean_text)
            display_title = f"{brand} {dress_color} {shirt_fabric} Suit".strip()
            # Clean up double spaces
            display_title = " ".join(display_title.split())
            product["display_title"] = display_title
            product["dress_color"] = dress_color

            if progress_callback:
                progress_callback(95, "Saving files...")
            
            # 6. Save output using the new writer
            self.writer.save_product(product)
            
            if progress_callback:
                progress_callback(100, "Done!")
            
            logger.info("Finished %s", url)
            return product

        except Exception as exc:
            logger.exception("Parser failed for %s", url)
            raise ProductExtractorError(f"Failed to parse {url}: {str(exc)}") from exc