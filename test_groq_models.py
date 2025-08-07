#!/usr/bin/env python3
"""
Test different Groq models for Hebrew translation
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test dreams
test_dreams = [
    "להיות שחקן כדורגל",
    "לאמץ לבצע אורך מינימליסטי",
    "Farm for life",
    "להתחתן ולהקים משפחה"
]

# Models to test (common Groq models)
models_to_test = [
    "llama-3.3-70b-versatile",  # Best for general tasks
    "llama-3.1-8b-instant",      # Fast and capable
    "mixtral-8x7b-32768",        # Good for multilingual
    "gemma2-9b-it",              # Google's model
    "llama3-70b-8192"            # Larger context
]

print("TESTING GROQ MODELS FOR HEBREW TRANSLATION")
print("=" * 60)

for model in models_to_test:
    print(f"\nTesting: {model}")
    print("-" * 40)
    
    try:
        # Test one Hebrew dream
        prompt = f"""Translate this Hebrew dream to English and normalize it.
Format: "to [verb] [object]" (e.g., "to become a doctor")
Hebrew: להיות שחקן כדורגל
English normalized dream:"""
        
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        response = completion.choices[0].message.content
        print(f"✅ Success: {response[:100]}")
        
    except Exception as e:
        if "does not exist" in str(e):
            print(f"❌ Model not available")
        else:
            print(f"❌ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("Recommendation: Use the model that gave the best translation")