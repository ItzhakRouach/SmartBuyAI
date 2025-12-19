import sqlite3
from datetime import datetime
import os

# --- Database Management Module ---
# This module handles all interactions with the SQLite database,
# ensuring data persistence and integrity.

# Get the absolute path of the current script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the path to the data folder (one level up from 'database')
DATA_DIR = os.path.join(BASE_DIR, '..','..','data')
DB_PATH = os.path.join(DATA_DIR, 'market_prices.db')


def init_db():
    """
        Initializes the SQLite database and creates the products table if it doesn't exist.
     """
    try:
        # 1. Create the data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"Created directory: {DATA_DIR}")

        # 2. Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 3. Create the table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT,
                    price REAL,
                    currency TEXT,
                    stock_status BOOLEAN,
                    url TEXT,
                    source_website TEXT,
                    scanned_at DATETIME
                )
            ''')
        conn.commit()
        conn.close()
        print(f"Database initialized at: {DB_PATH}")

    except Exception as e:
        print(f"Failed to initialize database: {e}")


def save_product_to_db(product_data,source_website):
    """
        Inserts or updates a product in the database.
        Uses 'INSERT OR REPLACE' based on the unique URL to update existing entries.
        """

    try:
        conn = sqlite3.connect('../data/market_prices.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO products
            (product_name, price, currency, stock_status, url, source_website, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',(
            product_data.get('product_name'),
            product_data.get('price'),
            product_data.get('currency'),
            product_data.get('stock_status'),
            product_data.get('url'),
            source_website,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()
        print("Product inserted successfully.")
    except Exception as e:
        print("Database error occured: ", e)

#If run direcrtly, initlized the DB
if __name__ == '__main__':
    init_db()

