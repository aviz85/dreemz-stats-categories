#!/usr/bin/env python3
"""
Check how age filtering affects category totals
"""

import sqlite3

def check_age_filtering():
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
    # Check age distribution
    print("=== AGE DISTRIBUTION ===")
    cursor.execute("SELECT MIN(age_at_dream), MAX(age_at_dream), AVG(age_at_dream) FROM dreams WHERE age_at_dream IS NOT NULL")
    min_age, max_age, avg_age = cursor.fetchone()
    print(f"Age range: {min_age} - {max_age} (avg: {avg_age:.1f})")
    
    cursor.execute("SELECT COUNT(*) FROM dreams WHERE age_at_dream IS NULL")
    null_ages = cursor.fetchone()[0]
    print(f"Dreams with NULL age: {null_ages:,}")
    
    # Check different age filters
    print("\n=== CATEGORY TOTALS BY AGE FILTER ===")
    
    age_ranges = [
        (3, 125, "All ages (3-125)"),
        (13, 60, "Default filter (13-60)"),
        (0, 100, "Wide range (0-100)"),
        (18, 65, "Adult range (18-65)")
    ]
    
    for min_age_filter, max_age_filter, label in age_ranges:
        cursor.execute("""
            SELECT SUM(count) FROM (
                SELECT category_1, COUNT(*) as count
                FROM dreams 
                WHERE category_1 IS NOT NULL AND category_1 != ''
                AND age_at_dream >= ? AND age_at_dream <= ?
                GROUP BY category_1
            )
        """, (min_age_filter, max_age_filter))
        
        total_in_range = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM dreams WHERE age_at_dream >= ? AND age_at_dream <= ?", 
                      (min_age_filter, max_age_filter))
        total_dreams_in_range = cursor.fetchone()[0]
        
        print(f"{label:20}: {total_in_range:,} dreams in categories ({total_dreams_in_range:,} total dreams)")
    
    # Check what the current default filter (13-60) excludes
    print(f"\n=== WHAT GETS EXCLUDED BY DEFAULT FILTER (13-60) ===")
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN age_at_dream < 13 THEN 'Under 13'
                WHEN age_at_dream > 60 THEN 'Over 60'
                ELSE 'Included (13-60)'
            END as age_group,
            COUNT(*) as count
        FROM dreams 
        WHERE age_at_dream IS NOT NULL
        GROUP BY 
            CASE 
                WHEN age_at_dream < 13 THEN 'Under 13'
                WHEN age_at_dream > 60 THEN 'Over 60'
                ELSE 'Included (13-60)'
            END
        ORDER BY count DESC
    """)
    
    for age_group, count in cursor.fetchall():
        percentage = count / 115624 * 100
        print(f"  {age_group:15}: {count:,} dreams ({percentage:.1f}%)")
    
    # Show top categories that get excluded
    print(f"\n=== TOP CATEGORIES IN EXCLUDED AGES ===")
    
    print("Under 13:")
    cursor.execute("""
        SELECT category_1, COUNT(*) as count
        FROM dreams 
        WHERE age_at_dream < 13 AND category_1 IS NOT NULL
        GROUP BY category_1
        ORDER BY count DESC
        LIMIT 5
    """)
    for category, count in cursor.fetchall():
        print(f"  {category}: {count:,}")
    
    print("\nOver 60:")
    cursor.execute("""
        SELECT category_1, COUNT(*) as count
        FROM dreams 
        WHERE age_at_dream > 60 AND category_1 IS NOT NULL
        GROUP BY category_1
        ORDER BY count DESC
        LIMIT 5
    """)
    for category, count in cursor.fetchall():
        print(f"  {category}: {count:,}")
    
    conn.close()

if __name__ == "__main__":
    check_age_filtering()