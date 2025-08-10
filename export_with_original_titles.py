#!/usr/bin/env python3
"""
Export dreams data with original titles from SQLite to CSV
This will include the original Hebrew titles that were missing from the previous export
"""

import sqlite3
import csv
import os

def export_dreams_with_original_titles():
    """Export dreams data including original titles"""
    
    print("🔄 Exporting dreams with original titles from SQLite...")
    
    # Connect to SQLite
    print("1. Connecting to SQLite database...")
    if not os.path.exists('dreams_complete.db'):
        print("❌ Error: dreams_complete.db not found!")
        return False
        
    conn = sqlite3.connect('dreams_complete.db')
    cursor = conn.cursor()
    
    # Check how many records we have
    cursor.execute("SELECT COUNT(*) FROM dreams WHERE normalized_title_v3 IS NOT NULL")
    total_count = cursor.fetchone()[0]
    print(f"2. Found {total_count:,} dreams with normalized titles")
    
    # Export data with original titles
    print("3. Exporting data...")
    cursor.execute("""
        SELECT 
            original_id,
            username,
            age_at_dream,
            title as original_title,
            normalized_title_v3,
            category_1,
            subcategory_1,
            category_2,
            subcategory_2,
            category_3,
            subcategory_3
        FROM dreams 
        WHERE normalized_title_v3 IS NOT NULL
        ORDER BY original_id
    """)
    
    # Write to CSV
    output_file = 'dreams_export_with_titles.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            'original_id',
            'username', 
            'age_at_dream',
            'original_title',
            'normalized_title_v3',
            'category_1',
            'subcategory_1', 
            'category_2',
            'subcategory_2',
            'category_3',
            'subcategory_3'
        ])
        
        # Write data
        count = 0
        for row in cursor:
            writer.writerow(row)
            count += 1
            if count % 10000 == 0:
                print(f"   Exported {count:,} records...")
    
    conn.close()
    
    print(f"✅ Export complete! {count:,} dreams exported to {output_file}")
    return True

if __name__ == "__main__":
    success = export_dreams_with_original_titles()
    if not success:
        exit(1)