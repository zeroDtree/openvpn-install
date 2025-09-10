#!/usr/bin/env python3
"""
Database initialization module for OpenVPN Client Management System
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import config

def init_db():
    """Initialize database"""
    # Ensure database directory exists
    db_path = config['default'].DATABASE_PATH
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create client files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            assigned_to TEXT,
            assigned_date TEXT,
            notes TEXT,
            is_available BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create default admin user
    admin_password = generate_password_hash(config['default'].DEFAULT_ADMIN_PASSWORD)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, is_admin) 
        VALUES (?, ?, ?)
    ''', (config['default'].DEFAULT_ADMIN_USERNAME, admin_password, 1))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(config['default'].DATABASE_PATH)

def populate_client_files():
    """Add existing client files to database"""
    import glob
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get client file pattern
    pattern = os.path.join(config['default'].CLIENT_FILES_DIR, config['default'].CLIENT_FILE_PATTERN)
    client_files = glob.glob(pattern)
    
    for file_path in client_files:
        filename = os.path.basename(file_path)
        cursor.execute('''
            INSERT OR IGNORE INTO client_files (filename, is_available) 
            VALUES (?, ?)
        ''', (filename, 1))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # If running this file directly, initialize database
    print("Initializing database...")
    init_db()
    print("Database initialization completed!")
    
    print("Populating client files...")
    populate_client_files()
    print("Client files population completed!")
