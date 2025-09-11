#!/usr/bin/env python3
"""
File Assignment Script for OpenVPN Client Management System
Assign client configuration files to users
"""

import sqlite3
import argparse
import os
import glob
from datetime import datetime
from config import config
from db_init import init_db, get_db_connection

def list_available_files():
    """List all available client files"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT filename, assigned_to, is_available 
        FROM client_files 
        ORDER BY filename
    ''')
    files = cursor.fetchall()
    
    print("\nClient file status:")
    print("-" * 80)
    print(f"{'Filename':<20} {'Status':<15} {'Assigned to':<20}")
    print("-" * 80)
    
    for file_info in files:
        filename, assigned_to, is_available = file_info
        status = "Available" if is_available else "Assigned"
        assigned = assigned_to if assigned_to else "-"
        print(f"{filename:<20} {status:<15} {assigned:<20}")
    
    conn.close()

def list_users():
    """List all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, is_admin FROM users ORDER BY username')
    users = cursor.fetchall()
    
    print("\nUser list:")
    print("-" * 50)
    print(f"{'ID':<5} {'Username':<20} {'Admin':<10}")
    print("-" * 50)
    
    for user in users:
        admin_status = "Yes" if user[2] else "No"
        print(f"{user[0]:<5} {user[1]:<20} {admin_status:<10}")
    
    conn.close()
    return users

def assign_file_to_user(filename, username, notes=""):
    """Assign file to user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if file exists
        cursor.execute('SELECT assigned_to, is_available FROM client_files WHERE filename = ?', (filename,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Error: File '{filename}' does not exist!")
            return False
        
        assigned_to, is_available = result
        
        if not is_available:
            print(f"Error: File '{filename}' is already assigned to '{assigned_to}'!")
            return False
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            print(f"Error: User '{username}' does not exist!")
            return False
        
        # Assign file
        cursor.execute('''
            UPDATE client_files 
            SET assigned_to = ?, assigned_date = ?, notes = ?, is_available = 0 
            WHERE filename = ?
        ''', (username, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, filename))
        
        conn.commit()
        print(f"✅ Successfully assigned file '{filename}' to user '{username}'")
        return True
        
    except Exception as e:
        print(f"Error assigning file: {e}")
        return False
    finally:
        conn.close()

def unassign_file(filename):
    """Unassign file"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if file exists
        cursor.execute('SELECT assigned_to, is_available FROM client_files WHERE filename = ?', (filename,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Error: File '{filename}' does not exist!")
            return False
        
        assigned_to, is_available = result
        
        if is_available:
            print(f"File '{filename}' is already available!")
            return False
        
        # Unassign
        cursor.execute('''
            UPDATE client_files 
            SET assigned_to = NULL, assigned_date = NULL, notes = NULL, is_available = 1 
            WHERE filename = ?
        ''', (filename,))
        
        conn.commit()
        print(f"✅ Successfully unassigned file '{filename}' (was assigned to: {assigned_to})")
        return True
        
    except Exception as e:
        print(f"Error unassigning file: {e}")
        return False
    finally:
        conn.close()

def batch_assign_files(user_pattern, file_pattern, notes="", exclude_admin=True):
    """Batch assign files
    
    Args:
        user_pattern: Regex pattern to match users
        file_pattern: Regex pattern to match files
        notes: Optional notes for assignment
        exclude_admin: Whether to exclude admin user (default: True)
    """
    import re
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all users (optionally excluding admin)
        if exclude_admin:
            cursor.execute('SELECT username FROM users WHERE username != ?', ('admin',))
        else:
            cursor.execute('SELECT username FROM users')
        all_users = [row[0] for row in cursor.fetchall()]
        
        # Use standard regex to match users
        try:
            users = [user for user in all_users if re.match(user_pattern, user)]
        except re.error as e:
            print(f"User regex error: {e}")
            print(f"Please check regex pattern: '{user_pattern}'")
            return False
        
        if not users:
            print(f"No users found matching pattern '{user_pattern}'!")
            print(f"Available users: {', '.join(all_users[:10])}{'...' if len(all_users) > 10 else ''}")
            return False
        
        # Get all available files
        cursor.execute('SELECT filename FROM client_files WHERE is_available = 1')
        all_files = [row[0] for row in cursor.fetchall()]
        
        # Use standard regex to match files
        try:
            files = [file for file in all_files if re.match(file_pattern, file)]
        except re.error as e:
            print(f"File regex error: {e}")
            print(f"Please check regex pattern: '{file_pattern}'")
            return False
        
        if not files:
            print(f"No available files found matching pattern '{file_pattern}'!")
            print(f"Available files: {', '.join(all_files[:10])}{'...' if len(all_files) > 10 else ''}")
            return False
        
        print(f"Found {len(users)} users and {len(files)} available files")
        
        # Assign files in order
        assigned_count = 0
        for i, filename in enumerate(files):
            if i < len(users):
                username = users[i]
                if assign_file_to_user(filename, username, notes):
                    assigned_count += 1
        
        print(f"✅ Batch assignment completed, successfully assigned {assigned_count} files")
        return True
        
    except Exception as e:
        print(f"Error in batch assignment: {e}")
        return False
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='OpenVPN client file assignment tool')
    parser.add_argument('--list-files', action='store_true', help='List all file status')
    parser.add_argument('--list-users', action='store_true', help='List all users')
    parser.add_argument('--assign', nargs=2, metavar=('FILENAME', 'USERNAME'), 
                       help='Assign file to user')
    parser.add_argument('--unassign', type=str, help='Unassign file')
    parser.add_argument('--batch-assign', nargs=2, metavar=('USER_PATTERN', 'FILE_PATTERN'),
                       help='Batch assign files (using regex)')
    parser.add_argument('--notes', type=str, default='', help='Add notes')
    parser.add_argument('--include-admin', action='store_true', 
                       help='Include admin user in batch assignment (default: exclude admin)')
    
    args = parser.parse_args()
    
    if args.list_files:
        list_available_files()
    elif args.list_users:
        list_users()
    elif args.assign:
        filename, username = args.assign
        assign_file_to_user(filename, username, args.notes)
    elif args.unassign:
        unassign_file(args.unassign)
    elif args.batch_assign:
        user_pattern, file_pattern = args.batch_assign
        exclude_admin = not args.include_admin
        batch_assign_files(user_pattern, file_pattern, args.notes, exclude_admin)
    else:
        # Interactive mode
        while True:
            print("\n" + "="*50)
            print("OpenVPN Client File Assignment Tool")
            print("="*50)
            print("1. List file status")
            print("2. List users")
            print("3. Assign file to user")
            print("4. Unassign file")
            print("5. Batch assign files")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Please select operation (0-5): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                list_available_files()
            elif choice == '2':
                list_users()
            elif choice == '3':
                list_available_files()
                filename = input("Please enter filename: ").strip()
                list_users()
                username = input("Please enter username: ").strip()
                notes = input("Please enter notes (optional): ").strip()
                if filename and username:
                    assign_file_to_user(filename, username, notes)
            elif choice == '4':
                list_available_files()
                filename = input("Please enter filename to unassign: ").strip()
                if filename:
                    unassign_file(filename)
            elif choice == '5':
                print("Batch assignment examples:")
                print("  User pattern: user_.* (matches all users starting with user_)")
                print("  File pattern: client.*\\.ovpn (matches all .ovpn files starting with client)")
                print("  Match all: .* (matches all users/files)")
                user_pattern = input("Please enter user regex pattern: ").strip()
                file_pattern = input("Please enter file regex pattern: ").strip()
                notes = input("Please enter notes (optional): ").strip()
                include_admin = input("Include admin user? (y/N): ").strip().lower() in ['y', 'yes']
                exclude_admin = not include_admin
                if user_pattern and file_pattern:
                    batch_assign_files(user_pattern, file_pattern, notes, exclude_admin)
            else:
                print("Invalid choice, please try again!")

if __name__ == '__main__':
    main()
