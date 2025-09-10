#!/usr/bin/env python3
"""
Random User Generator for OpenVPN Client Management System
Generates random user information and saves to CSV file
"""

import csv
import random
import string
import argparse
import os
from datetime import datetime

def generate_random_string(length=8):
    """Generate random string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_username():
    """Generate random username"""
    prefixes = ['user', 'client', 'vpn', 'node', 'device', 'terminal', 'access', 'connect']
    prefix = random.choice(prefixes)
    suffix = generate_random_string(6)
    return f"{prefix}_{suffix}"

def generate_random_email():
    """Generate random email"""
    domains = ['example.com', 'test.local', 'vpn.local', 'client.local', 'user.local']
    username = generate_random_string(8)
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_random_name():
    """Generate random name"""
    first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 
                   'Ivy', 'Jack', 'Kate', 'Leo', 'Mia', 'Noah', 'Olivia', 'Paul', 
                   'Quinn', 'Ruby', 'Sam', 'Tina', 'Uma', 'Victor', 'Wendy', 'Xavier', 
                   'Yara', 'Zoe']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return f"{first_name} {last_name}"

def generate_random_department():
    """Generate random department"""
    departments = ['IT', 'HR', 'Finance', 'Marketing', 'Sales', 'Operations', 'Support', 
                   'Development', 'QA', 'DevOps', 'Security', 'Network', 'Admin', 
                   'Management', 'Research', 'Design']
    return random.choice(departments)

def generate_random_notes():
    """Generate random notes"""
    notes_templates = [
        'Remote worker',
        'Mobile user',
        'Office user',
        'Temporary access',
        'Contractor',
        'Guest user',
        'Test account',
        'Emergency access',
        'Backup user',
        'Special project'
    ]
    return random.choice(notes_templates)

def generate_users_csv(num_users, output_file, include_admin=False):
    """Generate user CSV file"""
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'password', 'email', 'full_name', 'department', 'is_admin', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write CSV header
        writer.writeheader()
        
        # Generate user data
        for i in range(num_users):
            username = generate_random_username()
            password = generate_random_string(12)  # 12-character random password
            email = generate_random_email()
            full_name = generate_random_name()
            department = generate_random_department()
            notes = generate_random_notes()
            
            # Set first user as admin (if specified)
            is_admin = 'yes' if (include_admin and i == 0) else 'no'
            
            writer.writerow({
                'username': username,
                'password': password,
                'email': email,
                'full_name': full_name,
                'department': department,
                'is_admin': is_admin,
                'notes': notes
            })
    
    print(f"✅ Successfully generated {num_users} user records to file: {output_file}")
    print(f"📁 File contains fields: {', '.join(fieldnames)}")

def main():
    parser = argparse.ArgumentParser(description='Generate random user information CSV file')
    parser.add_argument('-n', '--num-users', type=int, default=50, 
                       help='Number of users to generate (default: 50)')
    parser.add_argument('-o', '--output', type=str, default='random_users.csv',
                       help='Output CSV filename (default: random_users.csv)')
    parser.add_argument('--include-admin', action='store_true',
                       help='Include one admin user')
    parser.add_argument('--preview', action='store_true',
                       help='Preview generated user information (do not save file)')
    
    args = parser.parse_args()
    
    if args.preview:
        print("Preview of generated user information:")
        print("-" * 80)
        print(f"{'Username':<15} {'Password':<12} {'Email':<25} {'Name':<15} {'Department':<10} {'Admin':<8}")
        print("-" * 80)
        
        for i in range(min(10, args.num_users)):  # Only show first 10
            username = generate_random_username()
            password = generate_random_string(12)
            email = generate_random_email()
            full_name = generate_random_name()
            department = generate_random_department()
            is_admin = 'Yes' if (args.include_admin and i == 0) else 'No'
            
            print(f"{username:<15} {password:<12} {email:<25} {full_name:<15} {department:<10} {is_admin:<8}")
        
        if args.num_users > 10:
            print(f"... and {args.num_users - 10} more users")
        
        print("\nContinue to generate complete CSV file? (y/N): ", end='')
        if input().strip().lower() not in ['y', 'yes']:
            print("Generation cancelled")
            return
    
    # Generate CSV file
    generate_users_csv(args.num_users, args.output, args.include_admin)
    
    # Show usage instructions
    print("\n📋 Usage Instructions:")
    print("1. You can use the following command to import users to the system:")
    print(f"   python3 manage_users.py --import-csv {args.output}")
    print("2. CSV file format:")
    print("   - username: Username (required)")
    print("   - password: Password (required)")
    print("   - email: Email address (optional)")
    print("   - full_name: Full name (optional)")
    print("   - department: Department (optional)")
    print("   - is_admin: Is admin (yes/no, default: no)")
    print("   - notes: Notes (optional)")

if __name__ == '__main__':
    main()
