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
        try:
            logger.info("Starting parsing: %s", url)
            
            if progress_callback:
                progress_callback(10, "Fetching webpage...")
            
            # =================================================================
            # KEEP YOUR EXISTING HTML FETCHING AND DATA EXTRACTION LOGIC HERE
            # (Do not delete your BeautifulSoup extraction code)
            # =================================================================
            # ... (Your existing code to populate the 'product' dictionary) ...
            
            # Ensure we have the base values before formatting
            brand = product.get("brand", "UnknownBrand")
            sku = product.get("product_id", product.get("sku", "NoSKU"))
            
            # Format Product ID exactly as: Brandname-SKU/ID
            product["product_id"] = f"{brand}-{sku}"

            if progress_callback:
                progress_callback(80, "Processing images...")
            
            raw_images = product.get("raw_images", [])
            if raw_images:
                processed_images = self.image_processor.process(
                    raw_images, 
                    self.writer.root, 
                    brand, 
                    sku  # Pass original sku to image processor for clean naming
                )
                product["images"] = processed_images

            if progress_callback:
                progress_callback(95, "Saving files...")

            # 4. Save output using the new unified method (TXT only, flat structure, no HTML)
            self.writer.save_product(product)

            if progress_callback:
                progress_callback(100, "Done!")

            logger.info("Finished parsing: %s", url)
            return product

        except Exception as e:
            # This except block MUST be at the same indentation level as the 'try:' above
            logger.error("Error parsing %s: %s", url, str(e))
            if progress_callback:
                progress_callback(100, f"Error: {str(e)}")
            raise
