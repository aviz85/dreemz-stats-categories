#!/usr/bin/env python3
"""
Full API Test Script - Tests all endpoints against real Render database
Simulates exactly what the React frontend does to identify crashes
"""
import requests
import json
import time

BASE_URL = "https://dreemz-analytics-dashboard.onrender.com"

def test_endpoint(name, url, expected_keys=None):
    """Test an API endpoint and analyze the response"""
    print(f"\n🔍 Testing {name}:")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text[:500]}...")
            return False
            
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   Raw response: {response.text[:200]}...")
            return False
            
        # Check for API errors
        if 'error' in data and data['error']:
            print(f"   ❌ API Error: {data['error']}")
            return False
            
        # Analyze data structure
        print(f"   ✅ Success - Response keys: {list(data.keys())}")
        
        # Check expected keys
        if expected_keys:
            missing = set(expected_keys) - set(data.keys())
            if missing:
                print(f"   ⚠️  Missing expected keys: {missing}")
        
        # Analyze data types and content
        for key, value in data.items():
            if isinstance(value, list):
                print(f"   📊 {key}: array with {len(value)} items")
                if len(value) > 0 and isinstance(value[0], dict):
                    print(f"      First item keys: {list(value[0].keys())}")
                    # Check for problematic data types
                    for k, v in value[0].items():
                        if v is not None:
                            type_name = type(v).__name__
                            if 'Decimal' in type_name:
                                print(f"      ⚠️  {k} has Decimal type: {v} ({type_name})")
                            elif type_name not in ['str', 'int', 'float', 'bool', 'NoneType']:
                                print(f"      ⚠️  {k} has unusual type: {v} ({type_name})")
                elif len(value) > 0:
                    print(f"      First item: {value[0]} ({type(value[0]).__name__})")
            else:
                print(f"   📊 {key}: {type(value).__name__} = {value}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 COMPREHENSIVE API TESTING")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    
    # Test all endpoints that the React frontend uses
    tests = [
        {
            'name': 'Status API',
            'url': f'{BASE_URL}/api/status',
            'expected': ['status', 'database', 'timestamp']
        },
        {
            'name': 'Unique Dreams (basic)',
            'url': f'{BASE_URL}/api/unique-dreams?limit=3',
            'expected': ['dreams', 'total_count', 'page', 'per_page']
        },
        {
            'name': 'Unique Dreams (with search)',
            'url': f'{BASE_URL}/api/unique-dreams?limit=2&search=soccer',
            'expected': ['dreams', 'total_count', 'page', 'per_page']
        },
        {
            'name': 'Unique Dreams (with age filter)',
            'url': f'{BASE_URL}/api/unique-dreams?limit=2&age_from=20&age_to=30',
            'expected': ['dreams', 'total_count', 'page', 'per_page']
        },
        {
            'name': 'Categories Analysis (basic)',
            'url': f'{BASE_URL}/api/categories-analysis',
            'expected': ['categories']
        },
        {
            'name': 'Categories Analysis (with age)',
            'url': f'{BASE_URL}/api/categories-analysis?min_age=20&max_age=40',
            'expected': ['categories']
        },
        {
            'name': 'Subcategories Analysis',
            'url': f'{BASE_URL}/api/subcategories-analysis?min_age=18&max_age=25',
            'expected': ['categories']
        },
        {
            'name': 'All Titles',
            'url': f'{BASE_URL}/api/all-titles',
            'expected': ['titles']
        },
        {
            'name': 'Category Dreams',
            'url': f'{BASE_URL}/api/category-dreams?category=Money & Wealth&type=categories',
            'expected': ['dreams']
        },
        {
            'name': 'Dream Details',
            'url': f'{BASE_URL}/api/dream-details/become soccer player',
            'expected': ['normalized_title', 'dreams', 'total_count']
        }
    ]
    
    results = []
    for test in tests:
        success = test_endpoint(
            test['name'], 
            test['url'], 
            test.get('expected')
        )
        results.append((test['name'], success))
        time.sleep(0.5)  # Be nice to the server
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if total - passed > 0:
        print("\n❌ Failed tests:")
        for name, success in results:
            if not success:
                print(f"   • {name}")
    
    # Test specific scenarios that might crash React
    print("\n🔍 REACT CRASH ANALYSIS:")
    print("-" * 40)
    
    # Test empty results
    print("Testing empty results scenario...")
    empty_test = test_endpoint(
        "Empty search", 
        f'{BASE_URL}/api/unique-dreams?search=nonexistentdreamtitle123&limit=1',
        ['dreams', 'total_count']
    )
    
    # Test edge cases
    print("Testing age edge cases...")
    edge_test = test_endpoint(
        "Age edges", 
        f'{BASE_URL}/api/unique-dreams?age_from=200&age_to=300&limit=1',
        ['dreams', 'total_count']
    )
    
    print("\n🎯 POTENTIAL FRONTEND ISSUES TO CHECK:")
    print("1. Are all numeric fields proper numbers (not strings/Decimals)?")
    print("2. Are all array fields actually arrays (not null/undefined)?")
    print("3. Are object structures consistent across all items?")
    print("4. Do empty results return proper empty arrays?")
    print("5. Are there any fields with unexpected data types?")
    
    print(f"\n✅ Testing completed!")

if __name__ == "__main__":
    main()