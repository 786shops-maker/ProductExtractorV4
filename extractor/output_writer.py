"""
output_writer.py
Writes extracted product data to disk with new structure:
downloads/
  2026-07-16_Afrozeh/
    Afrozeh-STONE.txt
    Afrozeh-STONE-z1.jpg
    Afrozeh-STONE-z2.jpg
"""
import shutil
from pathlib import Path
from datetime import datetime

class OutputWriter:
    def __init__(self, root_folder="downloads"):
        self.root = Path(root_folder)
        self.root.mkdir(parents=True, exist_ok=True)

    def safe_name(self, text):
        text = str(text)
        bad = '<>:"/|?*'
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
        Save a single product as a clean .txt file + images in the dated brand folder.
        NO sub-folders for each dress. NO HTML files.
        """
        brand = product.get("brand", "Unknown") or "Unknown"
        pid = product.get("product_id", "no-id") or "no-id"
        title = product.get("title", f"{brand} {pid} Suit")
        
        folder = self._brand_folder(brand)
        
        # Build the text file content
        price_info = product.get("price_info", {})
        price = str(price_info.get("price", "")).replace(",", "")
        sale_price = str(price_info.get("sale_price", "")).replace(",", "")
        
        # Determine final price and on-sale status
        if sale_price and sale_price != price:
            final_price = sale_price
            on_sale = "Yes"
        else:
            final_price = price
            on_sale = "No"
            
        price_str = f"{final_price} PKR" if final_price else "N/A"
        
        description = product.get("description", "")
        url = product.get("url", "")
        
        # Product ID format: Brandname-SKU/ID
        content = f"""Title: {title}
ProductID/SKU: {brand}-{pid}
Price: {price_str}
On Sale: {on_sale}

{description}

---------------------------
Product URL: {url}
"""
        
        # Save the text file
        txt_filename = folder / f"{self.safe_name(brand)}-{pid}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Copy images to the SAME brand folder (NO sub-folders)
        images = product.get("images", [])
        for idx, img_path in enumerate(images, 1):
            try:
                src = Path(img_path)
                if src.exists():
                    dest_name = f"{self.safe_name(brand)}-{pid}-z{idx}.jpg"
                    dest = folder / dest_name
                    shutil.copy2(src, dest)
            except Exception as e:
                pass
                
        return txt_filename

    # Deprecated methods kept as no-ops to prevent breaking changes
    def save_metadata(self, brand, pid, data):
        pass

    def save_description(self, brand, pid, text):
        pass

    def save_html(self, brand, pid, html):
        pass  # Explicitly disabled: No HTML files generated
