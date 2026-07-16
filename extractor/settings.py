"""
settings.py - Central configuration for ProductExtractorV3
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Settings:
    APP_NAME = "ProductExtractorV3"
    VERSION = "1.0.0"

    # Directories
    OUTPUT_DIR = BASE_DIR / "output"
    DOWNLOAD_DIR = OUTPUT_DIR / "downloads"
    PROCESSED_DIR = OUTPUT_DIR / "processed"
    LOG_DIR = BASE_DIR / "logs"
    TEMP_DIR = BASE_DIR / "temp"

    # Network
    REQUEST_TIMEOUT = 30
    RETRY_COUNT = 3
    RETRY_DELAY = 2
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )

    # Images
    IMAGE_FORMAT = "jpg"
    JPEG_QUALITY = 95
    MAX_IMAGE_WIDTH = 2000
    MAX_IMAGE_HEIGHT = 2000
    MIN_IMAGE_WIDTH = 400
    MIN_IMAGE_HEIGHT = 400

    # Processing
    MAX_WORKERS = 8
    ENABLE_HASH_CHECK = True
    ENABLE_IMAGE_OPTIMIZATION = True

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = LOG_DIR / "extractor.log"
    ERROR_LOG_FILE = LOG_DIR / "errors.log"

    @classmethod
    def ensure_directories(cls):
        for d in (
            cls.OUTPUT_DIR,
            cls.DOWNLOAD_DIR,
            cls.PROCESSED_DIR,
            cls.LOG_DIR,
            cls.TEMP_DIR,
        ):
            d.mkdir(parents=True, exist_ok=True)
