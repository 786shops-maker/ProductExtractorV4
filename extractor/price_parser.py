"""
price_parser.py
Universal price extractor with strict main-product targeting.
Ignores "related products" and "you may also like" sections to prevent wrong price extraction.
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
        
        # CRITICAL: Remove "related products" sections entirely before searching
        # This prevents the parser from grabbing prices of perfumes/accessories shown at the bottom
        bad_selectors = [
            '.product-recommendations', '.related-products', '.cross-sell', 
            '.upsell-products', '.you-may-also-like', '.recently-viewed',
            '.product-block-related', '.slider-related'
        ]
        for selector in bad_selectors:
            for bad_elem in soup.select(selector):
                bad_elem.decompose()
        
        prices = []
        sale_prices = []
        
        # Find all elements that look like prices in the CLEANED soup
        all_price_elements = soup.select('.price, .price-item, .amount, .product-price, [class*="Price"], .money')
        
        for elem in all_price_elements:
            elem_text = elem.get_text(" ", strip=True)
            
            # Check if the element or its parent explicitly indicates a sale
            classes = " ".join(elem.get("class", [])).lower()
            parent_classes = " ".join(elem.parent.get("class", [])).lower()
            is_sale = any(s in classes or s in parent_classes for s in ["sale", "discount", "special", "compare", "was"])
            
            for pattern in self.PRICE_PATTERNS:
                matches = re.findall(pattern, elem_text, re.IGNORECASE)
                for match in matches:
                    value = match.replace(",", "")
                    try:
                        value = int(value)
                        if 500 <= value <= 100000:  # Reasonable range for Pakistani suits
                            if is_sale:
                                sale_prices.append(value)
                            else:
                                prices.append(value)
                    except:
                        pass
        
        # Fallback: If no structured prices found, search the remaining text
        if not prices and not sale_prices:
            text = soup.get_text(" ", strip=True)
            for pattern in self.PRICE_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.replace(",", "")
                    try:
                        value = int(value)
                        if 500 <= value <= 100000:
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
        
        # Combine all found prices to determine regular vs sale
        all_found = sorted(list(set(prices + sale_prices)))
        
        if len(all_found) >= 2:
            # Highest is regular price, lowest is sale price
            result["price"] = str(all_found[-1])
            result["sale_price"] = str(all_found[0])
        elif len(all_found) == 1:
            result["price"] = str(all_found[0])
            
        return result
