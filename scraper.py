import time
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class LandScraper:
    def get_html(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            content = page.content()
            browser.close()
            return content

    def scrape_satterley(self, url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        # Logic to find items that look like property cards
        for item in soup.select('div[class*="estate"], div[class*="property"]'):
            text = item.get_text(separator=' ').strip()
            if "Lot" in text:
                try:
                    price_match = re.search(r'\$(\d{3},?\d{3})', text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0
                    lot = re.search(r'Lot\s?(\d+)', text).group(1)
                    results.append({
                        'estate_name': "Satterley Estate",
                        'suburb': "Perth",
                        'lot_number': lot,
                        'price': price,
                        'status': "Available" if "sold" not in text.lower() else "Sold",
                        'link': url
                    })
                except: continue
        return results
