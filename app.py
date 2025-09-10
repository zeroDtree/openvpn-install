#!/usr/bin/env python3
"""
OpenVPN Client Management Web Server
A simple web interface for managing OpenVPN client configuration file distribution
"""

import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import glob
from config import config
from db_init import init_db, populate_client_files, get_db_connection

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Database file path
DB_PATH = app.config['DATABASE_PATH']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_required(f):
    """Login decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['is_admin'] = user[2]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User file panel"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    current_user = session.get('username')
    
    # Get client files assigned to current user
    cursor.execute('''
        SELECT filename, assigned_to, assigned_date, notes, is_available 
        FROM client_files 
        WHERE assigned_to = ? AND is_available = 0
        ORDER BY filename
    ''', (current_user,))
    clients = cursor.fetchall()
    
    # Statistics - only show files assigned to current user
    assigned_count = len(clients)
    
    conn.close()
    
    return render_template('dashboard.html', 
                         clients=clients, 
                         assigned_count=assigned_count)


@app.route('/download/<filename>')
@login_required
def download_client(filename):
    """Download client file"""
    # Construct full file path
    file_path = os.path.join(app.config['CLIENT_FILES_DIR'], 'clients_ovpn', filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        flash('File does not exist!', 'error')
        return redirect(url_for('dashboard'))
    
    # Check user permissions
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT assigned_to, is_available FROM client_files WHERE filename = ?', (filename,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        assigned_to, is_available = result
        current_user = session.get('username')
        
        # Only the assigned user can download
        if is_available or assigned_to != current_user:
            logger.warning(f"Permission denied: User {current_user} tried to download {filename} (assigned to {assigned_to}, available: {is_available})")
            flash('You do not have permission to download this file!', 'error')
            return redirect(url_for('dashboard'))
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/api/clients')
@login_required
def api_clients():
    """API: Get client file list"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT filename, assigned_to, assigned_date, notes, is_available 
        FROM client_files 
        ORDER BY filename
    ''')
    clients = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'filename': client[0],
        'assigned_to': client[1],
        'assigned_date': client[2],
        'notes': client[3],
        'is_available': bool(client[4])
    } for client in clients])


if __name__ == '__main__':
    # Initialize database
    init_db()
    populate_client_files()
    
    # Start server
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
