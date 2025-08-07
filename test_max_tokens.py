#!/usr/bin/env python3
"""
Test if max_tokens is cutting off the response
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test with different max_tokens values
test_cases = [
    {"tokens": 10, "desc": "Very short (10 tokens)"},
    {"tokens": 50, "desc": "Short (50 tokens)"},
    {"tokens": 100, "desc": "Medium (100 tokens)"},
    {"tokens": 200, "desc": "Long (200 tokens)"}
]

prompt = "Translate: להיות יוטיובר\nEnglish:"

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test['desc']}")
    print(f"Max tokens: {test['tokens']}")
    print("-"*60)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=test['tokens']
    )
    
    msg = completion.choices[0].message
    print(f"Content: '{msg.content}'")
    if hasattr(msg, 'reasoning'):
        print(f"Reasoning length: {len(msg.reasoning)}")
        print(f"Reasoning: '{msg.reasoning}'")
        print(f"Reasoning ends with: '{msg.reasoning[-20:]}'")