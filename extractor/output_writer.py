"""
output_writer.py
Writes extracted product data to disk with new structure:
  downloads/
    2026-07-16_Afrozeh/
      Afrozeh-STONE.txt
      Afrozeh-STONE-z1.jpg
"""
import json
from pathlib import Path
from datetime import datetime

class OutputWriter:
    def __init__(self, root_folder="downloads"):
        self.root = Path(root_folder)
        self.root.mkdir(parents=True, exist_ok=True)

    def safe_name(self, text):
        text = str(text)
        bad = '<>:"/\\|?*'
        for ch in bad:
            text = text.replace(ch, "-")
        text = text.replace(" ", "-")
        while "--" in text:
            text = text.replace("--", "-")
        return text.strip("-")

    def _brand_folder(self, brand):
        """Create folder with today's date + brand name."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_brand = self.safe_name(brand)
        folder_name = f"{date_str}_{safe_brand}"
        folder = self.root / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def save_product(self, product: dict):
        """
        Save a single product as a clean .txt file + images in the brand folder.
        """
        brand = product.get("brand", "Unknown") or "Unknown"
        pid = product.get("product_id", "no-id") or "no-id"
        title = product.get("display_title", f"{brand} {pid} Suit")
        
        folder = self._brand_folder(brand)
        
        # Build the text file content
        price_info = product.get("price_info", {})
        price = price_info.get("price", "")
        sale_price = price_info.get("sale_price", "")
        
        # Determine final price and on-sale status
        if sale_price and sale_price != price:
            final_price = sale_price
            on_sale = "Yes"
        else:
            final_price = price
            on_sale = "No"
        
        price_str = f"{final_price} PKR" if final_price else "N/A"
        
        # Build description - NO BOLD MARKERS
        description = product.get("description", "")
        
        url = product.get("url", "")
        
        content = f"""Title: {title}

ProductID/SKU: {brand}-{pid}

Price: {price_str}

On Sale: {on_sale}

{description}

-----------------------------
Product URL: {url}
"""
        
        # Save the text file
        txt_filename = folder / f"{self.safe_name(brand)}-{pid}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Move/copy images to the brand folder
        images = product.get("images", [])
        for idx, img_path in enumerate(images, 1):
            try:
                src = Path(img_path)
                if src.exists():
                    # Rename to brand-pid-zN.jpg format
                    dest_name = f"{self.safe_name(brand)}-{pid}-z{idx}.jpg"
                    dest = folder / dest_name
                    # Copy (don't move, in case we need the original)
                    import shutil
                    shutil.copy2(src, dest)
            except Exception as e:
                pass
        
        return txt_filename

    # Keep old methods for backward compatibility, but they now delegate
    def save_metadata(self, brand, pid, data):
        pass  # No longer saving metadata.json

    def save_description(self, brand, pid, text):
        pass  # Now handled by save_product

    def save_html(self, brand, pid, html):
        pass  # No longer saving source.html