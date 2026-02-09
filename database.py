import sqlite3
import hashlib
from datetime import datetime

class LandDatabase:
    def __init__(self, db_path="land.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS land_stats (
                    hash TEXT PRIMARY KEY,
                    estate TEXT, suburb TEXT, lot TEXT, price REAL,
                    dimensions TEXT, deposit TEXT, status TEXT,
                    release_info TEXT, agent_details TEXT,
                    link TEXT, first_seen DATETIME, is_notified INTEGER DEFAULT 0
                )
            """)

    def upsert_block(self, d):
        # Unique ID based on Estate and Lot
        raw_id = f"{d['estate']}{d['lot']}".lower().strip()
        h = hashlib.sha256(raw_id.encode()).hexdigest()
        now = datetime.now().isoformat()
        
        with self.conn:
            # Check if it exists
            curr = self.conn.cursor()
            curr.execute("SELECT price, status FROM land_stats WHERE hash=?", (h,))
            row = curr.fetchone()
            
            if not row:
                self.conn.execute("""
                    INSERT INTO land_stats (hash, estate, suburb, lot, price, dimensions, deposit, status, release_info, agent_details, link, first_seen)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (h, d['estate'], d['suburb'], d['lot'], d['price'], d['dimensions'], d['deposit'], d['status'], d['release_info'], d['agent_details'], d['link'], now))
                return "NEW"
            elif row[0] != d['price'] or row[1] != d['status']:
                self.conn.execute("UPDATE land_stats SET price=?, status=?, release_info=? WHERE hash=?", (d['price'], d['status'], d['release_info'], h))
                return "UPDATE"
        return None

    def get_new_for_report(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM land_stats WHERE first_seen >= date('now', '-1 day')")
        return c.fetchall()
