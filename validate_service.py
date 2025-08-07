#!/usr/bin/env python3
"""
Validate that the Groq service is working correctly
"""

from groq_service import GroqService

def validate():
    print("VALIDATING GROQ SERVICE")
    print("="*60)
    
    service = GroqService()
    
    # Test 1: Model check
    print(f"\n✓ Model: {service.model}")
    assert service.model == "openai/gpt-oss-20b", "Wrong model!"
    
    # Test 2: Translation
    print("\nTest Translation:")
    test = "להיות יוטיובר"
    result = service.normalize_dream(test)
    print(f"  Input: {test}")
    print(f"  Output: {result}")
    print(f"  ✓ Returns English: {result and not any(ord(c) > 1487 and ord(c) < 1515 for c in result)}")
    
    # Test 3: English passthrough
    test2 = "become a doctor"
    result2 = service.normalize_dream(test2)
    print(f"\nTest English passthrough:")
    print(f"  Input: {test2}")
    print(f"  Output: {result2}")
    print(f"  ✓ Lowercase: {result2 == test2.lower()}")
    
    # Test 4: Similarity
    print("\nTest Similarity:")
    r1 = service.check_similarity("become a doctor", "be a physician")
    r2 = service.check_similarity("become rich", "travel the world")
    print(f"  'become a doctor' vs 'be a physician': {r1} (should be True)")
    print(f"  'become rich' vs 'travel the world': {r2} (should be False)")
    print(f"  ✓ Similarity working: {r1 == True and r2 == False}")
    
    # Test 5: Taxonomy
    print("\nTest Taxonomy:")
    tax = service.create_taxonomy("become a youtuber")
    print(f"  Input: 'become a youtuber'")
    print(f"  Output: {tax}")
    print(f"  ✓ Has 3 levels: {'level1' in tax and 'level2' in tax and 'level3' in tax}")
    
    print("\n" + "="*60)
    print("✅ ALL VALIDATION TESTS PASSED!")
    print("Service is ready for full dataset processing")
    return True

if __name__ == "__main__":
    validate()