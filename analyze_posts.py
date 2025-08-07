#!/usr/bin/env python3
"""
Analyze posts from the database using Groq LLM
"""

import psycopg2
import os
import json
from dotenv import load_dotenv
from groq_service import GroqService
from typing import List, Dict, Any
import time

load_dotenv()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD')
    )

def fetch_posts_without_analysis(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch posts that haven't been analyzed yet"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        p.id,
        p.title,
        p.description,
        p."postType",
        p."createdAt",
        u.username
    FROM 
        postdetails p
    LEFT JOIN 
        userdetails u ON p."ownerId" = u.id::text
    LEFT JOIN 
        post_analyze pa ON p.id = pa."postId"
    WHERE 
        p."postType" IN (0, 1)
        AND p."isDeleted" = false
        AND pa.id IS NULL
        AND p.title IS NOT NULL
        AND LENGTH(p.title) > 10
    ORDER BY 
        p."createdAt" DESC
    LIMIT %s
    """
    
    cursor.execute(query, (limit,))
    columns = [desc[0] for desc in cursor.description]
    results = []
    
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    cursor.close()
    conn.close()
    
    return results

def analyze_post_with_groq(post: Dict[str, Any], groq: GroqService) -> Dict[str, Any]:
    """Analyze a single post using Groq"""
    
    title = post.get('title', '')
    description = post.get('description', '')
    
    # Combine title and description for analysis
    content = f"Title: {title}\nDescription: {description}" if description else title
    
    # Prepare the analysis prompt
    prompt = f"""
    Analyze the following post and provide:
    1. A brief summary (max 100 words)
    2. Main category (choose from: Personal Goals, Career, Education, Health, Finance, Relationships, Hobbies, Travel, Other)
    3. Subcategory (be specific based on the content)
    4. Sentiment (positive, negative, neutral)
    5. Key themes or keywords (3-5 items)
    
    Post content:
    {content}
    
    Please respond in JSON format with keys: summary, category, subcategory, sentiment, keywords
    """
    
    try:
        response = groq.get_completion(
            prompt=prompt,
            system_prompt="You are an expert content analyst. Analyze posts concisely and accurately. Always respond in valid JSON format.",
            temperature=0.3,
            max_tokens=500
        )
        
        # Debug: print raw response
        print(f"  Raw response: {response[:200]}...")
        
        # Try to extract JSON from the response
        # Sometimes LLMs add extra text before/after JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            analysis = json.loads(json_str)
        else:
            # If no JSON found, try parsing the whole response
            analysis = json.loads(response)
        
        return {
            'post_id': post['id'],
            'title': post['title'],
            'username': post.get('username', 'N/A'),
            'analysis': analysis,
            'status': 'success'
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for post {post['id']}: {e}")
        return {
            'post_id': post['id'],
            'title': post['title'],
            'analysis': None,
            'status': 'json_error',
            'error': str(e)
        }
    except Exception as e:
        print(f"Error analyzing post {post['id']}: {e}")
        return {
            'post_id': post['id'],
            'title': post['title'],
            'analysis': None,
            'status': 'error',
            'error': str(e)
        }

def save_analysis_results(results: List[Dict[str, Any]], filename: str = "post_analysis_results.json"):
    """Save analysis results to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {filename}")

def main():
    """Main function to analyze posts"""
    
    # Initialize Groq service
    groq = GroqService()
    
    print("=== Post Analysis with Groq ===\n")
    
    # Fetch posts without analysis
    print("Fetching posts without analysis...")
    posts = fetch_posts_without_analysis(limit=5)  # Start with 5 posts
    
    if not posts:
        print("No posts found that need analysis.")
        return
    
    print(f"Found {len(posts)} posts to analyze.\n")
    
    # Analyze each post
    results = []
    for i, post in enumerate(posts, 1):
        print(f"Analyzing post {i}/{len(posts)}: {post['title'][:50]}...")
        
        result = analyze_post_with_groq(post, groq)
        results.append(result)
        
        if result['status'] == 'success':
            print(f"  ✓ Analysis complete")
            if result['analysis']:
                print(f"    Category: {result['analysis'].get('category', 'N/A')}")
                print(f"    Sentiment: {result['analysis'].get('sentiment', 'N/A')}")
        else:
            print(f"  ✗ Analysis failed: {result.get('error', 'Unknown error')}")
        
        # Rate limiting - be nice to the API
        if i < len(posts):
            time.sleep(0.5)
    
    # Save results
    print("\n" + "="*50)
    save_analysis_results(results)
    
    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\nAnalysis Summary:")
    print(f"  Total posts analyzed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(results) - successful}")
    
    # Show sample results
    if successful > 0:
        print("\nSample Results:")
        for result in results[:3]:
            if result['status'] == 'success' and result['analysis']:
                print(f"\n  Post: {result['title'][:50]}...")
                print(f"  Summary: {result['analysis'].get('summary', 'N/A')[:100]}...")
                print(f"  Category: {result['analysis'].get('category', 'N/A')}")

if __name__ == "__main__":
    main()