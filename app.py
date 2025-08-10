#!/usr/bin/env python3
"""
Dream Analytics Dashboard - Production Server
Serves the React frontend and provides API endpoints for dream analysis.
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import numpy as np
import faiss

app = Flask(__name__)

class SimilaritySearchSystem:
    def __init__(self):
        self.index = None
        self.titles = []
        self.title_counts = {}
        self.loaded = False
        
    def load_index(self):
        """Load the FAISS index and metadata"""
        try:
            if os.path.exists('dreams_faiss_index.faiss') and os.path.exists('dreams_faiss_metadata.json'):
                print("Loading FAISS index...")
                self.index = faiss.read_index('dreams_faiss_index.faiss')
                
                with open('dreams_faiss_metadata.json', 'r') as f:
                    metadata = json.load(f)
                    self.titles = metadata['titles']
                    self.title_counts = metadata['title_counts']
                
                self.loaded = True
                print(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
                return True
            else:
                print("❌ FAISS index files not found")
                return False
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            return False
    
    def get_current_titles(self):
        """Get current titles and counts from database"""
        try:
            conn = sqlite3.connect("dreams_complete.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT normalized_title_v3, COUNT(*) as count
                FROM dreams 
                WHERE normalized_title_v3 IS NOT NULL AND normalized_title_v3 != ''
                GROUP BY normalized_title_v3
            """)
            
            current_titles = {}
            for row in cursor.fetchall():
                title, count = row
                current_titles[title] = count
            
            conn.close()
            return current_titles
        except Exception as e:
            print(f"Error getting current titles: {e}")
            return {}
    
    def search_similar(self, query_title: str, k: int = 10, threshold: float = 0.0):
        """Search for similar titles using FAISS + string similarity fallback"""
        if not self.loaded:
            return []
        
        try:
            # Get current titles to filter out merged ones
            current_titles = self.get_current_titles()
            
            if query_title not in current_titles:
                return []
            
            # Try FAISS-based similarity first
            similar_titles = self._faiss_similarity_search(query_title, current_titles, k * 3, threshold)
            
            # If FAISS doesn't return enough diverse results, supplement with string similarity
            if len(similar_titles) < k:
                string_similar = self._string_similarity_search(query_title, current_titles, k)
                
                # Merge results, avoiding duplicates
                existing_titles = {item['title'] for item in similar_titles}
                for item in string_similar:
                    if item['title'] not in existing_titles and len(similar_titles) < k:
                        similar_titles.append(item)
            
            # Sort by similarity and return top k
            similar_titles.sort(key=lambda x: (x['similarity'], x['count']), reverse=True)
            return similar_titles[:k]
            
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def _faiss_similarity_search(self, query_title: str, current_titles: dict, k: int, threshold: float):
        """FAISS-based similarity search"""
        # Find all dream vectors for the query title
        query_indices = [i for i, title in enumerate(self.titles) if title == query_title]
        
        if not query_indices:
            return []
        
        # Use the first occurrence as the query vector
        query_idx = query_indices[0]
        query_vector = np.array([self.index.reconstruct(query_idx)], dtype=np.float32)
        
        # Search with higher k to find diverse results
        search_k = min(k * 20, self.index.ntotal)
        distances, indices = self.index.search(query_vector, search_k)
        
        # Collect unique similar titles
        title_similarities = {}
        
        for distance, idx in zip(distances[0], indices[0]):
            if idx >= len(self.titles):
                continue
                
            title = self.titles[idx]
            
            # Skip self matches
            if title == query_title:
                continue
            
            # Skip titles that no longer exist in database (merged)
            if title not in current_titles:
                continue
            
            # Convert distance to similarity percentage
            similarity = max(0, min(100, (2 - distance) * 50))
            
            # Apply threshold filter
            if similarity < threshold:
                continue
            
            # Keep the highest similarity score for each title
            if title not in title_similarities or similarity > title_similarities[title]['similarity']:
                title_similarities[title] = {
                    'similarity': similarity,
                    'count': current_titles[title]
                }
        
        # Convert to list
        results = []
        for title, data in title_similarities.items():
            results.append({
                'title': title,
                'similarity': round(data['similarity'], 1),
                'count': data['count']
            })
        
        return results
    
    def _string_similarity_search(self, query_title: str, current_titles: dict, k: int):
        """String-based similarity search as fallback"""
        import difflib
        
        query_words = set(query_title.lower().split())
        similar_titles = []
        
        for title, count in current_titles.items():
            if title == query_title:
                continue
            
            # Calculate word overlap similarity
            title_words = set(title.lower().split())
            
            if query_words and title_words:
                intersection = len(query_words.intersection(title_words))
                union = len(query_words.union(title_words))
                jaccard_similarity = intersection / union if union > 0 else 0
                
                # Also calculate string similarity
                string_similarity = difflib.SequenceMatcher(None, query_title.lower(), title.lower()).ratio()
                
                # Combine both similarities
                combined_similarity = (jaccard_similarity * 0.6 + string_similarity * 0.4) * 100
                
                if combined_similarity > 20:  # Minimum threshold for string similarity
                    similar_titles.append({
                        'title': title,
                        'similarity': round(combined_similarity, 1),
                        'count': count
                    })
        
        # Sort by similarity and return top results
        similar_titles.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_titles[:k]

# Initialize similarity system
similarity_system = SimilaritySearchSystem()
similarity_system.load_index()

@app.route('/')
def index():
    """Serve the main dashboard"""
    if os.path.exists('templates/dashboard_spa.html'):
        return render_template('dashboard_spa.html')
    else:
        return jsonify({'error': 'Dashboard not found'}), 404

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    return jsonify({
        'status': {'current': 0, 'total': 0, 'rate': 0, 'running': False},
        'database': get_database_stats(),
        'timestamp': datetime.now().isoformat()
    })

def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect("dreams_complete.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dreams")
        total_dreams = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT normalized_title_v3) FROM dreams WHERE normalized_title_v3 IS NOT NULL")
        unique_titles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category_1) FROM dreams WHERE category_1 IS NOT NULL")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT subcategory_1) FROM dreams WHERE subcategory_1 IS NOT NULL")
        subcategories_count = cursor.fetchone()[0]
        
        # Get categories array for React component
        cursor.execute("""
            SELECT category_1 as name, COUNT(*) as count
            FROM dreams 
            WHERE category_1 IS NOT NULL AND category_1 != ''
            GROUP BY category_1
            ORDER BY count DESC
            LIMIT 20
        """)
        categories_list = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Get recent dreams for the dashboard
        cursor.execute("""
            SELECT normalized_title_v3, category_1, subcategory_1, category_2, subcategory_2, category_3, subcategory_3, age_at_dream, title
            FROM dreams 
            WHERE normalized_title_v3 IS NOT NULL
            ORDER BY rowid DESC
            LIMIT 10
        """)
        recent_dreams = []
        for row in cursor.fetchall():
            normalized_title, cat1, sub1, cat2, sub2, cat3, sub3, age, original_title = row
            categories = []
            if cat1:
                categories.append({'category': cat1, 'subcategory': sub1 or ''})
            if cat2:
                categories.append({'category': cat2, 'subcategory': sub2 or ''})
            if cat3:
                categories.append({'category': cat3, 'subcategory': sub3 or ''})
            
            recent_dreams.append({
                'id': len(recent_dreams) + 1,
                'normalized': normalized_title,
                'original': original_title or normalized_title,
                'categories': categories
            })
        
        conn.close()
        
        return {
            'total_dreams': total_dreams,
            'unique_titles': unique_titles,
            'categories': categories_list,  # Array for React
            'categories_count': categories_count,
            'subcategories': subcategories_count,
            'recent': recent_dreams,
            'single_category': 0,
            'double_category': 0,
            'triple_category': 0
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {
            'total_dreams': 0,
            'unique_titles': 0,
            'categories': [],
            'categories_count': 0,
            'subcategories': 0,
            'recent': [],
            'single_category': 0,
            'double_category': 0,
            'triple_category': 0
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
    
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = ["normalized_title_v3 IS NOT NULL", "normalized_title_v3 != ''"]
    params = []
    
    if search:
        where_conditions.append("normalized_title_v3 LIKE ?")
        params.append(f"%{search}%")
    
    if age_from is not None:
        where_conditions.append("age_at_dream >= ?")
        params.append(age_from)
    
    if age_to is not None:
        where_conditions.append("age_at_dream <= ?")
        params.append(age_to)
    
    where_clause = " AND ".join(where_conditions)
    
    # Count total for pagination
    cursor.execute(f"""
        SELECT COUNT(DISTINCT normalized_title_v3) 
        FROM dreams 
        WHERE {where_clause}
    """, params)
    total_count = cursor.fetchone()[0]
    
    # Get the data
    sort_column = {
        'count': 'COUNT(*)',
        'title': 'normalized_title_v3',
        'avg_age': 'AVG(age_at_dream)'
    }.get(sort_by, 'COUNT(*)')
    
    sort_direction = 'DESC' if sort_order == 'desc' else 'ASC'
    
    cursor.execute(f"""
        SELECT 
            normalized_title_v3,
            COUNT(*) as count,
            AVG(age_at_dream) as avg_age,
            MIN(age_at_dream) as min_age,
            MAX(age_at_dream) as max_age
        FROM dreams 
        WHERE {where_clause}
        GROUP BY normalized_title_v3
        ORDER BY {sort_column} {sort_direction}
        LIMIT ? OFFSET ?
    """, params + [limit, offset])
    
    dreams = []
    for row in cursor.fetchall():
        title, count, avg_age, min_age, max_age = row
        
        # Calculate age groups based on min/max ages
        age_groups = []
        if min_age is not None and max_age is not None:
            if min_age <= 12:
                age_groups.append('Under 13')
            if min_age <= 18 and max_age >= 13:
                age_groups.append('13-18')
            if min_age <= 30 and max_age >= 19:
                age_groups.append('19-30')
            if min_age <= 45 and max_age >= 31:
                age_groups.append('31-45')
            if min_age <= 60 and max_age >= 46:
                age_groups.append('46-60')
            if max_age >= 60:
                age_groups.append('60+')
        
        dreams.append({
            'normalized_title': title,
            'count': count,
            'avg_age': round(avg_age, 1) if avg_age else None,
            'min_age': min_age,
            'max_age': max_age,
            'age_groups': age_groups
        })
    
    conn.close()
    
    return jsonify({
        'dreams': dreams,
        'total_count': total_count,
        'page': offset // limit,
        'per_page': limit
    })

@app.route('/api/dream-details/<path:normalized_title>')
def api_dream_details(normalized_title):
    """Get detailed information about a specific normalized dream"""
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
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
            subcategory_3,
            title
        FROM dreams 
        WHERE normalized_title_v3 = ?
        ORDER BY CASE WHEN age_at_dream IS NULL THEN 1 ELSE 0 END, age_at_dream
        LIMIT 100
    """, (normalized_title,))
    
    raw_dreams = []
    for row in cursor.fetchall():
        original_id, username, age, cat1, sub1, cat2, sub2, cat3, sub3, title = row
        categories = []
        if cat1:
            categories.append({'category': cat1, 'subcategory': sub1 or ''})
        if cat2:
            categories.append({'category': cat2, 'subcategory': sub2 or ''})
        if cat3:
            categories.append({'category': cat3, 'subcategory': sub3 or ''})
        
        # Determine age group
        age_group = 'Unknown'
        if age is not None:
            if age <= 12:
                age_group = 'Under 13'
            elif age <= 18:
                age_group = '13-18'
            elif age <= 30:
                age_group = '19-30'
            elif age <= 45:
                age_group = '31-45'
            elif age <= 60:
                age_group = '46-60'
            else:
                age_group = '60+'
        
        raw_dreams.append({
            'dream_id': original_id,
            'username': username,
            'age': age,
            'age_group': age_group,
            'categories': categories,
            'original_title': title or f"Dream {original_id[:8]}..."
        })
    
    # Create age distribution
    age_counts = {}
    for dream in raw_dreams:
        age_group = dream['age_group']
        age_counts[age_group] = age_counts.get(age_group, 0) + 1
    
    age_distribution = [
        {'age_group': ag, 'count': count}
        for ag, count in age_counts.items()
    ]
    
    # Create category distribution
    cat_counts = {}
    for dream in raw_dreams:
        for cat in dream['categories']:
            category = cat['category']
            cat_counts[category] = cat_counts.get(category, 0) + 1
    
    category_distribution = [
        {'category': cat, 'count': count}
        for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Sample dreams (first 20)
    sample_dreams = raw_dreams[:20]
    
    conn.close()
    
    return jsonify({
        'age_distribution': age_distribution,
        'category_distribution': category_distribution,
        'sample_dreams': sample_dreams,
        'total_count': len(raw_dreams)
    })

@app.route('/api/similarity-search', methods=['POST'])
def api_similarity_search():
    """Search for similar dream titles"""
    data = request.json
    query_title = data.get('title', '')
    k = data.get('k', 10)
    threshold = data.get('threshold', 0.0)
    
    if not query_title:
        return jsonify({'error': 'Title is required'}), 400
    
    if not similarity_system or not similarity_system.loaded:
        return jsonify({'error': 'Similarity search not available. FAISS index not loaded.'}), 503
    
    similar_titles = similarity_system.search_similar(query_title, k, threshold)
    
    return jsonify({
        'query': query_title,
        'similar': similar_titles,
        'total_found': len(similar_titles)
    })

@app.route('/api/all-titles')
def api_all_titles():
    """Get all unique normalized titles for selection"""
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT normalized_title_v3, COUNT(*) as count
        FROM dreams 
        WHERE normalized_title_v3 IS NOT NULL AND normalized_title_v3 != ''
        GROUP BY normalized_title_v3
        ORDER BY count DESC
    """)
    
    titles = [{'title': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'titles': titles})

@app.route('/api/categories-analysis')
def api_categories_analysis():
    """Get category statistics for analysis"""
    min_age = request.args.get('min_age', 3, type=int)
    max_age = request.args.get('max_age', 125, type=int)
    
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
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
              AND age_at_dream >= ? AND age_at_dream <= ?
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
        category, count, avg_age, min_age, max_age, genders, age_group = row
        categories_data.append({
            'category': category,
            'count': count,
            'avg_age': avg_age,
            'min_age': min_age,
            'max_age': max_age,
            'gender_dist': genders,
            'top_age_group': age_group
        })
    
    conn.close()
    
    return jsonify({'categories': categories_data})

@app.route('/api/subcategories-analysis')
def api_subcategories_analysis():
    """Get subcategory statistics for analysis"""
    min_age = request.args.get('min_age', 3, type=int)
    max_age = request.args.get('max_age', 125, type=int)
    
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
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
              AND age_at_dream >= ? AND age_at_dream <= ?
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
        category, count, avg_age, min_age, max_age, genders, age_group = row
        categories_data.append({
            'category': category,
            'count': count,
            'avg_age': avg_age,
            'min_age': min_age,
            'max_age': max_age,
            'gender_dist': genders,
            'top_age_group': age_group
        })
    
    conn.close()
    
    return jsonify({'categories': categories_data})

@app.route('/api/category-dreams')
def api_category_dreams():
    """Get dreams for a specific category or subcategory"""
    category = request.args.get('category', '')
    view_type = request.args.get('type', 'categories')
    
    if not category:
        return jsonify({'error': 'Category parameter is required'}), 400
    
    conn = sqlite3.connect("dreams_complete.db")
    cursor = conn.cursor()
    
    filter_column = 'subcategory_1' if view_type == 'subcategories' else 'category_1'
    
    cursor.execute(f"""
        SELECT 
            normalized_title_v3,
            COUNT(*) as count,
            MIN(age_at_dream) as min_age,
            MAX(age_at_dream) as max_age,
            '' as genders
        FROM dreams 
        WHERE {filter_column} = ?
        GROUP BY normalized_title_v3
        ORDER BY count DESC
        LIMIT 100
    """, (category,))
    
    dreams = []
    for row in cursor.fetchall():
        title, count, min_age, max_age, genders = row
        dreams.append({
            'normalized_title': title,
            'count': count,
            'min_age': min_age,
            'max_age': max_age,
            'genders': genders
        })
    
    conn.close()
    
    return jsonify({'dreams': dreams})

@app.route('/api/merge-titles', methods=['POST'])
def api_merge_titles():
    """Merge multiple dream titles into one"""
    data = request.json
    target_title = data.get('target', data.get('target_title', ''))
    source_titles = data.get('titles', data.get('source_titles', []))
    
    if not target_title or not source_titles:
        return jsonify({'error': 'Target title and source titles are required'}), 400
    
    try:
        conn = sqlite3.connect("dreams_complete.db")
        cursor = conn.cursor()
        
        # Update all dreams with source titles to use the target title
        placeholders = ','.join(['?' for _ in source_titles])
        cursor.execute(f"""
            UPDATE dreams 
            SET normalized_title_v3 = ?
            WHERE normalized_title_v3 IN ({placeholders})
        """, [target_title] + source_titles)
        
        updated_count = cursor.rowcount
        
        # Get the new count for the target title
        cursor.execute("SELECT COUNT(*) FROM dreams WHERE normalized_title_v3 = ?", (target_title,))
        new_total_count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"Merged {len(source_titles)} titles into '{target_title}', updated {updated_count} dreams")
        
        return jsonify({
            'success': True,
            'target': target_title,
            'merged_count': updated_count,
            'new_total_count': new_total_count
        })
        
    except Exception as e:
        print(f"Error merging titles: {e}")
        return jsonify({'error': 'Failed to merge titles'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)