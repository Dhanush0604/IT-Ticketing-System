-- Drop existing tables to ensure a clean start
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tickets;

-- Create the users table
CREATE TABLE users (
    employee_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    category TEXT
);

-- Create the tickets table
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    time TEXT,
    caller TEXT,
    department TEXT,
    contact TEXT,
    issue TEXT,
    category TEXT,
    assigned_to TEXT,
    priority TEXT,
    status TEXT,
    resolution TEXT,
    notes TEXT
);

-- FIX: Insert YOUR specific list of users
INSERT INTO users (employee_code, name, password, role, category) VALUES
('1110', 'Lokesh', 'password', 'admin', 'Level 3'),
('2763', 'Dhanush', 'password', 'admin', 'Level 3'),
('82655', 'Manikandan', 'password', 'agent', 'Level 1'),
('82717', 'Manjunathan', 'password', 'agent', 'Level 1');

-- Insert some sample tickets assigned to your agents for testing
INSERT INTO tickets (date, time, caller, department, contact, issue, category, assigned_to, priority, status) VALUES
('2025-08-15', '11:00:00', 'Sample Caller 1', 'Finance', '555-0101', 'PC is very slow after update', 'Hardware', 'Manikandan', 'Low', 'Open'),
('2025-08-15', '11:05:00', 'Sample Caller 2', 'HR', '555-0102', 'Cannot access the shared drive', 'Network', 'Manjunathan', 'High', 'Open');

