#!/usr/bin/env python3
"""
Debug the full response from Groq API to understand the structure
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test different types of prompts
test_cases = [
    {
        "name": "Translation",
        "prompt": "Translate: להיות יוטיובר\nEnglish:"
    },
    {
        "name": "Yes/No",
        "prompt": "Similar? 'be youtuber' vs 'become youtube star'. Answer: y/n"
    },
    {
        "name": "Category",
        "prompt": "Category for 'become doctor': Career|Medicine|Professional"
    }
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test['name']}")
    print(f"Prompt: {test['prompt']}")
    print("-"*60)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": test['prompt']}],
        temperature=0.1,
        max_tokens=50
    )
    
    # Print the full response structure
    print("Full completion object:")
    print(json.dumps(completion.model_dump(), indent=2))
    
    # Extract message
    msg = completion.choices[0].message
    print(f"\nMessage content: '{msg.content}'")
    if hasattr(msg, 'reasoning'):
        print(f"Message reasoning: '{msg.reasoning}'")