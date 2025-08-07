#!/usr/bin/env python3
"""
Test the Groq service on real data samples from TSV
"""

import csv
import random
from groq_service import GroqService

def test_on_samples():
    print("TESTING ON REAL DATA SAMPLES")
    print("="*60)
    
    # Load some samples from TSV
    dreams = []
    with open('full_results.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i >= 50:  # Get first 50 dreams
                break
            if row['post_title'] and len(row['post_title'].strip()) > 0:
                dreams.append(row['post_title'])
    
    # Sample 10 random dreams
    test_dreams = random.sample(dreams, min(10, len(dreams)))
    
    service = GroqService()
    
    print("\n1. Testing Normalization on Real Dreams:")
    print("-"*60)
    normalized = []
    for dream in test_dreams:
        norm = service.normalize_dream(dream)
        normalized.append(norm)
        print(f"'{dream[:50]}...' → '{norm}'")
    
    print("\n2. Testing Similarity on Normalized Dreams:")
    print("-"*60)
    # Test first 3 pairs
    for i in range(min(3, len(normalized)-1)):
        similar = service.check_similarity(normalized[i], normalized[i+1])
        result = "✓ Similar" if similar else "✗ Different"
        print(f"'{normalized[i]}' vs '{normalized[i+1]}': {result}")
    
    print("\n3. Testing Taxonomy on Normalized Dreams:")
    print("-"*60)
    # Test first 5 normalized dreams
    for norm in normalized[:5]:
        taxonomy = service.create_taxonomy(norm)
        print(f"'{norm}':")
        print(f"  → {taxonomy['level1']} | {taxonomy['level2']} | {taxonomy['level3']}")
    
    print("\n" + "="*60)
    print("REAL DATA TEST COMPLETED")

if __name__ == "__main__":
    test_on_samples()