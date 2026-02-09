import sqlite3
import hashlib
from datetime import datetime

class LandDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    unique_hash TEXT PRIMARY KEY,
                    estate_name TEXT,
                    suburb TEXT,
                    lot_number TEXT,
                    price REAL,
                    status TEXT,
                    link TEXT,
                    last_seen DATETIME
                )
            """)

    def generate_hash(self, estate, lot):
        raw = f"{str(estate).lower()}|{str(lot).lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_listing(self, u_hash):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM listings WHERE unique_hash = ?", (u_hash,))
        return cursor.fetchone()

    def upsert_listing(self, data):
        u_hash = self.generate_hash(data['estate_name'], data['lot_number'])
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO listings (unique_hash, estate_name, suburb, lot_number, price, status, link, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(unique_hash) DO UPDATE SET 
                price=excluded.price, status=excluded.status, last_seen=excluded.last_seen
            """, (u_hash, data['estate_name'], data['suburb'], data['lot_number'], 
                  data['price'], data['status'], data['link'], now))
