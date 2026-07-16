from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = BASE_DIR / "downloads"
LOG_FOLDER = BASE_DIR / "logs"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

MAX_IMAGES = 5
IMAGE_SIZES = [(600, 960), (500, 800), (400, 640), (300, 480)]
JPEG_QUALITY = 95
REMOVE_FACE = True

# Fixed the space in REQUEST_TIMEOUT
REQUEST_TIMEOUT = 25 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

LOG_FILE = LOG_FOLDER / "product_extractor.log"
PROFILE_FOLDER = BASE_DIR / "profiles"
PROFILE_FOLDER.mkdir(exist_ok=True)