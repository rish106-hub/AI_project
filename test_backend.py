#!/usr/bin/env python3
import os
import sys
import sqlite3

# -------------------- Dependency Checks --------------------
try:
    import flask
    from flask import json
except ImportError:
    print("Dependency error: Flask is not installed.")
    sys.exit(1)

try:
    import sqlite3
except ImportError:
    print("Dependency error: sqlite3 is not installed.")
    sys.exit(1)

# -------------------- Import Backend Module --------------------
try:
    from backend import app, create_folders, init_db
except Exception as e:
    print("Failed to import backend modules:", e)
    sys.exit(1)

# -------------------- Folder & Database Checks --------------------
expected_folders = ['data', 'logs', 'static', 'templates']
missing_folders = [folder for folder in expected_folders if not os.path.exists(folder)]
if missing_folders:
    print("Missing folders detected:", ", ".join(missing_folders))
    print("Attempting to create missing folders...")
    create_folders()

db_path = os.path.join('data', 'habit_tracker.db')
if not os.path.exists(db_path):
    print(f"Database file '{db_path}' not found. Initializing database...")
    init_db()

# Verify database file creation after init
if not os.path.exists(db_path):
    print(f"Database file '{db_path}' still not found after initialization.")
    sys.exit(1)

# -------------------- API Endpoint Tests --------------------
with app.test_client() as client:
    # Test GET /api/habits (should return 200 and a JSON list)
    response = client.get('/api/habits')
    if response.status_code != 200:
        print("API test failed: GET /api/habits did not return status 200.")
        sys.exit(1)
    
    # Test POST /api/habits (create a new habit)
    habit_data = {
        "name": "Test Habit",
        "description": "This is a test habit.",
        "frequency": "daily",
        "category": "test"
    }
    response = client.post('/api/habits', json=habit_data)
    if response.status_code != 201:
        print("API test failed: POST /api/habits did not return status 201.")
        sys.exit(1)
    created_habit = response.get_json()
    habit_id = created_habit.get("id")
    if not habit_id:
        print("API test failed: Created habit does not have an id.")
        sys.exit(1)
    
    # Test GET /api/habits/<id> to fetch the created habit
    response = client.get(f'/api/habits/{habit_id}')
    if response.status_code != 200:
        print("API test failed: GET /api/habits/<id> did not return status 200.")
        sys.exit(1)
    
    # Test PUT /api/habits/<id> to update the habit
    update_data = {"description": "Updated test habit description"}
    response = client.put(f'/api/habits/{habit_id}', json=update_data)
    if response.status_code != 200:
        print("API test failed: PUT /api/habits/<id> did not return status 200.")
        sys.exit(1)
    
    # Test POST /api/habits/<id>/log to log a habit completion
    log_data = {"status": "completed"}
    response = client.post(f'/api/habits/{habit_id}/log', json=log_data)
    if response.status_code != 201:
        print("API test failed: POST /api/habits/<id>/log did not return status 201.")
        sys.exit(1)
    
    # Test GET /api/recommendations to fetch AI recommendations
    response = client.get('/api/recommendations')
    if response.status_code != 200:
        print("API test failed: GET /api/recommendations did not return status 200.")
        sys.exit(1)

# -------------------- Final Output --------------------
print("All good")
