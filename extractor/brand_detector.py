"""
brand_detector.py
Detect brand from domain with easy-to-edit mappings.
"""
from urllib.parse import urlparse

class BrandDetector:
    BRAND_MAP = {
        "sapphireonline.pk": "Sapphire",
        "asimjofa.com": "Asim Jofa",
        "mariab.pk": "Maria B",
        "baroque.pk": "Baroque",
        "zellbury.com": "Zellbury",
        "khaadi.com": "Khaadi",
        "limelight.pk": "Limelight",
        "ethnic.pk": "Ethnic",
        "alkaramstudio.com": "Alkaram",  # CHANGED: Just "Alkaram"
        "gulahmedshop.com": "Gul Ahmed",
        "junaidjamshed.com": "J.",
        "crossstitch.pk": "Cross Stitch",
        "charizma.com": "Charizma",
        "laam.pk": "LAAM",
        "sanaullastore.com": "Sanaulla Store"
    }
    
    def detect(self, url: str) -> str:
        host = urlparse(url).netloc.lower()
        host = host.replace("www.", "")
        for domain, brand in self.BRAND_MAP.items():
            if domain in host:
                return brand
        if host:
            return host.split(".")[0].replace("-", " ").title()
        return ""
    
    @classmethod
    def add_brand(cls, domain: str, brand: str):
        cls.BRAND_MAP[domain.lower()] = brand