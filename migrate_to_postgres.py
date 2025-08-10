#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this script after setting up your Render PostgreSQL database
"""

import sqlite3
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to SQLite
    print("1. Connecting to SQLite database...")
    sqlite_conn = sqlite3.connect('dreams_complete.db.backup')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    print("2. Connecting to PostgreSQL database...")
    postgres_conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    postgres_cursor = postgres_conn.cursor()
    
    # Create table structure in PostgreSQL
    print("3. Creating table structure...")
    postgres_cursor.execute("""
        CREATE TABLE IF NOT EXISTS dreams (
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
    
    # Create indexes for performance
    print("4. Creating indexes...")
    postgres_cursor.execute("CREATE INDEX IF NOT EXISTS idx_normalized_title ON dreams(normalized_title_v3);")
    postgres_cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_1 ON dreams(category_1);")
    postgres_cursor.execute("CREATE INDEX IF NOT EXISTS idx_subcategory_1 ON dreams(subcategory_1);")
    postgres_cursor.execute("CREATE INDEX IF NOT EXISTS idx_age ON dreams(age_at_dream);")
    
    # Get data from SQLite
    print("5. Reading data from SQLite...")
    sqlite_cursor.execute("""
        SELECT 
            original_id,
            username,
            age_at_dream,
            normalized_title_v3,
            category_1,
            subcategory_1,
            category_2,
            subcategory_2,
            category_3,
            subcategory_3
        FROM dreams
    """)
    
    # Insert data into PostgreSQL in batches
    print("6. Inserting data into PostgreSQL...")
    batch_size = 1000
    total_rows = 0
    
    while True:
        rows = sqlite_cursor.fetchmany(batch_size)
        if not rows:
            break
        
        # Prepare data for PostgreSQL
        postgres_data = []
        for row in rows:
            postgres_data.append(row)
        
        # Insert batch
        postgres_cursor.executemany("""
            INSERT INTO dreams (
                original_id, username, age_at_dream, normalized_title_v3,
                category_1, subcategory_1, category_2, subcategory_2,
                category_3, subcategory_3
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, postgres_data)
        
        total_rows += len(rows)
        print(f"   Inserted {total_rows} rows...")
    
    # Commit changes
    postgres_conn.commit()
    
    # Verify migration
    print("7. Verifying migration...")
    postgres_cursor.execute("SELECT COUNT(*) FROM dreams")
    pg_count = postgres_cursor.fetchone()[0]
    
    sqlite_cursor.execute("SELECT COUNT(*) FROM dreams")
    sqlite_count = sqlite_cursor.fetchone()[0]
    
    print(f"   SQLite rows: {sqlite_count}")
    print(f"   PostgreSQL rows: {pg_count}")
    
    if pg_count == sqlite_count:
        print("✅ Migration successful!")
    else:
        print("❌ Migration incomplete - row counts don't match")
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    
    print("🎉 Migration completed!")

if __name__ == '__main__':
    # Check for required environment variable
    if not os.environ.get('DATABASE_URL'):
        print("❌ Please set the DATABASE_URL environment variable with your PostgreSQL connection string")
        print("   Example: export DATABASE_URL='postgresql://user:password@host:port/database'")
        exit(1)
    
    migrate_data()