#!/usr/bin/env python3
"""
Test the simplified Groq service
"""

from groq_service import GroqService

def test_service():
    print("TESTING GROQ SERVICE")
    print("="*60)
    
    service = GroqService()
    
    # Test 1: Normalization
    print("\n1. Testing Normalization:")
    print("-"*40)
    test_dreams = [
        "להיות יוטיובר",
        "להיות כדורגלן",
        "לקנות דירה",
        "become a doctor",
        "travel the world"
    ]
    
    for dream in test_dreams:
        normalized = service.normalize_dream(dream)
        print(f"'{dream}' → '{normalized}'")
    
    # Test 2: Similarity
    print("\n2. Testing Similarity:")
    print("-"*40)
    test_pairs = [
        ("become a youtuber", "be a youtube star"),
        ("become a doctor", "be a physician"),
        ("buy a house", "purchase real estate"),
        ("travel the world", "become rich"),
        ("become rich", "make lots of money")
    ]
    
    for p1, p2 in test_pairs:
        similar = service.check_similarity(p1, p2)
        result = "✓ Similar" if similar else "✗ Different"
        print(f"'{p1}' vs '{p2}': {result}")
    
    # Test 3: Taxonomy
    print("\n3. Testing Taxonomy:")
    print("-"*40)
    test_phrases = [
        "become a youtuber",
        "become a doctor",
        "travel the world",
        "get married",
        "become rich"
    ]
    
    for phrase in test_phrases:
        taxonomy = service.create_taxonomy(phrase)
        print(f"'{phrase}':")
        print(f"  → {taxonomy['level1']} | {taxonomy['level2']} | {taxonomy['level3']}")
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")

if __name__ == "__main__":
    test_service()