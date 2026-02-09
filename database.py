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
                    suburb TEXT,
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
        h = hashlib.sha256(f"{d['estate']}{d['lot']}{d['stage']}".lower().encode()).hexdigest()
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
                INSERT INTO listings (hash, estate, suburb, lot, price, size, frontage, stage, status, link, updated)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(hash) DO UPDATE SET 
                price=excluded.price, status=excluded.status, updated=excluded.updated
            """, (h, d['estate'], d.get('suburb',''), d['lot'], d['price'], d.get('size',''), 
                  d.get('frontage',''), d.get('stage',''), d['status'], d['link'], now))
        return h
