from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend to call API from another domain

DB = 'tickets.db'

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return open("Rajsriya Ticketing Tool.html").read()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE employee_code = ? AND password = ?', 
                        (data['employeeCode'], data['password'])).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    conn = get_db_connection()
    tickets = conn.execute('SELECT * FROM tickets ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in tickets])

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    now = datetime.now()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO tickets (date, time, caller, department, contact, issue, category,
                             assigned_to, priority, status, resolution, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        now.strftime('%Y-%m-%d'),
        now.strftime('%I:%M %p'),
        data['caller'], data['department'], data['contact'], data['issue'],
        data['category'], data['assignedTo'], data['priority'], 'In Progress', '', data['notes']
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Ticket created successfully'}), 201

@app.route('/api/tickets/<int:id>', methods=['PUT'])
def update_ticket(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE tickets SET
        caller=?, department=?, contact=?, issue=?, category=?,
        assigned_to=?, priority=?, status=?, resolution=?, notes=?
        WHERE id=?
    ''', (
        data['caller'], data['department'], data['contact'], data['issue'],
        data['category'], data['assignedTo'], data['priority'],
        data['status'], data['resolution'], data['notes'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Ticket updated successfully'}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO users (employee_code, name, password, role, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['employeeCode'], data['name'], data['password'],
        data['role'], data['category']
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User created'}), 201

if __name__ == '__main__':
    app.run(debug=True)
