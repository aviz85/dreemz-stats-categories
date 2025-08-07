#!/usr/bin/env python3
"""
Test script for dream grouping - runs without user input
"""

import time
from dream_grouping_service import DreamGroupingService
from groq_service import GroqService

def main():
    """Main test function"""
    
    print("DREAM GROUPING TEST")
    print("="*60)
    
    # Initialize service (model parameter ignored - always uses openai/gpt-oss-20b)
    groq = GroqService()
    service = DreamGroupingService(groq)
    
    # Test 1: Normalization
    print("\n=== Testing Normalization ===")
    test_dreams = [
        "להיות יוטיובר",
        "become a YouTuber",
        "להיות כדורגלן",
        "לקנות דירה",
        "travel the world"
    ]
    
    for dream in test_dreams:
        normalized = service.normalize_dream(dream)
        print(f"'{dream}' → '{normalized}'")
        time.sleep(0.2)  # Small delay
    
    print("\n=== Testing Similarity ===")
    # First normalize some phrases
    norm1 = service.normalize_dream("להיות יוטיובר")
    norm2 = service.normalize_dream("להיות יוטיוברית מצליחה")
    norm3 = service.normalize_dream("להיות כדורגלן")
    
    test_pairs = [
        (norm1, norm2),  # Should be similar
        (norm1, norm3),  # Should be different
        ("become rich", "make lots of money"),  # Should be similar
        ("become a doctor", "be a youtuber")  # Should be different
    ]
    
    for phrase1, phrase2 in test_pairs:
        similar = service.check_similarity(phrase1, phrase2)
        print(f"'{phrase1}' vs '{phrase2}': {'✓ Similar' if similar else '✗ Different'}")
        time.sleep(0.2)
    
    print("\n=== Testing Taxonomy ===")
    test_phrases = [
        "become a youtuber",
        "become a doctor",
        "travel the world"
    ]
    
    for phrase in test_phrases:
        taxonomy = service.create_taxonomy(phrase)
        print(f"'{phrase}':")
        print(f"  → {taxonomy['level1']} > {taxonomy['level2']} > {taxonomy['level3']}")
        time.sleep(0.2)
    
    print("\n" + "="*60)
    print("TESTS COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()