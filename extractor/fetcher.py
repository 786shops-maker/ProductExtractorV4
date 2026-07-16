"""
Product Extractor V2 - fetcher.py
"""
from pathlib import Path
import time
import requests
from bs4 import BeautifulSoup
from config import HEADERS, REQUEST_TIMEOUT, DOWNLOAD_FOLDER

class WebFetcher:
    def __init__(self):  # FIXED: Added underscores
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def download(self, url, retries=3):
        err = None
        for _ in range(retries):
            try:
                r = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                r.raise_for_status()
                self.save_html(url, r.text)
                return r.text
            except Exception as ex:
                err = ex
                time.sleep(2)
        raise Exception(f"Unable to download page: {err}")

    def soup(self, url):
        return BeautifulSoup(self.download(url), "lxml")

    def save_html(self, url, html):
        name = (url.replace("https://", "").replace("http://", "")
                .replace("/", "_").replace("?", "_")
                .replace("&", "_").replace("=", "_"))
        Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)
        file = Path(DOWNLOAD_FOLDER) / (name + ".html")
        file.write_text(html, encoding="utf-8")
        return file