#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, date
from flask import Flask, request, jsonify, abort

# -------------------- Folder & Database Setup --------------------
def create_folders():
    """Creates required folders if they do not exist."""
    folders = ['data', 'logs', 'static', 'templates']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def init_db():
    """Initializes the SQLite database and creates necessary tables."""
    db_path = os.path.join('data', 'habit_tracker.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Create habits table
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            frequency TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            log_date DATE,
            status TEXT,
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

def get_db_connection():
    """Returns a connection to the SQLite database."""
    db_path = os.path.join('data', 'habit_tracker.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- Flask App & Endpoints --------------------
app = Flask(__name__)

@app.route('/api/habits', methods=['GET'])
def get_habits():
    """Retrieve all habits."""
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    habits_list = [dict(habit) for habit in habits]
    return jsonify(habits_list), 200

@app.route('/api/habits', methods=['POST'])
def create_habit():
    """Create a new habit."""
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Habit 'name' is required")
    name = data['name']
    description = data.get('description', '')
    frequency = data.get('frequency', '')
    category = data.get('category', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO habits (name, description, frequency, category)
        VALUES (?, ?, ?, ?)
    ''', (name, description, frequency, category))
    conn.commit()
    habit_id = cur.lastrowid
    conn.close()
    return jsonify({
        'id': habit_id, 
        'name': name, 
        'description': description, 
        'frequency': frequency, 
        'category': category
    }), 201

@app.route('/api/habits/<int:habit_id>', methods=['GET'])
def get_habit(habit_id):
    """Retrieve a specific habit by its ID."""
    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()
    conn.close()
    if habit is None:
        abort(404, description="Habit not found")
    return jsonify(dict(habit)), 200

@app.route('/api/habits/<int:habit_id>', methods=['PUT'])
def update_habit(habit_id):
    """Update an existing habit."""
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")
    fields = []
    values = []
    for key in ['name', 'description', 'frequency', 'category']:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        abort(400, description="No valid fields provided for update")
    values.append(habit_id)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'''
        UPDATE habits SET {", ".join(fields)} WHERE id = ?
    ''', tuple(values))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Habit updated successfully'}), 200

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    """Delete a habit by its ID."""
    conn = get_db_connection()
    conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Habit deleted successfully'}), 200

@app.route('/api/habits/<int:habit_id>/log', methods=['POST'])
def log_habit(habit_id):
    """Log a habit completion."""
    data = request.get_json() or {}
    status = data.get('status', 'completed')
    log_date = data.get('log_date', date.today().isoformat())
    
    # Verify habit exists
    conn = get_db_connection()
    habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()
    if habit is None:
        conn.close()
        abort(404, description="Habit not found")
    
    conn.execute('''
        INSERT INTO logs (habit_id, log_date, status)
        VALUES (?, ?, ?)
    ''', (habit_id, log_date, status))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Habit logged successfully'}), 201

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """
    Provide AI-based recommendations:
    For each habit, if it hasn't been logged today, recommend completing it.
    """
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    recommendations = []
    for habit in habits:
        habit_dict = dict(habit)
        habit_id = habit_dict['id']
        log = conn.execute('''
            SELECT log_date FROM logs
            WHERE habit_id = ?
            ORDER BY log_date DESC LIMIT 1
        ''', (habit_id,)).fetchone()
        if log:
            last_log = datetime.strptime(log['log_date'], '%Y-%m-%d').date()
        else:
            last_log = None
        
        if not last_log or (date.today() - last_log).days >= 1:
            recommendations.append({
                'habit_id': habit_id,
                'recommendation': f"Don't forget to complete your habit: {habit_dict['name']} today!"
            })
    conn.close()
    return jsonify(recommendations), 200

# -------------------- Main Execution --------------------
if __name__ == '__main__':
    create_folders()
    init_db()
    # Start the Flask server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
