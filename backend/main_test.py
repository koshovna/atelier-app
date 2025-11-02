import pytest
from database import Database

db = Database('atelier.db')

# Тест: добавление нового заказа
def test_add_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count_before = cursor.fetchone()[0]

    data = ('Ермошенко', 'ORD555', 'Джинсы', '2025-11-03', '2025-11-12', 'Мастерова', 2000.0)
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number='ORD555'")
    count_new = cursor.fetchone()[0]
    conn.close()
    assert count_new == 1

# Тест: удаление заказа
def test_delete_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_number='ORD555'")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number='ORD555'")
    count_deleted = cursor.fetchone()[0]
    conn.close()
    assert count_deleted == 0

# Тест: обновление заказа
def test_update_order():
    conn = db.get_connection()
    cursor = conn.cursor()
    # Добавим заказ
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Проверкин', 'ORD777', 'Жилет', '2025-11-04', '2025-11-10', 'Мастерова', 1800.0))
    conn.commit()

    # Обновим название изделия
    cursor.execute("""
        UPDATE orders
        SET product_name='Пальто'
        WHERE order_number='ORD777'
    """)
    conn.commit()

    cursor.execute("SELECT product_name FROM orders WHERE order_number='ORD777'")
    updated_name = cursor.fetchone()[0]
    conn.close()
    assert updated_name == 'Пальто'

# Тест: аналитика (максимальная стоимость заказа)
def test_max_cost():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(cost) FROM orders")
    max_cost = cursor.fetchone()[0]
    conn.close()
    assert max_cost >= 0

# Тест: удаление заказов от клиента
def test_delete_by_client():
    conn = db.get_connection()
    cursor = conn.cursor()
    # Добавим заказ для клиента "Тестов"
    cursor.execute("""
        INSERT INTO orders (client_surname, order_number, product_name, order_date, completion_date, master_surname, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Тестов', 'ORD999', 'Пиджак', '2025-11-03', '2025-11-12', 'Мастерова', 2000.0))
    conn.commit()

    # Удалить все заказы клиента "Тестов"
    cursor.execute("DELETE FROM orders WHERE client_surname='Тестов'")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE client_surname='Тестов'")
    count_deleted = cursor.fetchone()[0]
    conn.close()
    assert count_deleted == 0
