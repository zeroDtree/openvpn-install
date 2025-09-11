#!/usr/bin/env python3
"""
User Management Script for OpenVPN Client Management System
"""

import sqlite3
import sys
import getpass
import csv
import argparse
import os
from werkzeug.security import generate_password_hash
from config import config
from db_init import init_db, get_db_connection


def list_users():
    """List all users"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, is_admin FROM users ORDER BY username")
    users = cursor.fetchall()

    print("\nUser List:")
    print("-" * 50)
    print(f"{'ID':<5} {'Username':<20} {'Admin':<10}")
    print("-" * 50)

    for user in users:
        admin_status = "Yes" if user[2] else "No"
        print(f"{user[0]:<5} {user[1]:<20} {admin_status:<10}")
    print("-" * 50)
    print(f"Total users: {len(users)}")

    conn.close()


def add_user():
    """Add new user"""
    username = input("Please enter username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return

    password = getpass.getpass("Please enter password: ")
    if not password:
        print("Password cannot be empty!")
        return

    is_admin_input = input("Is admin? (y/N): ").strip().lower()
    is_admin = is_admin_input in ["y", "yes"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, is_admin) 
            VALUES (?, ?, ?)
        """,
            (username, password_hash, is_admin),
        )

        conn.commit()
        print(f"User '{username}' added successfully!")

    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists!")
    except Exception as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()


def delete_user():
    """Delete user"""
    list_users()

    try:
        user_id = int(input("\nPlease enter user ID to delete: "))
    except ValueError:
        print("Please enter a valid user ID!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        print("User does not exist!")
        conn.close()
        return

    # Confirm deletion
    confirm = input(f"Are you sure to delete user '{user[0]}'? (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Delete operation cancelled")
        conn.close()
        return

    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print(f"User '{user[0]}' deleted successfully!")
    except Exception as e:
        print(f"Error deleting user: {e}")
    finally:
        conn.close()


def change_password():
    """Change user password"""
    list_users()

    try:
        user_id = int(input("\nPlease enter user ID to change password: "))
    except ValueError:
        print("Please enter a valid user ID!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        print("User does not exist!")
        conn.close()
        return

    new_password = getpass.getpass(f"Please enter new password for user '{user[0]}': ")
    if not new_password:
        print("Password cannot be empty!")
        conn.close()
        return

    try:
        password_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        conn.commit()
        print(f"Password for user '{user[0]}' changed successfully!")
    except Exception as e:
        print(f"Error changing password: {e}")
    finally:
        conn.close()


def toggle_admin():
    """Toggle user admin status"""
    list_users()

    try:
        user_id = int(input("\nPlease enter user ID to modify: "))
    except ValueError:
        print("Please enter a valid user ID!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT username, is_admin FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        print("User does not exist!")
        conn.close()
        return

    username, current_admin = user
    new_admin = not current_admin
    admin_status = "admin" if new_admin else "regular user"

    confirm = input(f"Are you sure to set user '{username}' as {admin_status}? (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Modification cancelled")
        conn.close()
        return

    try:
        cursor.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_admin, user_id))
        conn.commit()
        print(f"User '{username}' has been set as {admin_status}!")
    except Exception as e:
        print(f"Error modifying user status: {e}")
    finally:
        conn.close()


def import_users_from_csv(csv_file, dry_run=False):
    """Import users from CSV file"""
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' does not exist!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    success_count = 0
    error_count = 0
    skipped_count = 0

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            # Detect CSV format
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(file, delimiter=delimiter)

            # Check required fields
            required_fields = ["username", "password"]
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"Error: CSV file must contain the following fields: {', '.join(required_fields)}")
                print(f"Current fields: {', '.join(reader.fieldnames)}")
                return

            print(f"Starting to import users from file: {csv_file}")
            if dry_run:
                print("🔍 Preview mode - will not actually import users")
            print("-" * 80)

            for row_num, row in enumerate(reader, start=2):  # Start from row 2 (row 1 is header)
                try:
                    username = row["username"].strip()
                    password = row["password"].strip()

                    if not username or not password:
                        print(f"Row {row_num}: Skip - username or password is empty")
                        skipped_count += 1
                        continue

                    # Check if user already exists
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        print(f"Row {row_num}: Skip - user '{username}' already exists")
                        skipped_count += 1
                        continue

                    # Parse optional fields
                    is_admin = row.get("is_admin", "no").strip().lower() in ["yes", "y", "true", "1"]
                    email = row.get("email", "").strip()
                    full_name = row.get("full_name", "").strip()
                    department = row.get("department", "").strip()
                    notes = row.get("notes", "").strip()

                    if dry_run:
                        print(f"Row {row_num}: Will import user '{username}' (Admin: {'Yes' if is_admin else 'No'})")
                    else:
                        # Insert user
                        password_hash = generate_password_hash(password)
                        cursor.execute(
                            """
                            INSERT INTO users (username, password_hash, is_admin) 
                            VALUES (?, ?, ?)
                        """,
                            (username, password_hash, is_admin),
                        )

                        print(f"Row {row_num}: Successfully imported user '{username}'")

                    success_count += 1

                except Exception as e:
                    print(f"Row {row_num}: Error - {e}")
                    error_count += 1

            if not dry_run:
                conn.commit()

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        error_count += 1
    finally:
        conn.close()

    # Show import results
    print("-" * 80)
    print(f"Import completed:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ⚠️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")

    if dry_run and success_count > 0:
        print(f"\n💡 Preview completed, will import {success_count} users, please run:")
        print(f"   python3 manage_users.py --import-csv {csv_file}")


def update_users_from_csv(csv_file, dry_run=False):
    """Update existing users from CSV file"""
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' does not exist!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    success_count = 0
    error_count = 0
    skipped_count = 0

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            # Detect CSV format
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(file, delimiter=delimiter)

            # Check required fields
            required_fields = ["username"]
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"Error: CSV file must contain the following fields: {', '.join(required_fields)}")
                print(f"Current fields: {', '.join(reader.fieldnames)}")
                return

            print(f"Starting to update users from file: {csv_file}")
            if dry_run:
                print("🔍 Preview mode - will not actually update users")
            print("-" * 80)

            for row_num, row in enumerate(reader, start=2):  # Start from row 2 (row 1 is header)
                try:
                    username = row["username"].strip()

                    if not username:
                        print(f"Row {row_num}: Skip - username is empty")
                        skipped_count += 1
                        continue

                    # Check if user exists
                    cursor.execute("SELECT id, is_admin FROM users WHERE username = ?", (username,))
                    existing_user = cursor.fetchone()
                    
                    if not existing_user:
                        print(f"Row {row_num}: Skip - user '{username}' does not exist (use import to create new users)")
                        skipped_count += 1
                        continue

                    user_id, current_admin = existing_user

                    # Parse fields to update
                    password = row.get("password", "").strip()
                    is_admin = row.get("is_admin", "").strip().lower() in ["yes", "y", "true", "1"]
                    email = row.get("email", "").strip()
                    full_name = row.get("full_name", "").strip()
                    department = row.get("department", "").strip()
                    notes = row.get("notes", "").strip()

                    # Prepare update fields
                    update_fields = []
                    update_values = []

                    # Update password if provided
                    if password:
                        password_hash = generate_password_hash(password)
                        update_fields.append("password_hash = ?")
                        update_values.append(password_hash)

                    # Update admin status if provided
                    if row.get("is_admin", "").strip():  # Only update if explicitly provided
                        update_fields.append("is_admin = ?")
                        update_values.append(is_admin)

                    # Add user_id for WHERE clause
                    update_values.append(user_id)

                    if not update_fields:
                        print(f"Row {row_num}: Skip - no fields to update for user '{username}'")
                        skipped_count += 1
                        continue

                    if dry_run:
                        changes = []
                        if password:
                            changes.append("password")
                        if row.get("is_admin", "").strip():
                            changes.append(f"admin status ({'Yes' if is_admin else 'No'})")
                        print(f"Row {row_num}: Will update user '{username}' - {', '.join(changes)}")
                    else:
                        # Update user
                        update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                        cursor.execute(update_sql, update_values)
                        print(f"Row {row_num}: Successfully updated user '{username}'")

                    success_count += 1

                except Exception as e:
                    print(f"Row {row_num}: Error - {e}")
                    error_count += 1

            if not dry_run:
                conn.commit()

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        error_count += 1
    finally:
        conn.close()

    # Show update results
    print("-" * 80)
    print(f"Update completed:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ⚠️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")

    if dry_run and success_count > 0:
        print(f"\n💡 Preview completed, will update {success_count} users, please run:")
        print(f"   python3 manage_users.py --update-csv {csv_file}")


def upsert_users_from_csv(csv_file, dry_run=False):
    """Upsert users from CSV file (insert if not exists, update if exists)"""
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' does not exist!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    success_count = 0
    error_count = 0
    skipped_count = 0
    insert_count = 0
    update_count = 0

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            # Detect CSV format
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(file, delimiter=delimiter)

            # Check required fields
            required_fields = ["username", "password"]
            if not all(field in reader.fieldnames for field in required_fields):
                print(f"Error: CSV file must contain the following fields: {', '.join(required_fields)}")
                print(f"Current fields: {', '.join(reader.fieldnames)}")
                return

            print(f"Starting to upsert users from file: {csv_file}")
            if dry_run:
                print("🔍 Preview mode - will not actually upsert users")
            print("-" * 80)

            for row_num, row in enumerate(reader, start=2):  # Start from row 2 (row 1 is header)
                try:
                    username = row["username"].strip()
                    password = row["password"].strip()

                    if not username or not password:
                        print(f"Row {row_num}: Skip - username or password is empty")
                        skipped_count += 1
                        continue

                    # Check if user exists
                    cursor.execute("SELECT id, is_admin FROM users WHERE username = ?", (username,))
                    existing_user = cursor.fetchone()

                    # Parse fields
                    is_admin = row.get("is_admin", "no").strip().lower() in ["yes", "y", "true", "1"]
                    email = row.get("email", "").strip()
                    full_name = row.get("full_name", "").strip()
                    department = row.get("department", "").strip()
                    notes = row.get("notes", "").strip()

                    if existing_user:
                        # User exists - update
                        user_id, current_admin = existing_user
                        
                        # Prepare update fields
                        update_fields = ["password_hash = ?"]
                        update_values = [generate_password_hash(password)]
                        
                        # Update admin status if provided
                        if row.get("is_admin", "").strip():  # Only update if explicitly provided
                            update_fields.append("is_admin = ?")
                            update_values.append(is_admin)
                        
                        # Add user_id for WHERE clause
                        update_values.append(user_id)

                        if dry_run:
                            changes = ["password"]
                            if row.get("is_admin", "").strip():
                                changes.append(f"admin status ({'Yes' if is_admin else 'No'})")
                            print(f"Row {row_num}: Will UPDATE user '{username}' - {', '.join(changes)}")
                        else:
                            # Update user
                            update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                            cursor.execute(update_sql, update_values)
                            print(f"Row {row_num}: Successfully UPDATED user '{username}'")
                        
                        update_count += 1
                    else:
                        # User doesn't exist - insert
                        if dry_run:
                            print(f"Row {row_num}: Will INSERT new user '{username}' (Admin: {'Yes' if is_admin else 'No'})")
                        else:
                            # Insert new user
                            password_hash = generate_password_hash(password)
                            cursor.execute(
                                """
                                INSERT INTO users (username, password_hash, is_admin) 
                                VALUES (?, ?, ?)
                            """,
                                (username, password_hash, is_admin),
                            )
                            print(f"Row {row_num}: Successfully INSERTED new user '{username}'")
                        
                        insert_count += 1

                    success_count += 1

                except Exception as e:
                    print(f"Row {row_num}: Error - {e}")
                    error_count += 1

            if not dry_run:
                conn.commit()

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        error_count += 1
    finally:
        conn.close()

    # Show upsert results
    print("-" * 80)
    print(f"Upsert completed:")
    print(f"  ✅ Success: {success_count}")
    print(f"    📝 Inserted: {insert_count}")
    print(f"    🔄 Updated: {update_count}")
    print(f"  ⚠️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")

    if dry_run and success_count > 0:
        print(f"\n💡 Preview completed, will upsert {success_count} users ({insert_count} insert, {update_count} update), please run:")
        print(f"   python3 manage_users.py --upsert-csv {csv_file}")


def export_users_to_csv(output_file):
    """Export users to CSV file"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT username, is_admin FROM users ORDER BY username")
        users = cursor.fetchall()

        if not users:
            print("No user data to export")
            return

        with open(output_file, "w", newline="", encoding="utf-8") as file:
            fieldnames = ["username", "password", "email", "full_name", "department", "is_admin", "notes"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for username, is_admin in users:
                writer.writerow(
                    {
                        "username": username,
                        "password": "",  # Password cannot be exported
                        "email": "",
                        "full_name": "",
                        "department": "",
                        "is_admin": "yes" if is_admin else "no",
                        "notes": "",
                    }
                )

        print(f"✅ Successfully exported {len(users)} users to file: {output_file}")
        print("Note: Password field is empty, needs to be set manually")

    except Exception as e:
        print(f"Error exporting users: {e}")
    finally:
        conn.close()


def main():
    """Main function - supports interactive and command line modes"""
    parser = argparse.ArgumentParser(description="OpenVPN Client Management System - User Management")
    parser.add_argument("--import-csv", type=str, help="Import users from CSV file")
    parser.add_argument("--update-csv", type=str, help="Update existing users from CSV file")
    parser.add_argument("--upsert-csv", type=str, help="Upsert users from CSV file (insert if not exists, update if exists)")
    parser.add_argument("--export-csv", type=str, help="Export users to CSV file")
    parser.add_argument("--preview-import", type=str, help="Preview CSV import (do not actually import)")
    parser.add_argument("--preview-update", type=str, help="Preview CSV update (do not actually update)")
    parser.add_argument("--preview-upsert", type=str, help="Preview CSV upsert (do not actually upsert)")
    parser.add_argument("--list-users", action="store_true", help="List all users")

    args = parser.parse_args()

    # Command line mode
    if args.import_csv:
        import_users_from_csv(args.import_csv, dry_run=False)
        return

    if args.update_csv:
        update_users_from_csv(args.update_csv, dry_run=False)
        return

    if args.upsert_csv:
        upsert_users_from_csv(args.upsert_csv, dry_run=False)
        return

    if args.preview_import:
        import_users_from_csv(args.preview_import, dry_run=True)
        return

    if args.preview_update:
        update_users_from_csv(args.preview_update, dry_run=True)
        return

    if args.preview_upsert:
        upsert_users_from_csv(args.preview_upsert, dry_run=True)
        return

    if args.export_csv:
        export_users_to_csv(args.export_csv)
        return

    if args.list_users:
        list_users()
        return

    # Interactive mode
    while True:
        print("\n" + "=" * 50)
        print("OpenVPN Client Management System - User Management")
        print("=" * 50)
        print("1. List all users")
        print("2. Add new user")
        print("3. Delete user")
        print("4. Change user password")
        print("5. Toggle admin status")
        print("6. Import users from CSV")
        print("7. Update users from CSV")
        print("8. Upsert users from CSV (insert/update)")
        print("9. Export users to CSV")
        print("0. Exit")
        print("-" * 50)

        choice = input("Please select operation (0-9): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            list_users()
        elif choice == "2":
            add_user()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            change_password()
        elif choice == "5":
            toggle_admin()
        elif choice == "6":
            csv_file = input("Please enter CSV file path: ").strip()
            if csv_file:
                preview = input("Preview import first? (y/N): ").strip().lower()
                if preview in ["y", "yes"]:
                    import_users_from_csv(csv_file, dry_run=True)
                    confirm = input("Confirm import? (y/N): ").strip().lower()
                    if confirm in ["y", "yes"]:
                        import_users_from_csv(csv_file, dry_run=False)
                else:
                    import_users_from_csv(csv_file, dry_run=False)
        elif choice == "7":
            csv_file = input("Please enter CSV file path: ").strip()
            if csv_file:
                preview = input("Preview update first? (y/N): ").strip().lower()
                if preview in ["y", "yes"]:
                    update_users_from_csv(csv_file, dry_run=True)
                    confirm = input("Confirm update? (y/N): ").strip().lower()
                    if confirm in ["y", "yes"]:
                        update_users_from_csv(csv_file, dry_run=False)
                else:
                    update_users_from_csv(csv_file, dry_run=False)
        elif choice == "8":
            csv_file = input("Please enter CSV file path: ").strip()
            if csv_file:
                preview = input("Preview upsert first? (y/N): ").strip().lower()
                if preview in ["y", "yes"]:
                    upsert_users_from_csv(csv_file, dry_run=True)
                    confirm = input("Confirm upsert? (y/N): ").strip().lower()
                    if confirm in ["y", "yes"]:
                        upsert_users_from_csv(csv_file, dry_run=False)
                else:
                    upsert_users_from_csv(csv_file, dry_run=False)
        elif choice == "9":
            output_file = input("Please enter output CSV file path: ").strip()
            if output_file:
                export_users_to_csv(output_file)
        else:
            print("Invalid choice, please try again!")


if __name__ == "__main__":
    main()
