"""
Product Extractor V4
image_processor.py
Production Image Processing Engine
"""
from pathlib import Path
import hashlib
import cv2
import numpy as np
from PIL import Image

PRIMARY_WIDTH = 600
PRIMARY_HEIGHT = 960
SECONDARY_WIDTH = 500
SECONDARY_HEIGHT = 800
JPG_QUALITY = 95
CASCADE_FILE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

class ImageProcessor:
    def __init__(self):
        self.face_detector = cv2.CascadeClassifier(CASCADE_FILE)

    def load_image(self, filename):
        image = Image.open(filename)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

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
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            return None
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        return faces[0]

    def is_back_view(self, image):
        rgb = np.array(image)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(80, 80))
        return len(faces) == 0

    def get_chin_position(self, face):
        x, y, w, h = face
        return int(y + h * 0.85)

    def crop_below_chin(self, image):
        """Crop image to remove face/head, keeping the dress (chin area crop)."""
        width, height = image.size
        
        if self.is_back_view(image):
            crop_top = int(height * 0.05)
            return image.crop((0, crop_top, width, height))
        
        face = self.detect_face(image)
        if face is None:
            crop_top = int(height * 0.10)
            return image.crop((0, crop_top, width, height))
        
        chin_y = self.get_chin_position(face)
        crop_top = max(chin_y, int(height * 0.05))
        crop_top = min(crop_top, int(height * 0.15))
        
        return image.crop((0, crop_top, width, height))

    def resize_keep_ratio(self, image, target_width, target_height):
        src_w, src_h = image.width, image.height
        src_ratio, dst_ratio = src_w / src_h, target_width / target_height
        
        if src_ratio > dst_ratio:
            new_h, new_w = target_height, int(target_height * src_ratio)
        else:
            new_w, new_h = target_width, int(target_width / src_ratio)
            
        image = image.resize((new_w, new_h), Image.LANCZOS)
        left, top = (new_w - target_width) // 2, (new_h - target_height) // 2
        return image.crop((left, top, left + target_width, top + target_height))

    def best_resize(self, image):
        if image.width >= PRIMARY_WIDTH and image.height >= PRIMARY_HEIGHT:
            return self.resize_keep_ratio(image, PRIMARY_WIDTH, PRIMARY_HEIGHT)
        return self.resize_keep_ratio(image, SECONDARY_WIDTH, SECONDARY_HEIGHT)

    def process(self, image_files, output_folder, brand, product_id):
        safe_brand = str(brand).replace(" ", "-").replace("/", "-").replace("\\", "-")
        # FLAT temp folder to avoid sub-folders per dress
        temp_processed = Path(output_folder) / "temp_processed"
        temp_processed.mkdir(parents=True, exist_ok=True)
        
        image_files = self.remove_duplicate_files(image_files)
        processed = []
        count = 1
        for filename in image_files:
            try:
                image = self.load_image(filename)
                image = self.crop_below_chin(image)
                image = self.best_resize(image)
                outfile = temp_processed / f"{safe_brand}-{product_id}-z{count}.jpg"
                self.save_as_jpg(image, outfile)
                processed.append(str(outfile))
                count += 1
            except Exception as ex:
                print(f"Error processing {filename}: {ex}")
        return processed
