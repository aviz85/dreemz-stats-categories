#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('dreams_complete.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT category_1, COUNT(*) as count
    FROM dreams 
    WHERE category_1 IS NOT NULL AND category_1 != ''
    GROUP BY category_1
    ORDER BY count DESC
''')

total_sum = 0
print('ALL CATEGORIES WITH COUNTS:')
print('=' * 50)
for category, count in cursor.fetchall():
    total_sum += count
    print(f'{category:30}: {count:,}')

print('=' * 50)
print(f'TOTAL SUM: {total_sum:,}')

cursor.execute('SELECT COUNT(*) FROM dreams')
db_total = cursor.fetchone()[0]
print(f'DB TOTAL:  {db_total:,}')
print(f'MATCH:     {"✅ YES" if total_sum == db_total else "❌ NO"}')

conn.close()