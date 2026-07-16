"""
Product Extractor V2
image_processor.py
Production Image Processing Engine
"""
from pathlib import Path
from typing import List
import hashlib
import cv2
import numpy as np
from PIL import Image

# ----------------------------------------
# Output Sizes
# ----------------------------------------
PRIMARY_WIDTH = 600
PRIMARY_HEIGHT = 960
SECONDARY_WIDTH = 500
SECONDARY_HEIGHT = 800

# ----------------------------------------
# JPG Quality
# ----------------------------------------
JPG_QUALITY = 95

# ----------------------------------------
# Face Detection
# ----------------------------------------
CASCADE_FILE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

class ImageProcessor:
    def __init__(self):
        self.face_detector = cv2.CascadeClassifier(CASCADE_FILE)
    
    def load_image(self, filename):
        image = Image.open(filename)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    
    def image_size(self, image):
        return image.width, image.height
    
    def is_large_enough(self, image):
        w, h = self.image_size(image)
        if w >= PRIMARY_WIDTH and h >= PRIMARY_HEIGHT:
            return True
        if w >= SECONDARY_WIDTH and h >= SECONDARY_HEIGHT:
            return True
        return False
    
    def file_hash(self, filename):
        h = hashlib.md5()
        with open(filename, "rb") as f:
            while True:
                block = f.read(65536)
                if not block:
                    break
                h.update(block)
        return h.hexdigest()
    
    def remove_duplicate_files(self, files):
        seen = {}
        output = []
        for file in files:
            try:
                md5 = self.file_hash(file)
            except Exception:
                continue
            if md5 in seen:
                continue
            seen[md5] = True
            output.append(file)
        return output
    
    def save_as_jpg(self, image, filename):
        image.save(filename, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True)
    
    def detect_face(self, image):
        rgb = np.array(image)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(60, 60))
        if len(faces) == 0:
            return None
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        return faces[0]
    
    def chin_y(self, face):
        x, y, w, h = face
        return int(y + h * 0.90)
    
    def is_likely_back_view(self, image):
        rgb = np.array(image)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(80, 80))
        if len(faces) == 0:
            return True
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        face_area = largest_face[2] * largest_face[3]
        image_area = image.width * image.height
        if face_area < (image_area * 0.015):
            return True
        return False

    def crop_below_chin(self, image):
        if self.is_likely_back_view(image):
            return self.smart_crop_back_view(image)
        
        face = self.detect_face(image)
        if face is None:
            return self.smart_crop(image)
        
        crop_top = self.chin_y(face)
        width = image.width
        height = image.height
        
        if crop_top > height * 0.45:
            return self.smart_crop(image)
        
        crop_top = max(crop_top, int(height * 0.12))
        crop_top = min(crop_top, int(height * 0.35))
        
        return image.crop((0, crop_top, width, height))
    
    def smart_crop_back_view(self, image):
        width = image.width
        height = image.height
        crop_top = int(height * 0.08)
        return image.crop((0, crop_top, width, height))
    
    def smart_crop(self, image):
        width = image.width
        height = image.height
        crop_top = int(height * 0.18)
        return image.crop((0, crop_top, width, height))
    
    def resize_keep_ratio(self, image, target_width, target_height):
        src_w = image.width
        src_h = image.height
        src_ratio = src_w / src_h
        dst_ratio = target_width / target_height
        
        if src_ratio > dst_ratio:
            new_h = target_height
            new_w = int(new_h * src_ratio)
        else:
            new_w = target_width
            new_h = int(new_w / src_ratio)
        
        image = image.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_width) // 2
        top = (new_h - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return image.crop((left, top, right, bottom))
    
    def resize_primary(self, image):
        return self.resize_keep_ratio(image, PRIMARY_WIDTH, PRIMARY_HEIGHT)
    
    def resize_secondary(self, image):
        return self.resize_keep_ratio(image, SECONDARY_WIDTH, SECONDARY_HEIGHT)
    
    def best_resize(self, image):
        w = image.width
        h = image.height
        if w >= PRIMARY_WIDTH and h >= PRIMARY_HEIGHT:
            return self.resize_primary(image)
        return self.resize_secondary(image)
    
    def process(self, image_files, output_folder, brand, product_id):
        safe_brand = str(brand).replace(" ", "-").replace("/", "-").replace("\\", "-")
        output_path = Path(output_folder) / safe_brand / f"{safe_brand}-{product_id}"
        output_path.mkdir(parents=True, exist_ok=True)
        
        image_files = self.remove_duplicate_files(image_files)
        processed = []
        count = 1
        
        for filename in image_files:
            try:
                image = self.load_image(filename)
                image = self.crop_below_chin(image)
                image = self.best_resize(image)
                outfile = output_path / f"{safe_brand}-{product_id}-z{count}.jpg"
                self.save_as_jpg(image, outfile)
                processed.append(str(outfile))
                count += 1
            except Exception as ex:
                print(f"Error processing {filename}: {ex}")
        
        return processed