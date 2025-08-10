#!/usr/bin/env python3
"""
Dream Analytics Dashboard - PostgreSQL Production Server with Import Feature
Serves the React frontend and provides API endpoints for dream analysis.
"""

import os
import psycopg2
import psycopg2.extras
import json
import csv
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global import status
import_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'message': 'Ready to import',
    'success': None,
    'error': None,
    'last_update': datetime.now().isoformat()
}

def get_db_connection():
    """Get PostgreSQL database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        # Fallback for local development
        return psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'dreams'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', ''),
            port=os.environ.get('DB_PORT', 5432)
        )

def run_import_in_background():
    """Run the CSV import in a background thread"""
    global import_status
    
    try:
        import_status['running'] = True
        import_status['message'] = 'Starting import...'
        import_status['progress'] = 0
        import_status['error'] = None
        
        # Check if CSV exists
        if not os.path.exists('dreams_export.csv'):
            raise Exception('CSV file not found. Please ensure dreams_export.csv is in the deployment.')
        
        # Connect to database
        import_status['message'] = 'Connecting to database...'
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table structure
        import_status['message'] = 'Creating table structure...'
        cursor.execute("""
            DROP TABLE IF EXISTS dreams CASCADE;
            CREATE TABLE dreams (
                id SERIAL PRIMARY KEY,
                original_id VARCHAR(255),
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
        
        # Count total rows for progress tracking
        import_status['message'] = 'Counting rows in CSV...'
        with open('dreams_export.csv', 'r', encoding='utf-8') as f:
            total_rows = sum(1 for line in f) - 1  # Subtract header
        
        import_status['total'] = total_rows
        import_status['message'] = f'Importing {total_rows:,} dreams...'
        
        # Import CSV data
        with open('dreams_export.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip header
            
            batch_size = 1000
            batch = []
            rows_imported = 0
            
            for row in reader:
                # Clean data
                clean_row = []
                for value in row:
                    if value == '' or value == 'None':
                        clean_row.append(None)
                    else:
                        try:
                            # Try to convert to integer for age
                            if 'age' in header[len(clean_row)] if len(clean_row) < len(header) else False:
                                clean_row.append(int(value) if value.isdigit() else value)
                            else:
                                clean_row.append(value)
                        except:
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
                    
                    rows_imported += len(batch)
                    import_status['progress'] = rows_imported
                    import_status['message'] = f'Imported {rows_imported:,} of {total_rows:,} dreams...'
                    import_status['last_update'] = datetime.now().isoformat()
                    
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
                rows_imported += len(batch)
                import_status['progress'] = rows_imported
        
        # Create indexes
        import_status['message'] = 'Creating indexes for performance...'
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_normalized_title ON dreams(normalized_title_v3)",
            "CREATE INDEX IF NOT EXISTS idx_category_1 ON dreams(category_1)",
            "CREATE INDEX IF NOT EXISTS idx_subcategory_1 ON dreams(subcategory_1)",
            "CREATE INDEX IF NOT EXISTS idx_age ON dreams(age_at_dream)"
        ]
        
        for idx_sql in indexes:
            cursor.execute(idx_sql)
        
        # Commit all changes
        conn.commit()
        
        # Verify import
        cursor.execute("SELECT COUNT(*) FROM dreams")
        final_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT normalized_title_v3) FROM dreams WHERE normalized_title_v3 IS NOT NULL")
        unique_titles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category_1) FROM dreams WHERE category_1 IS NOT NULL")
        categories = cursor.fetchone()[0]
        
        conn.close()
        
        import_status['success'] = True
        import_status['message'] = f'Successfully imported {final_count:,} dreams! Found {unique_titles:,} unique titles and {categories} categories.'
        import_status['progress'] = final_count
        import_status['total'] = final_count
        
    except Exception as e:
        import_status['success'] = False
        import_status['error'] = str(e)
        import_status['message'] = f'Import failed: {str(e)}'
    finally:
        import_status['running'] = False
        import_status['last_update'] = datetime.now().isoformat()

@app.route('/')
def index():
    """Serve the main dashboard"""
    if os.path.exists('templates/dashboard_spa.html'):
        return render_template('dashboard_spa.html')
    else:
        return jsonify({'error': 'Dashboard not found'}), 404

@app.route('/import')
def import_page():
    """Serve the import interface page"""
    return render_template('import.html')

@app.route('/api/status')
def api_status():
    """API endpoint for current status including import status"""
    return jsonify({
        'status': import_status,
        'database': get_database_stats(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/import/start', methods=['POST'])
def start_import():
    """Start the CSV import process"""
    global import_status
    
    if import_status['running']:
        return jsonify({
            'success': False,
            'message': 'Import already running',
            'status': import_status
        }), 400
    
    # Check if data already exists
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dreams")
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count > 0:
            # Ask for confirmation
            if not request.json.get('force', False):
                return jsonify({
                    'success': False,
                    'message': f'Database already contains {existing_count:,} dreams. Send force=true to overwrite.',
                    'existing_count': existing_count
                }), 400
    except:
        # Table doesn't exist yet, that's fine
        pass
    
    # Start import in background thread
    thread = threading.Thread(target=run_import_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Import started',
        'status': import_status
    })

@app.route('/api/import/status')
def import_status_endpoint():
    """Get current import status"""
    return jsonify(import_status)

def get_database_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dreams")
        total_dreams = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT normalized_title_v3) FROM dreams WHERE normalized_title_v3 IS NOT NULL")
        unique_titles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category_1) FROM dreams WHERE category_1 IS NOT NULL")
        categories = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT subcategory_1) FROM dreams WHERE subcategory_1 IS NOT NULL")
        subcategories = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_dreams': total_dreams,
            'unique_titles': unique_titles,
            'categories': categories,
            'subcategories': subcategories
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {
            'total_dreams': 0,
            'unique_titles': 0,
            'categories': 0,
            'subcategories': 0,
            'error': str(e)
        }

@app.route('/api/unique-dreams')
def api_unique_dreams():
    """Get unique dreams with filtering and pagination"""
    search = request.args.get('search', '')
    age_from = request.args.get('age_from', type=int)
    age_to = request.args.get('age_to', type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    sort_by = request.args.get('sort', 'count')
    sort_order = request.args.get('order', 'desc')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        # Build WHERE clause
        where_conditions = ["normalized_title_v3 IS NOT NULL", "normalized_title_v3 != ''"]
        params = []
        
        if search:
            where_conditions.append("normalized_title_v3 ILIKE %s")
            params.append(f"%{search}%")
        
        if age_from is not None:
            where_conditions.append("age_at_dream >= %s")
            params.append(age_from)
        
        if age_to is not None:
            where_conditions.append("age_at_dream <= %s")
            params.append(age_to)
        
        where_clause = " AND ".join(where_conditions)
        
        # Count total for pagination
        cursor.execute(f"""
            SELECT COUNT(DISTINCT normalized_title_v3) as count
            FROM dreams 
            WHERE {where_clause}
        """, params)
        total_count = cursor.fetchone()['count']
        
        # Get the data
        sort_column = {
            'count': 'COUNT(*)',
            'title': 'normalized_title_v3',
            'avg_age': 'AVG(age_at_dream)'
        }.get(sort_by, 'COUNT(*)')
        
        sort_direction = 'DESC' if sort_order == 'desc' else 'ASC'
        
        # Build safe query with proper parameter binding
        if sort_column == 'COUNT(*)':
            order_clause = "COUNT(*)"
        elif sort_column == 'AVG(age_at_dream)':
            order_clause = "AVG(age_at_dream)"
        else:
            order_clause = "normalized_title_v3"
            
        query = f"""
            SELECT 
                normalized_title_v3,
                COUNT(*) as count,
                AVG(age_at_dream) as avg_age,
                MIN(age_at_dream) as min_age,
                MAX(age_at_dream) as max_age
            FROM dreams 
            WHERE {where_clause}
            GROUP BY normalized_title_v3
            ORDER BY {order_clause} {sort_direction}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, params + [limit, offset])
        
        dreams = []
        for row in cursor.fetchall():
            dreams.append({
                'normalized_title': row['normalized_title_v3'],
                'count': row['count'],
                'avg_age': round(float(row['avg_age']), 1) if row['avg_age'] else None,
                'min_age': row['min_age'],
                'max_age': row['max_age']
            })
        
        conn.close()
        
        return jsonify({
            'dreams': dreams,
            'total_count': total_count,
            'page': offset // limit,
            'per_page': limit
        })
    except Exception as e:
        return jsonify({'error': str(e), 'dreams': [], 'total_count': 0}), 500

@app.route('/api/dream-details/<path:normalized_title>')
def api_dream_details(normalized_title):
    """Get detailed information about a specific normalized dream"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT 
                original_id,
                username,
                age_at_dream,
                category_1,
                subcategory_1,
                category_2,
                subcategory_2,
                category_3,
                subcategory_3
            FROM dreams 
            WHERE normalized_title_v3 = %s
            ORDER BY age_at_dream
            LIMIT 100
        """, (normalized_title,))
        
        dreams = []
        for row in cursor.fetchall():
            dreams.append({
                'original_id': row['original_id'],
                'username': row['username'],
                'age': row['age_at_dream'],
                'categories': [
                    {'category': row['category_1'], 'subcategory': row['subcategory_1']} if row['category_1'] else None,
                    {'category': row['category_2'], 'subcategory': row['subcategory_2']} if row['category_2'] else None,
                    {'category': row['category_3'], 'subcategory': row['subcategory_3']} if row['category_3'] else None,
                ]
            })
        
        conn.close()
        
        return jsonify({
            'normalized_title': normalized_title,
            'dreams': dreams,
            'total_count': len(dreams)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'dreams': []}), 500

@app.route('/api/all-titles')
def api_all_titles():
    """Get all unique normalized titles for selection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT normalized_title_v3, COUNT(*) as count
            FROM dreams 
            WHERE normalized_title_v3 IS NOT NULL AND normalized_title_v3 != ''
            GROUP BY normalized_title_v3
            ORDER BY count DESC
        """)
        
        titles = [{'title': row['normalized_title_v3'], 'count': row['count']} for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'titles': titles})
    except Exception as e:
        return jsonify({'error': str(e), 'titles': []}), 500

@app.route('/api/categories-analysis')
def api_categories_analysis():
    """Get category statistics for analysis"""
    min_age = request.args.get('min_age', 3, type=int)
    max_age = request.args.get('max_age', 125, type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            WITH category_stats AS (
                SELECT 
                    category_1 as category,
                    COUNT(*) as dream_count,
                    AVG(age_at_dream) as avg_age,
                    MIN(age_at_dream) as min_age,
                    MAX(age_at_dream) as max_age
                FROM dreams 
                WHERE category_1 IS NOT NULL AND category_1 != ''
                  AND age_at_dream >= %s AND age_at_dream <= %s
                GROUP BY category_1
            )
            SELECT 
                cs.category,
                cs.dream_count,
                cs.avg_age,
                cs.min_age,
                cs.max_age,
                '' as genders,
                CASE 
                    WHEN cs.avg_age < 13 THEN 'Under 13'
                    WHEN cs.avg_age < 19 THEN '13-18'
                    WHEN cs.avg_age < 31 THEN '19-30'
                    WHEN cs.avg_age < 46 THEN '31-45'
                    WHEN cs.avg_age < 61 THEN '46-60'
                    ELSE '60+'
                END as age_group
            FROM category_stats cs
            ORDER BY cs.dream_count DESC
        """, (min_age, max_age))
        
        categories_data = []
        for row in cursor.fetchall():
            categories_data.append({
                'category': row['category'],
                'count': row['dream_count'],
                'avg_age': row['avg_age'],
                'min_age': row['min_age'],
                'max_age': row['max_age'],
                'gender_dist': row['genders'],
                'top_age_group': row['age_group']
            })
        
        conn.close()
        
        return jsonify({'categories': categories_data})
    except Exception as e:
        return jsonify({'error': str(e), 'categories': []}), 500

@app.route('/api/subcategories-analysis')
def api_subcategories_analysis():
    """Get subcategory statistics for analysis"""
    min_age = request.args.get('min_age', 3, type=int)
    max_age = request.args.get('max_age', 125, type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            WITH subcategory_stats AS (
                SELECT 
                    subcategory_1 as category,
                    COUNT(*) as dream_count,
                    AVG(age_at_dream) as avg_age,
                    MIN(age_at_dream) as min_age,
                    MAX(age_at_dream) as max_age
                FROM dreams 
                WHERE subcategory_1 IS NOT NULL AND subcategory_1 != ''
                  AND age_at_dream >= %s AND age_at_dream <= %s
                GROUP BY subcategory_1
            )
            SELECT 
                cs.category,
                cs.dream_count,
                cs.avg_age,
                cs.min_age,
                cs.max_age,
                '' as genders,
                CASE 
                    WHEN cs.avg_age < 13 THEN 'Under 13'
                    WHEN cs.avg_age < 19 THEN '13-18'
                    WHEN cs.avg_age < 31 THEN '19-30'
                    WHEN cs.avg_age < 46 THEN '31-45'
                    WHEN cs.avg_age < 61 THEN '46-60'
                    ELSE '60+'
                END as age_group
            FROM subcategory_stats cs
            ORDER BY cs.dream_count DESC
        """, (min_age, max_age))
        
        categories_data = []
        for row in cursor.fetchall():
            categories_data.append({
                'category': row['category'],
                'count': row['dream_count'],
                'avg_age': row['avg_age'],
                'min_age': row['min_age'],
                'max_age': row['max_age'],
                'gender_dist': row['genders'],
                'top_age_group': row['age_group']
            })
        
        conn.close()
        
        return jsonify({'categories': categories_data})
    except Exception as e:
        return jsonify({'error': str(e), 'categories': []}), 500

@app.route('/api/category-dreams')
def api_category_dreams():
    """Get dreams for a specific category or subcategory"""
    category = request.args.get('category', '')
    view_type = request.args.get('type', 'categories')
    
    if not category:
        return jsonify({'error': 'Category parameter is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(psycopg2.extras.RealDictCursor)
        
        filter_column = 'subcategory_1' if view_type == 'subcategories' else 'category_1'
        
        cursor.execute(f"""
            SELECT 
                normalized_title_v3,
                COUNT(*) as count,
                MIN(age_at_dream) as min_age,
                MAX(age_at_dream) as max_age,
                '' as genders
            FROM dreams 
            WHERE {filter_column} = %s
            GROUP BY normalized_title_v3
            ORDER BY count DESC
            LIMIT 100
        """, (category,))
        
        dreams = []
        for row in cursor.fetchall():
            dreams.append({
                'normalized_title': row['normalized_title_v3'],
                'count': row['count'],
                'min_age': row['min_age'],
                'max_age': row['max_age'],
                'genders': row['genders']
            })
        
        conn.close()
        
        return jsonify({'dreams': dreams})
    except Exception as e:
        return jsonify({'error': str(e), 'dreams': []}), 500

@app.route('/api/merge-titles', methods=['POST'])
def api_merge_titles():
    """Merge multiple dream titles into one"""
    data = request.json
    target_title = data.get('target_title', '')
    source_titles = data.get('source_titles', [])
    
    if not target_title or not source_titles:
        return jsonify({'error': 'Target title and source titles are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update all dreams with source titles to use the target title
        placeholders = ','.join(['%s' for _ in source_titles])
        cursor.execute(f"""
            UPDATE dreams 
            SET normalized_title_v3 = %s
            WHERE normalized_title_v3 IN ({placeholders})
        """, [target_title] + source_titles)
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Merged {len(source_titles)} titles into '{target_title}', updated {updated_count} dreams")
        
        return jsonify({
            'success': True,
            'target_title': target_title,
            'merged_titles': source_titles,
            'updated_dreams': updated_count
        })
        
    except Exception as e:
        print(f"Error merging titles: {e}")
        return jsonify({'error': 'Failed to merge titles'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)