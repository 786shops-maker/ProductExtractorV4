from dataclasses import dataclass, field
from typing import List


@dataclass
class Product:

    url: str = ""

    brand: str = ""

    title: str = ""

    sku: str = ""

    price: str = ""

    sale_price: str = ""

    currency: str = ""

    color: str = ""

    description: str = ""

    image_urls: List[str] = field(default_factory=list)

    downloaded_images: List[str] = field(default_factory=list)

    output_folder: str = ""