import os
import requests
from database import LandDatabase
from scraper import LandScraper

def send_telegram(msg):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

def run():
    db = LandDatabase("land.db")
    scraper = LandScraper()
    
    # Add your target URLs here inside the brackets
    urls = ["https://www.satterley.com.au/land-for-sale/perth"]
    
    for url in urls:
        print(f"Checking {url}...")
        items = scraper.scrape_satterley(url)
        for item in items:
            u_hash = db.generate_hash(item['estate_name'], item['lot_number'])
            existing = db.get_listing(u_hash)
            
            if not existing:
                db.upsert_listing(item)
                if item['price'] > 0:
                    msg = f"🚨 <b>NEW LAND FOUND!</b>\nEstate: {item['estate_name']}\nLot: {item['lot_number']}\nPrice: ${item['price']:,.0f}\n<a href='{item['link']}'>Link</a>"
                    send_telegram(msg)
            else:
                old_price = existing[4]
                if item['price'] < old_price and item['price'] > 0:
                    db.upsert_listing(item)
                    msg = f"📉 <b>PRICE DROP!</b>\nLot: {item['lot_number']}\nWas: ${old_price:,.0f}\nNow: ${item['price']:,.0f}"
                    send_telegram(msg)

if __name__ == "__main__":
    run()
