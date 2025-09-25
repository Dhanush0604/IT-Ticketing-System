import os
import sqlite3
from flask import Flask, request, jsonify, render_template, Response
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SQL_INIT_SCRIPT = os.path.join(BASE_DIR, "init_db.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        if not os.path.exists(SQL_INIT_SCRIPT):
            print(f"FATAL ERROR: init_db.sql not found at {SQL_INIT_SCRIPT}")
            return
        print(f"Initializing database from {SQL_INIT_SCRIPT}...")
        try:
            with open(SQL_INIT_SCRIPT, 'r') as f: sql_script = f.read()
            conn = sqlite3.connect(DB_PATH)
            conn.executescript(sql_script)
            # Add location columns if they don't exist
            try:
                conn.execute("ALTER TABLE users ADD COLUMN location TEXT;")
            except sqlite3.OperationalError: pass
            try:
                conn.execute("ALTER TABLE tickets ADD COLUMN location TEXT;")
            except sqlite3.OperationalError: pass
            conn.commit()
            conn.close()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"FATAL ERROR during database initialization: {e}")

# --- Page Routes ---
@app.route('/')
def index(): return render_template("index.html")

@app.route('/favicon.ico')
def favicon(): return Response(status=204)

@app.route('/user-management')
def user_management_page():
    return render_template("user_management.html")

# --- API Routes ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE employee_code = ?', (data.get('employeeCode'),)).fetchone()
    conn.close()
    if user and user['password'] == data.get('password'):
        user_info = dict(user); user_info.pop('password', None)
        return jsonify({'success': True, 'user': user_info})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    employee_code = request.args.get('employeeCode')
    if not employee_code: return jsonify({"error": "employeeCode is required"}), 400
    conn = get_db_connection()
    user = conn.execute('SELECT name, role FROM users WHERE employee_code = ?', (employee_code,)).fetchone()
    if not user: return jsonify({"error": "User not found."}), 404
    
    total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Completed'").fetchone()[0]
    
    all_tickets = conn.execute('SELECT * FROM tickets ORDER BY id DESC').fetchall()
    my_tickets = conn.execute('SELECT * FROM tickets WHERE assigned_to = ? ORDER BY id DESC', (user['name'],)).fetchall()
    conn.close()

    return jsonify({
        "stats": {"total": total, "resolved": resolved, "open": total - resolved},
        "allTickets": [dict(row) for row in all_tickets],
        "myTickets": [dict(row) for row in my_tickets]
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT employee_code, name, role, category, password, location FROM users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])
    
@app.route('/api/tickets/new', methods=['POST'])
def create_ticket():
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO tickets (date, time, caller, department, contact, issue, category, assigned_to, priority, status, resolution, notes, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                     (datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), data['caller'], data['department'], data['contact'], data['issue'], data['category'], data['assigned_to'], data['priority'], 'Open', '', data.get('notes', ''), data.get('location', '')))
        conn.commit(); conn.close()
        return jsonify({'success': True}), 201
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tickets/update/<int:ticket_id>', methods=['POST'])
def update_ticket(ticket_id):
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute("UPDATE tickets SET status = ?, resolution = ?, location = ? WHERE id = ?", (data['status'], data['resolution'], data.get('location', ''), ticket_id))
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tickets/delete/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/new', methods=['POST'])
def create_user():
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (employee_code, name, password, role, category, location) VALUES (?, ?, ?, ?, ?, ?)", 
                     (data['employee_code'], data['name'], data['password'], data['role'], data.get('category', ''), data.get('location', '')))
        conn.commit(); conn.close()
        return jsonify({'success': True}), 201
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Employee code already exists.'}), 409
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/update/<employee_code>', methods=['POST'])
def update_user(employee_code):
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute( "UPDATE users SET name = ?, role = ?, category = ?, password = ?, location = ? WHERE employee_code = ?", 
                     (data['name'], data['role'], data['category'], data['password'], data.get('location', ''), employee_code))
        conn.commit(); conn.close()
        return jsonify({'success': True, 'message': 'User updated successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
        
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
