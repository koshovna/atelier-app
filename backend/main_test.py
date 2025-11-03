import pytest
import uuid
from database import Database

db = Database('atelier.db')

def test_add_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count_before = cursor.fetchone()[0]

    test_order_number = str(uuid.uuid4())
    data = ('Ермошенко', test_order_number, 'Джинсы', '2025-11-03', '2025-11-12', 'Мастерова', 2000.0)
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number=?", (test_order_number,))
    count_new = cursor.fetchone()[0]
    conn.close()
    assert count_new == 1

def test_delete_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    test_order_number = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Удалёнкин', test_order_number, 'Куртка', '2025-11-03', '2025-11-12', 'Мастерова', 2100.0))
    conn.commit()
    cursor.execute("DELETE FROM orders WHERE order_number=?", (test_order_number,))
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number=?", (test_order_number,))
    count_deleted = cursor.fetchone()[0]
    conn.close()
    assert count_deleted == 0

def test_update_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    test_order_number = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Проверкин', test_order_number, 'Жилет', '2025-11-04', '2025-11-10', 'Мастерова', 1800.0))
    conn.commit()
    cursor.execute("""
        UPDATE orders
        SET product_name='Пальто'
        WHERE order_number=?
    """, (test_order_number,))
    conn.commit()
    cursor.execute("SELECT product_name FROM orders WHERE order_number=?", (test_order_number,))
    updated_name = cursor.fetchone()[0]
    conn.close()
    assert updated_name == 'Пальто'

def test_max_cost():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(cost) FROM orders")
    max_cost = cursor.fetchone()[0]
    conn.close()
    assert max_cost >= 0

def test_delete_by_client():
    conn = db.get_connection()
    cursor = conn.cursor()
    test_order_number = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Тестов', test_order_number, 'Пиджак', '2025-11-03', '2025-11-12', 'Мастерова', 2000.0))
    conn.commit()
    cursor.execute("DELETE FROM orders WHERE client_surname='Тестов'")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE client_surname='Тестов'")
    count_deleted = cursor.fetchone()[0]
    conn.close()
    assert count_deleted == 0
