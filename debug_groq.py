#!/usr/bin/env python3
"""
Debug Groq responses
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

tests = [
    "Translate to English: להיות יוטיובר",
    "What is 'לקנות דירה' in English?",
    "Are 'become a youtuber' and 'be a youtube star' similar? Answer yes or no."
]

for test in tests:
    print(f"\nTest: {test}")
    print("-" * 40)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": test}],
        temperature=0.1,
        max_tokens=50
    )
    
    msg = completion.choices[0].message
    print(f"Content: '{msg.content}'")
    if hasattr(msg, 'reasoning'):
        print(f"Reasoning: '{msg.reasoning}'")
        
        # Try to extract answer
        reasoning = msg.reasoning
        if "translation:" in reasoning.lower():
            parts = reasoning.lower().split("translation:")
            if len(parts) > 1:
                answer = parts[-1].strip().strip('"').strip("'").strip('.')
                print(f"Extracted: '{answer}'")
        elif '"' in reasoning:
            import re
            quotes = re.findall(r'"([^"]+)"', reasoning)
            if quotes:
                print(f"Quoted text: {quotes}")