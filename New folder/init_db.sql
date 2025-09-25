CREATE TABLE users (
    employee_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    category TEXT
);

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
