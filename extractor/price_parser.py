"""
price_parser.py
Universal price extractor with sale price priority.
"""
import re
from bs4 import BeautifulSoup

class PriceParser:
    PRICE_PATTERNS = [
        r"Rs\.?\s*([\d,]+)",
        r"PKR\s*([\d,]+)",
        r"Rs\s*([\d,]+)",
        r"([\d,]+)\s*PKR",
        r"Price[:\s]+Rs\.?\s*([\d,]+)",
        r"Sale\s*Price[:\s]+Rs\.?\s*([\d,]+)",
        r"Special\s*Price[:\s]+([\d,]+)",
    ]
    
    def parse(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)
        
        prices = []
        sale_prices = []
        
        # First, look for prices in specific sale price elements
        sale_selectors = [
            '[class*="sale"]',
            '[class*="Sale"]',
            '.price--sale',
            '.sale-price',
            '.special-price',
            '[class*="discount"]',
            '.on-sale'
        ]
        
        for selector in sale_selectors:
            sale_elements = soup.select(selector)
            for elem in sale_elements:
                elem_text = elem.get_text(" ", strip=True)
                for pattern in self.PRICE_PATTERNS:
                    for match in re.findall(pattern, elem_text, re.IGNORECASE):
                        value = match.replace(",", "")
                        try:
                            value = int(value)
                            if 500 <= value <= 100000:  # Reasonable price range
                                sale_prices.append(value)
                        except:
                            pass
        
        # Then look for regular price elements
        price_selectors = [
            '[class*="price"]',
            '[class*="Price"]',
            '.amount',
            '.woocommerce-Price-amount',
            '.product-price',
            '.price-wrapper'
        ]
        
        for selector in price_selectors:
            price_elements = soup.select(selector)
            for elem in price_elements:
                # Skip if it's a sale price element (already processed)
                elem_classes = " ".join(elem.get("class", []))
                if any(x in elem_classes.lower() for x in ["sale", "discount", "special"]):
                    continue
                    
                elem_text = elem.get_text(" ", strip=True)
                for pattern in self.PRICE_PATTERNS:
                    for match in re.findall(pattern, elem_text, re.IGNORECASE):
                        value = match.replace(",", "")
                        try:
                            value = int(value)
                            if 500 <= value <= 100000:  # Reasonable price range
                                prices.append(value)
                        except:
                            pass
        
        # Fallback: search entire text
        if not prices and not sale_prices:
            for pattern in self.PRICE_PATTERNS:
                for match in re.findall(pattern, text, re.IGNORECASE):
                    value = match.replace(",", "")
                    try:
                        value = int(value)
                        if 500 <= value <= 100000:
                            prices.append(value)
                    except:
                        pass
        
        # Remove duplicates and sort
        prices = sorted(list(set(prices)))
        sale_prices = sorted(list(set(sale_prices)))
        
        result = {
            "price": "",
            "sale_price": "",
            "currency": "PKR"
        }
        
        # Priority: Use sale price if available
        if sale_prices:
            result["sale_price"] = str(sale_prices[-1])  # Highest sale price
            if prices and prices[-1] > sale_prices[-1]:
                result["price"] = str(prices[-1])  # Original price (higher)
            else:
                result["price"] = str(sale_prices[-1])
        elif prices:
            if len(prices) >= 2:
                # Assume lower is sale price, higher is original
                result["sale_price"] = str(prices[0])
                result["price"] = str(prices[-1])
            else:
                result["price"] = str(prices[0])
        
        return result