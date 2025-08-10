#!/usr/bin/env python3
"""
Export SQLite data to CSV for PostgreSQL import
Run this from wherever your dreams database is located
"""

import sqlite3
import csv
import os

def find_database():
    """Find the dreams database file"""
    possible_names = [
        'dreams_complete.db',
        'dreams.db', 
        'database.db',
        'dreams_complete.db.backup'
    ]
    
    for name in possible_names:
        if os.path.exists(name):
            return name
    
    # If not found, ask user
    print("❌ Database file not found. Please provide the path:")
    print("   Tried: " + ", ".join(possible_names))
    
    db_path = input("Enter database file path: ").strip()
    if os.path.exists(db_path):
        return db_path
    
    return None

def export_to_csv():
    """Export dreams table to CSV"""
    
    db_path = find_database()
    if not db_path:
        print("❌ No database file found")
        return False
    
    print(f"📤 Exporting data from: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"   Available tables: {[t[0] for t in tables]}")
        
        # Try to find the dreams table
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='dreams'
        """)
        schema = cursor.fetchone()
        
        if not schema:
            print("❌ No 'dreams' table found")
            return False
        
        print(f"   Found dreams table")
        
        # Get column names
        cursor.execute("PRAGMA table_info(dreams)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"   Columns: {column_names}")
        
        # Prepare SELECT query for the columns we need
        required_columns = [
            'original_id', 'username', 'age_at_dream', 'normalized_title_v3',
            'category_1', 'subcategory_1', 'category_2', 'subcategory_2',
            'category_3', 'subcategory_3'
        ]
        
        # Use available columns that match our requirements
        select_columns = []
        csv_headers = []
        
        for col in required_columns:
            if col in column_names:
                select_columns.append(col)
                csv_headers.append(col)
            else:
                # Use NULL for missing columns
                select_columns.append(f"NULL as {col}")
                csv_headers.append(col)
        
        # Get all data
        query = f"SELECT {', '.join(select_columns)} FROM dreams ORDER BY rowid"
        cursor.execute(query)
        
        # Write to CSV
        with open('dreams_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(csv_headers)
            
            # Data in batches
            batch_size = 1000
            total_rows = 0
            
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                
                # Clean up the data (handle None values)
                clean_rows = []
                for row in rows:
                    clean_row = []
                    for value in row:
                        if value is None:
                            clean_row.append('')
                        else:
                            clean_row.append(str(value))
                    clean_rows.append(clean_row)
                
                writer.writerows(clean_rows)
                total_rows += len(rows)
                print(f"   Exported {total_rows} rows...")
        
        conn.close()
        
        # Check file size
        file_size = os.path.getsize('dreams_export.csv') / (1024 * 1024)  # MB
        print(f"✅ Export complete!")
        print(f"   File: dreams_export.csv")
        print(f"   Size: {file_size:.1f} MB")
        print(f"   Rows: {total_rows}")
        
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Dreams Database CSV Exporter")
    print("=" * 40)
    
    success = export_to_csv()
    
    if success:
        print("\n📋 Next steps:")
        print("1. Upload dreams_export.csv to your Render service")
        print("2. Run: python import_from_csv.py")
        print("3. Your PostgreSQL database will be populated!")
    else:
        print("\n❌ Export failed. Please check your database file.")