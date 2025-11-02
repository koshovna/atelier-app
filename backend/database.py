import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='atelier.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_surname TEXT NOT NULL,
                order_number TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                order_date TEXT NOT NULL,
                completion_date TEXT NOT NULL,
                master_surname TEXT NOT NULL,
                cost REAL NOT NULL
            )
        ''')
        
        # Добавляем пользователя
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         ('admin', '123'))
        except sqlite3.IntegrityError:
            pass
        
        # Добавляем данные
        test_orders = [
            ('Иванов', 'ORD001', 'Платье', '2025-10-01', '2025-10-15', 'Петрова', 5000.0),
            ('Сидоров', 'ORD002', 'Костюм', '2025-10-05', '2025-10-20', 'Смирнова', 8000.0),
            ('Петров', 'ORD003', 'Юбка', '2025-10-10', '2025-10-18', 'Петрова', 3000.0),
            ('Козлов', 'ORD004', 'Брюки', '2025-10-12', '2025-10-25', 'Иванова', 4500.0),
        ]
        
        for order in test_orders:
            try:
                cursor.execute('''
                    INSERT INTO orders (client_surname, order_number, product_name, 
                                      order_date, completion_date, master_surname, cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', order)
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        conn.close()
