#!/usr/bin/env python3
"""
Check category coverage - why categories don't sum to total dreams
"""

import sqlite3

def check_categories_coverage():
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
    # Total dreams
    cursor.execute("SELECT COUNT(*) FROM dreams")
    total_dreams = cursor.fetchone()[0]
    print(f"Total dreams in database: {total_dreams:,}")
    
    # Dreams with category_1
    cursor.execute("SELECT COUNT(*) FROM dreams WHERE category_1 IS NOT NULL AND category_1 != ''")
    with_category1 = cursor.fetchone()[0]
    print(f"Dreams with category_1: {with_category1:,}")
    
    # Dreams without category_1
    cursor.execute("SELECT COUNT(*) FROM dreams WHERE category_1 IS NULL OR category_1 = ''")
    without_category1 = cursor.fetchone()[0]
    print(f"Dreams WITHOUT category_1: {without_category1:,}")
    
    # Check sum of all categories
    cursor.execute("""
        SELECT SUM(count) as total FROM (
            SELECT category_1, COUNT(*) as count
            FROM dreams 
            WHERE category_1 IS NOT NULL AND category_1 != ''
            GROUP BY category_1
        )
    """)
    sum_categories = cursor.fetchone()[0]
    print(f"\nSum of all category counts: {sum_categories:,}")
    
    # Check unique categories
    cursor.execute("""
        SELECT COUNT(DISTINCT category_1) 
        FROM dreams 
        WHERE category_1 IS NOT NULL AND category_1 != ''
    """)
    unique_categories = cursor.fetchone()[0]
    print(f"Number of unique categories: {unique_categories}")
    
    # Check top categories
    print("\nTop 10 categories by count:")
    cursor.execute("""
        SELECT category_1, COUNT(*) as count
        FROM dreams 
        WHERE category_1 IS NOT NULL AND category_1 != ''
        GROUP BY category_1
        ORDER BY count DESC
        LIMIT 10
    """)
    for category, count in cursor.fetchall():
        print(f"  {category}: {count:,}")
    
    # Check for duplicate counting or missing data
    print("\n--- Checking for issues ---")
    
    # Check if there are dreams with normalized_title but no category
    cursor.execute("""
        SELECT COUNT(*) 
        FROM dreams 
        WHERE normalized_title_v3 IS NOT NULL 
        AND normalized_title_v3 != ''
        AND (category_1 IS NULL OR category_1 = '')
    """)
    titled_no_category = cursor.fetchone()[0]
    print(f"Dreams with title but NO category: {titled_no_category:,}")
    
    # Sample some dreams without categories
    if titled_no_category > 0:
        print("\nSample dreams with title but no category:")
        cursor.execute("""
            SELECT id, normalized_title_v3, age_at_dream
            FROM dreams 
            WHERE normalized_title_v3 IS NOT NULL 
            AND normalized_title_v3 != ''
            AND (category_1 IS NULL OR category_1 = '')
            LIMIT 5
        """)
        for dream_id, title, age in cursor.fetchall():
            print(f"  ID {dream_id}: '{title}' (age: {age})")
    
    conn.close()
    
    print(f"\n📊 Summary:")
    print(f"  - Total dreams: {total_dreams:,}")
    print(f"  - With categories: {with_category1:,} ({with_category1/total_dreams*100:.1f}%)")
    print(f"  - Without categories: {without_category1:,} ({without_category1/total_dreams*100:.1f}%)")
    print(f"  - Missing: {total_dreams - with_category1:,} dreams don't appear in category analysis!")

if __name__ == "__main__":
    check_categories_coverage()