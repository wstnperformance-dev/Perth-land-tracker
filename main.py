import os
import requests
from database import LandDatabase
from scraper import LandIntelligence

def send_alert(msg):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT')
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})

def run():
    db = LandDatabase("land.db")
    bot = LandIntelligence()
    
    # ADD EVERY DEVELOPER PAGE HERE
    # These are "hub" pages - the bot will scour everything inside them
    target_urls = [
        "https://www.openlot.com.au/perth-wa",
        "https://www.satterley.com.au/land-for-sale/perth",
        "https://www.peet.com.au/wa/land-for-sale",
        "https://www.developmentwa.com.au/residential",
        "https://www.cedarwoods.com.au/land-releases-perth-wa"
    ]
    
    for url in target_urls:
        print(f"Scouring: {url}")
        blocks = bot.scour_page(url)
        for b in blocks:
            if b['status'] == "Sold": continue
            
            h = hashlib.sha256(f"{b['estate']}{b['lot']}{b['stage']}".lower().encode()).hexdigest()
            existing = db.get_listing(h)
            
            if not existing:
                db.upsert(b)
                msg = (f"🌟 <b>{b['status']}</b>\n"
                       f"🏡 Estate: {b['estate']}\n"
                       f"📍 Lot: {b['lot']} | {b['stage']}\n"
                       f"📐 {b['size']} | {b['frontage']} wide\n"
                       f"💰 Price: ${b['price']:,.0f}\n"
                       f"🔗 <a href='{b['link']}'>Go to Site</a>")
                send_alert(msg)
            else:
                # Check for critical changes
                old_status = existing[8]
                if b['status'] != old_status:
                    db.upsert(b)
                    msg = (f"🔄 <b>STATUS CHANGE</b>\n"
                           f"🏡 {b['estate']} | Lot {b['lot']}\n"
                           f"Was: {old_status}\n"
                           f"Now: <b>{b['status']}</b>")
                    send_alert(msg)

import hashlib
if __name__ == "__main__":
    run()
