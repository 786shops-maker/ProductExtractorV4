"""
image_downloader.py
Download product images for later processing.
Prioritizes high-quality versions.
"""
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests
import re

class ImageDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        })

    def download_images(self, images, output_folder, limit=5):
        output = Path(output_folder)
        output.mkdir(parents=True, exist_ok=True)
        downloaded = []
        
        for index, image in enumerate(images[:limit], start=1):
            url = image["url"] if isinstance(image, dict) else str(image)
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if it's actually an image
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print(f"Skipping non-image: {url}")
                    continue
                
                ext = self._extension(url, content_type)
                filename = output / f"image_{index}{ext}"
                
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                downloaded.append(str(filename))
                
            except Exception as ex:
                print(f"Failed to download: {url}")
                print(f"Error: {ex}")
        
        return downloaded

    def _extension(self, url, content_type=""):
        """Determine file extension from URL or content type."""
        # First try content type
        if "image/png" in content_type:
            return ".png"
        if "image/webp" in content_type:
            return ".webp"
        if "image/jpeg" in content_type or "image/jpg" in content_type:
            return ".jpg"
        
        # Fallback to URL
        path = urlparse(url).path.lower()
        path = unquote(path)  # Decode URL-encoded characters
        
        if path.endswith(".png"):
            return ".png"
        if path.endswith(".webp"):
            return ".webp"
        if path.endswith(".jpeg") or path.endswith(".jpg"):
            return ".jpg"
        if path.endswith(".gif"):
            return ".gif"
        
        # Default to jpg
        return ".jpg"