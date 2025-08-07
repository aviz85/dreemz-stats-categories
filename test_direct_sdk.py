#!/usr/bin/env python3
"""
Direct test with Groq SDK to understand response structure
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test 1: Simple translation
print("Test 1: Translation request")
print("-" * 40)

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Translate to English: להיות יוטיובר"
        }
    ],
    temperature=0.1,
    max_tokens=50
)

print("Response object type:", type(completion))
print("Response attributes:", dir(completion.choices[0].message))
print("\nMessage content:", completion.choices[0].message.content)
print("Message role:", completion.choices[0].message.role)

# Check if there's a reasoning field
if hasattr(completion.choices[0].message, 'reasoning'):
    print("Reasoning:", completion.choices[0].message.reasoning)

# Print full message object
print("\nFull message:", completion.choices[0].message)

# Test 2: Different prompt style
print("\n\nTest 2: Direct question")
print("-" * 40)

completion2 = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "What is 2+2?"
        }
    ],
    temperature=0,
    max_tokens=10
)

print("Message content:", completion2.choices[0].message.content)
if hasattr(completion2.choices[0].message, 'reasoning'):
    print("Reasoning:", completion2.choices[0].message.reasoning)
    
# Test 3: With system message
print("\n\nTest 3: With system prompt")
print("-" * 40)

completion3 = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer concisely."
        },
        {
            "role": "user",
            "content": "Translate: להיות יוטיובר"
        }
    ],
    temperature=0.1,
    max_tokens=20
)

print("Message content:", completion3.choices[0].message.content)
if hasattr(completion3.choices[0].message, 'reasoning'):
    print("Reasoning:", completion3.choices[0].message.reasoning)