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
                    hash TEXT PRIMARY KEY,
                    estate TEXT,
                    lot TEXT,
                    price REAL,
                    size TEXT,
                    frontage TEXT,
                    stage TEXT,
                    status TEXT,
                    link TEXT,
                    updated DATETIME
                )
            """)

    def get_listing(self, h):
        c = self.conn.cursor()
        c.execute("SELECT * FROM listings WHERE hash = ?", (h,))
        return c.fetchone()

    def upsert(self, d):
        # Unique ID based on Estate, Lot, and Stage to prevent duplicates
        raw_id = f"{d['estate']}{d['lot']}{d['stage']}".lower().strip()
        h = hashlib.sha256(raw_id.encode()).hexdigest()
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO listings (hash, estate, lot, price, size, frontage, stage, status, link, updated)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(hash) DO UPDATE SET 
                price=excluded.price, status=excluded.status, updated=excluded.updated,
                size=excluded.size, frontage=excluded.frontage, stage=excluded.stage
            """, (h, d['estate'], d['lot'], d['price'], d['size'], 
                  d['frontage'], d['stage'], d['status'], d['link'], now))
        return h
