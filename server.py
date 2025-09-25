from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import os

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow the HTML file to make requests
CORS(app)

# Define the path to the database file.
DB_PATH = os.path.join('F', 'Database for ticket tool', 'database.json')

def read_data():
    """Reads the entire database from the JSON file."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, 'r') as f:
            if os.path.getsize(DB_PATH) == 0:
                return {'users': {}, 'tickets': []}
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'users': {}, 'tickets': []}

def write_data(data):
    """Writes the entire database to the JSON file."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error writing to database file: {e}")

# --- Server Homepage ---
@app.route('/')
def index():
    """A simple root route to confirm the server is running."""
    return "<h1>IT Ticketing Dashboard Server</h1><p>The server is running correctly.</p>"

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

# --- NEW LOGIN ENDPOINT ---
@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.json
    employee_code = data.get('employeeCode')
    password = data.get('password')

    all_data = read_data()
    users = all_data.get('users', {})

    user = users.get(employee_code)

    if user and user.get('password') == password:
        print(f"Successful login for employee code: {employee_code}")
        # Don't send the password back to the client
        user_info = user.copy()
        user_info.pop('password', None) 
        return jsonify({'success': True, 'user': user_info, 'employeeCode': employee_code})
    else:
        print(f"Failed login attempt for employee code: {employee_code}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# --- DATA ENDPOINTS ---
@app.route('/api/data', methods=['GET'])
def get_data():
    """API endpoint to get all data."""
    print("GET request received for /api/data")
    data = read_data()
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def update_data():
    """API endpoint to update all data."""
    print("POST request received for /api/data")
    new_data = request.json
    if not new_data:
        return jsonify({'error': 'Invalid data provided'}), 400
    
    write_data(new_data)
    return jsonify({'success': True, 'message': 'Data updated successfully.'})

if __name__ == '__main__':
    # Initialize the database file if it doesn't exist
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        print(f"Database file not found or empty. Creating a new one at {DB_PATH}")
        initial_data = {
            "users": {
                "1110": {"name": "Lokesh", "role": "admin", "category": "Level 3", "password": "password"},
                "2763": {"name": "Dhanush", "role": "admin", "category": "Level 3", "password": "password"},
                "82655": {"name": "Manikandan", "role": "agent", "category": "Level 1", "password": "password"},
                "82717": {"name": "Manjunathan", "role": "agent", "category": "Level 1", "password": "password"}
            },
            "tickets": [
                {"id": "001", "date": "2024-08-01", "time": "10:30 AM", "caller": "Jane Doe", "department": "Sales", "contact": "jane.doe@example.com", "issue": "Unable to connect to Wi-Fi.", "category": "Network", "assignedTo": "Manikandan", "priority": "High", "status": "In Progress", "resolution": "", "notes": "User is in a rush for a client meeting."}
            ]
        }
        write_data(initial_data)

    app.run(host='0.0.0.0', port=5000, debug=True)
