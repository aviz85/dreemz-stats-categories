#!/usr/bin/env python3
"""
Test the updated Groq service with official SDK
"""

from groq_service import GroqService

def main():
    print("Testing Groq Service with Official SDK")
    print("="*60)
    
    # Initialize service
    groq = GroqService()
    
    # Test 1: Simple completion
    print("\n1. Simple test:")
    response = groq.get_completion("Say hello", max_tokens=10)
    print(f"Response: '{response}'")
    
    # Test 2: Translation
    print("\n2. Translation test:")
    response = groq.get_completion(
        "Translate to English: להיות יוטיובר",
        temperature=0.1,
        max_tokens=20
    )
    print(f"Response: '{response}'")
    
    # Test 3: Another translation
    print("\n3. Another translation:")
    response = groq.get_completion(
        "What is 'לקנות דירה' in English? Answer:",
        temperature=0.1,
        max_tokens=20
    )
    print(f"Response: '{response}'")
    
    # Test 4: Similarity check
    print("\n4. Similarity check:")
    response = groq.get_completion(
        "Are 'become a youtuber' and 'be a youtube star' similar? Answer with yes or no:",
        temperature=0,
        max_tokens=5
    )
    print(f"Response: '{response}'")
    
    print("\n" + "="*60)
    print("Tests completed!")

if __name__ == "__main__":
    main()