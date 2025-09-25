@echo off

REM Navigate to the directory where your app.py is located
cd /d "C:\Users\Administrator\Desktop\MyWebPage\Ticketing Tool"

REM --- Step 1: Initialize database (only if not already created) ---
IF NOT EXIST database.db (
    echo database.db not found. Attempting to create and populate it...
    REM Check if sqlite3 command is available
    where sqlite3 >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: 'sqlite3' command not found.
        echo Please ensure SQLite is installed and added to your system's PATH.
        echo.
        pause
        exit /b 1
    )
    REM Execute the SQL script to create tables and insert initial data
    sqlite3 database.db < init_db.sql
    IF %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to execute init_db.sql. Check the SQL file for errors.
        pause
        exit /b 1
    )
    echo Database initialized successfully.
) ELSE (
    echo database.db already exists. Skipping database initialization.
)

REM --- Step 2: Start Flask app ---
echo Starting Flask server...
REM Open the browser automatically to the new URL with port 5003
start "" http://127.0.0.1:5003/
python app.py

pause
