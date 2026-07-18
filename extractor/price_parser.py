"""
price_parser.py
Extracts product price robustly using JSON-LD, Meta tags, and proximity-based regex.
"""
import re
import json
from bs4 import BeautifulSoup

class PriceParser:
    def parse(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        price = None
        sale_price = None

        # 1. Try JSON-LD Structured Data (Most reliable for Shopify)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, dict):
                        price = float(offers.get('price', 0))
                    elif isinstance(offers, list) and len(offers) > 0:
                        price = float(offers[0].get('price', 0))
                elif isinstance(data, list):
                    for item in data:
                        if 'offers' in item:
                            offers = item['offers']
                            if isinstance(offers, dict):
                                price = float(offers.get('price', 0))
                                break
                            elif isinstance(offers, list) and len(offers) > 0:
                                price = float(offers[0].get('price', 0))
                                break
            except Exception:
                pass

        # 2. Try Meta Tags
        if price is None:
            meta_price = soup.find('meta', property='product:price:amount')
            if meta_price and meta_price.get('content'):
                try:
                    price = float(meta_price['content'])
                except ValueError:
                    pass

        # 3. Fallback: Proximity-based Regex (Ignores shipping/COD policy text)
        if price is None:
            text = soup.get_text(separator=' ', strip=True)
            
            # Find locations of key product indicators to anchor our search
            indicators = ['add to cart', 'article no', 'product id', 'sku', 'pay in']
            indicator_indices = [text.lower().find(ind) for ind in indicators if text.lower().find(ind) != -1]
            
            if indicator_indices:
                # Use the first found indicator as the anchor
                anchor = min(indicator_indices)
                # Search window: 600 chars before to 600 chars after
                start = max(0, anchor - 600)
                end = min(len(text), anchor + 600)
                search_text = text[start:end]
            else:
                search_text = text

            # Find all prices in the search window
            matches = re.findall(r'(?:PKR|Rs\.?|PKR\.?)\s*([\d,]+)', search_text, re.IGNORECASE)
            if not matches:
                matches = re.findall(r'([\d,]+)\s*(?:PKR|Rs\.?)', search_text, re.IGNORECASE)
            
            if matches:
                valid_prices = []
                for m in matches:
                    try:
                        val = float(m.replace(',', '').strip())
                        if 500 < val < 100000:  # Reasonable product price range
                            valid_prices.append(val)
                    except ValueError:
                        pass
                
                if valid_prices:
                    # Sort prices. If there are multiple (e.g., original and sale), 
                    # the lowest is usually the current active price.
                    valid_prices.sort()
                    price = valid_prices[0]

        if price is not None:
            price = int(price) if price.is_integer() else round(price, 2)
        if sale_price is not None:
            sale_price = int(sale_price) if sale_price.is_integer() else round(sale_price, 2)

        return {
            "price": str(price) if price else "",
            "sale_price": str(sale_price) if sale_price else ""
        }