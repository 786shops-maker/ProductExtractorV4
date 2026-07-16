"""
price_parser.py
Universal price extractor with strict main-product targeting.
Ignores "related products" and "you may also like" sections.
"""
import re
from bs4 import BeautifulSoup

class PriceParser:
    PRICE_PATTERNS = [
        r"Rs\.?\s*([\d,]+)",
        r"PKR\s*([\d,]+)",
        r"Rs\s*([\d,]+)",
        r"([\d,]+)\s*PKR",
    ]
    
    def parse(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        
        # CRITICAL: Remove "related products" sections entirely
        bad_selectors = [
            '.product-recommendations', '.related-products', '.cross-sell', 
            '.upsell-products', '.you-may-also-like', '.recently-viewed',
            '.product-block-related', '.slider-related', '.grid__item'
        ]
        for selector in bad_selectors:
            for bad_elem in soup.select(selector):
                # Only remove if it contains price-like content
                if any(p in bad_elem.get_text().lower() for p in ['rs', 'pkr', 'price']):
                    bad_elem.decompose()
        
        prices = []
        sale_prices = []
        
        # Find prices in MAIN product area only
        main_selectors = [
            '.product__price', '.product-price', '.price--current',
            '.product__price--current', '.money', '.price-item--current'
        ]
        
        for selector in main_selectors:
            elements = soup.select(selector)
            for elem in elements:
                elem_text = elem.get_text(" ", strip=True)
                
                # Check if sale
                classes = " ".join(elem.get("class", [])).lower()
                parent_classes = " ".join(elem.parent.get("class", [])).lower()
                is_sale = any(s in classes or s in parent_classes for s in ["sale", "discount", "special", "compare"])
                
                for pattern in self.PRICE_PATTERNS:
                    matches = re.findall(pattern, elem_text, re.IGNORECASE)
                    for match in matches:
                        value = match.replace(",", "")
                        try:
                            value = int(value)
                            if 1000 <= value <= 50000:  # Reasonable range
                                if is_sale:
                                    sale_prices.append(value)
                                else:
                                    prices.append(value)
                        except:
                            pass
        
        # If no structured prices, search text (but exclude related product text)
        if not prices and not sale_prices:
            # Get text from main product area only
            main_area = soup.select_one('.product, .product-single, .product-detail')
            if main_area:
                text = main_area.get_text(" ", strip=True)
            else:
                text = soup.get_text(" ", strip=True)
            
            for pattern in self.PRICE_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.replace(",", "")
                    try:
                        value = int(value)
                        if 1000 <= value <= 50000:
                            prices.append(value)
                    except:
                        pass

        # Deduplicate and sort
        prices = sorted(list(set(prices)))
        sale_prices = sorted(list(set(sale_prices)))
        
        result = {
            "price": "",
            "sale_price": "",
            "currency": "PKR"
        }
        
        # Combine all found prices
        all_found = sorted(list(set(prices + sale_prices)))
        
        if len(all_found) >= 2:
            result["price"] = str(all_found[-1])  # Highest
            result["sale_price"] = str(all_found[0])  # Lowest
        elif len(all_found) == 1:
            result["price"] = str(all_found[0])
            
        return result
