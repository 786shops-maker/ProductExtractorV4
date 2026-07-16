"""
parser.py
Production orchestrator for ProductExtractor.
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
        
        # Image pipeline components
        self.image_finder = ImageFinder()
        self.image_selector = ImageSelector()
        self.downloader = ImageDownloader()
        self.processor = ImageProcessor()
        
        self.writer = OutputWriter(root_folder=output_dir)
        self.output_dir = output_dir

    def parse(self, url: str, progress_callback=None):
        logger.info("Processing %s", url)
        try:
            if progress_callback:
                progress_callback(10, "Fetching page...")
                
            # 1. Fetch raw HTML (this is a string)
            html = self.fetcher.download(url)
            
            if progress_callback:
                progress_callback(30, "Extracting metadata...")
            
            # 2. Extract metadata
            brand = self.brand_detector.detect(url)
            
            # Get clean text specifically for the description parser
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
                progress_callback(50, "Finding and downloading images...")

            # 3. Extract and process images
            processed_images = []
            try:
                images = self.image_finder.find(html, url) or []
                selected_images = self.image_selector.select(images) or []
                
                temp_img_dir = os.path.join(self.output_dir, "temp_images")
                downloaded_files = self.downloader.download_images(selected_images, temp_img_dir)
                
                safe_brand = brand or "Unknown"
                pid = product["product_id"] or "no-id"
                
                if downloaded_files:
                    if progress_callback:
                        progress_callback(80, "Processing images...")
                    processed_images = self.processor.process(
                        downloaded_files, 
                        self.output_dir, 
                        safe_brand, 
                        pid
                    )
            except Exception as img_pipeline_err:
                logger.warning(f"Image pipeline skipped: {img_pipeline_err}")

            product["images"] = processed_images

            if progress_callback:
                progress_callback(95, "Saving files...")

            # 4. Save output
            safe_brand = brand or "Unknown"
            pid = product["product_id"] or "no-id"
            self.writer.save_metadata(safe_brand, pid, product)
            self.writer.save_description(safe_brand, pid, product["description"])
            self.writer.save_html(safe_brand, pid, html)
            
            if progress_callback:
                progress_callback(100, "Done!")
                
            logger.info("Finished %s", url)
            return product

        except Exception as exc:
            logger.exception("Parser failed for %s", url)
            raise ProductExtractorError(f"Failed to parse {url}: {str(exc)}") from exc
