import time
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class LandIntelligence:
    def get_content(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(3)
                return page.content()
            except: return ""
            finally: browser.close()

    def scour_page(self, url):
        html = self.get_content(url)
        if not html: return []
        soup = BeautifulSoup(html, 'html.parser')
        data = []

        # Find everything that looks like a lot, a row, or a card
        items = soup.find_all(['tr', 'div', 'article'], class_=re.compile(r'lot|property|estate|item|card', re.I))
        
        for item in items:
            text = item.get_text(separator=' ').strip()
            # If it has a Lot number or a Price, it's a block
            if re.search(r'Lot\s?\d+|\$\d+', text):
                lot = re.search(r'Lot\s?(\d+)', text)
                price = re.search(r'\$(\d{3},?\d{3})', text)
                size = re.search(r'(\d{2,4})\s?m2|sqm', text, re.I)
                front = re.search(r'(\d{1,2})\s?m\s?(front|wide)', text, re.I)
                
                # Identify Status (EOI, Coming Soon, etc)
                status = "Now Selling"
                if any(x in text.lower() for x in ["eoi", "interest", "ballot", "register"]):
                    status = "📌 EOI / Registration"
                elif any(x in text.lower() for x in ["coming soon", "future", "next release"]):
                    status = "⏳ Coming Soon"
                elif "sold" in text.lower():
                    status = "Sold"

                data.append({
                    'estate': url.split('/')[-2].replace('-', ' ').title() if len(url.split('/')) > 2 else "Unknown Estate",
                    'lot': lot.group(1) if lot else "TBA",
                    'price': float(price.group(1).replace(',', '')) if price else 0,
                    'size': size.group(1) + "sqm" if size else "TBA",
                    'frontage': front.group(1) + "m" if front else "TBA",
                    'stage': re.search(r'Stage\s?(\d+)', text, re.I).group(0) if re.search(r'Stage\s?(\d+)', text, re.I) else "TBA",
                    'status': status,
                    'link': url
                })
        return data
