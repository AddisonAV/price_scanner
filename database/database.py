import sqlite3
from contextlib import closing

class DatabaseHandler:
    def __init__(self, db_name='scraper_data.db'):
        self.db_name = db_name
        self._create_tables()

    def _create_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self._create_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraper_data (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        url TEXT,
                        currency TEXT,
                        price REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()

    def insert_data(self, name, url, currency, price):
        with self._create_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO scraper_data (name, url, currency, price)
                    VALUES (?, ?, ?, ?)
                ''', (name, url, currency, price))
                conn.commit()

    def fetch_all_data(self):
        with self._create_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('SELECT * FROM scraper_data')
                return cursor.fetchall()
            
    def fetch_data_by_name(self, name):
        with self._create_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                               SELECT * FROM scraper_data 
                               WHERE name = ?
                               ORDER BY timestamp ASC
                               ''', (name,))
                return cursor.fetchall()

