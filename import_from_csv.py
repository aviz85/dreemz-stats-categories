#!/usr/bin/env python3
"""
Import CSV data to PostgreSQL (run on Render after uploading CSV)
"""

import psycopg2
import os
import csv

def import_from_csv():
    """Import dreams data from CSV to PostgreSQL"""
    
    print("📥 Importing CSV data to PostgreSQL...")
    print("=" * 40)
    
    # Connect to PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("   Make sure this script is running on Render with PostgreSQL configured")
        return False
    
    if not os.path.exists('dreams_export.csv'):
        print("❌ dreams_export.csv not found")
        print("   Please upload the CSV file first")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL")
        
        # Create table structure
        print("1. Creating table structure...")
        cursor.execute("""
            DROP TABLE IF EXISTS dreams CASCADE;
            CREATE TABLE dreams (
                id SERIAL PRIMARY KEY,
                original_id INTEGER,
                username VARCHAR(255),
                age_at_dream INTEGER,
                normalized_title_v3 TEXT,
                category_1 TEXT,
                subcategory_1 TEXT,
                category_2 TEXT,
                subcategory_2 TEXT,
                category_3 TEXT,
                subcategory_3 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("   ✅ Table created")
        
        # Import CSV data
        print("2. Importing CSV data...")
        with open('dreams_export.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header
            header = next(reader)
            print(f"   CSV headers: {header}")
            
            # Insert data in batches
            batch_size = 1000
            batch = []
            total_rows = 0
            
            for row in reader:
                # Convert empty strings to None for proper NULL handling
                clean_row = []
                for value in row:
                    if value == '' or value == 'None':
                        clean_row.append(None)
                    else:
                        # Try to convert integers
                        if value.isdigit():
                            clean_row.append(int(value))
                        else:
                            clean_row.append(value)
                
                batch.append(clean_row)
                
                if len(batch) >= batch_size:
                    # Insert batch
                    cursor.executemany("""
                        INSERT INTO dreams (
                            original_id, username, age_at_dream, normalized_title_v3,
                            category_1, subcategory_1, category_2, subcategory_2,
                            category_3, subcategory_3
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, batch)
                    
                    total_rows += len(batch)
                    print(f"   Imported {total_rows} rows...")
                    batch = []
            
            # Insert remaining rows
            if batch:
                cursor.executemany("""
                    INSERT INTO dreams (
                        original_id, username, age_at_dream, normalized_title_v3,
                        category_1, subcategory_1, category_2, subcategory_2,
                        category_3, subcategory_3
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, batch)
                total_rows += len(batch)
        
        print(f"   ✅ Imported {total_rows} rows")
        
        # Create indexes for performance
        print("3. Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_normalized_title ON dreams(normalized_title_v3)",
            "CREATE INDEX IF NOT EXISTS idx_category_1 ON dreams(category_1)", 
            "CREATE INDEX IF NOT EXISTS idx_subcategory_1 ON dreams(subcategory_1)",
            "CREATE INDEX IF NOT EXISTS idx_age ON dreams(age_at_dream)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        print("   ✅ Indexes created")
        
        # Commit all changes
        conn.commit()
        print("4. ✅ All changes committed")
        
        # Verify import
        cursor.execute("SELECT COUNT(*) FROM dreams")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT normalized_title_v3) FROM dreams WHERE normalized_title_v3 IS NOT NULL")
        unique_titles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category_1) FROM dreams WHERE category_1 IS NOT NULL")
        categories = cursor.fetchone()[0]
        
        print(f"\n🎉 Import successful!")
        print(f"   Total dreams: {count:,}")
        print(f"   Unique titles: {unique_titles:,}")
        print(f"   Categories: {categories}")
        
        # Test a query
        cursor.execute("SELECT normalized_title_v3, COUNT(*) FROM dreams WHERE normalized_title_v3 IS NOT NULL GROUP BY normalized_title_v3 ORDER BY COUNT(*) DESC LIMIT 3")
        top_dreams = cursor.fetchall()
        
        print(f"\n📊 Top dreams:")
        for dream, count in top_dreams:
            print(f"   '{dream}': {count} dreams")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == '__main__':
    print("🔄 Dreams Database CSV Importer")
    
    success = import_from_csv()
    
    if success:
        print(f"\n✅ Database ready! Your dream analytics dashboard should now work.")
        print(f"   Access your dashboard at your Render URL")
    else:
        print(f"\n❌ Import failed. Check the error messages above.")