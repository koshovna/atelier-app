from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)
db = Database()

# Аутентификация
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                  (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'message': 'Успешный вход'})
    return jsonify({'success': False, 'message': 'Неверный логин или пароль'}), 401

# CRUD для заказов
@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sort_by = request.args.get('sort_by')
    if sort_by:
        cursor.execute(f'SELECT * FROM orders ORDER BY {sort_by}')
    else:
        cursor.execute('SELECT * FROM orders')
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.json
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO orders (client_surname, order_number, product_name, 
                              order_date, completion_date, master_surname, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['client_surname'], data['order_number'], data['product_name'],
              data['order_date'], data['completion_date'], data['master_surname'], 
              data['cost']))
        conn.commit()
        return jsonify({'success': True, 'message': 'Заказ добавлен'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Заказ с таким номером уже существует'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE orders 
            SET client_surname=?, order_number=?, product_name=?, 
                order_date=?, completion_date=?, master_surname=?, cost=?
            WHERE id=?
        ''', (data['client_surname'], data['order_number'], data['product_name'],
              data['order_date'], data['completion_date'], data['master_surname'], 
              data['cost'], order_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Заказ обновлен'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Заказ удален'})

# Специальные функции
@app.route('/api/orders/update-by-date', methods=['POST'])
def update_orders_by_date():
    data = request.json
    date = data.get('date')
    updates = data.get('updates')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key}=?" for key in updates.keys()])
    values = list(updates.values()) + [date]
    
    cursor.execute(f'''
        UPDATE orders 
        SET {set_clause}
        WHERE order_date > ?
    ''', values)
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'affected': affected, 
                   'message': f'Обновлено записей: {affected}'})

@app.route('/api/orders/delete-by-client', methods=['DELETE'])
def delete_by_client():
    surname = request.args.get('surname')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE client_surname=?', (surname,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'affected': affected,
                   'message': f'Удалено записей: {affected}'})

# Аналитика
@app.route('/api/analytics/orders-by-master', methods=['GET'])
def orders_by_master():
    master = request.args.get('master')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM orders WHERE master_surname=?', (master,))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'master': master, 'count': result['count']})

@app.route('/api/analytics/max-cost', methods=['GET'])
def max_cost():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(cost) as max_cost FROM orders')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'max_cost': result['max_cost'] or 0})

@app.route('/api/analytics/avg-cost', methods=['GET'])
def avg_cost():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(cost) as avg_cost FROM orders')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'avg_cost': round(result['avg_cost'] or 0, 2)})

# Клиенты
@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sort_by = request.args.get('sort_by', 'client_surname')
    
    cursor.execute(f'''
        SELECT client_surname, order_number, 
               CAST((julianday(completion_date) - julianday(order_date)) AS INTEGER) as duration
        FROM orders
        ORDER BY {sort_by}
    ''')
    
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clients)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


