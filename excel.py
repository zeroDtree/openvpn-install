#!/usr/bin/env python3
"""
Script to extract usernames from users.csv and create an Excel file
"""

import pandas as pd
import os

def extract_usernames_to_excel():
    """
    Extract usernames from users.csv and create a new Excel file
    """
    # Read the CSV file
    csv_file = 'users.csv'
    excel_file = 'usernames.xlsx'
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Extract only the username column
        usernames_df = df[['username']].copy()
        
        # Add a serial number column for better organization
        usernames_df.insert(0, 'serial_number', range(1, len(usernames_df) + 1))
        
        # Create Excel file
        usernames_df.to_excel(excel_file, index=False, sheet_name='Usernames')
        
        print(f"Successfully extracted {len(usernames_df)} usernames to {excel_file}")
        print(f"Excel file contains columns: Serial Number, Username")
        
        # Display first few rows as preview
        print("\nPreview of the Excel file:")
        print(usernames_df.head(10).to_string(index=False))
        
    except FileNotFoundError:
        print(f"Error: {csv_file} not found in the current directory")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    extract_usernames_to_excel()
