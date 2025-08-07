#!/usr/bin/env python3

from groq_service import GroqService

groq = GroqService()

# Test translation
prompt = "Translate to English: להיות יוטיובר"
response = groq.get_completion(prompt, temperature=0.1, max_tokens=50)
print(f"Prompt: {prompt}")
print(f"Response: '{response}'")
print()

# Enable debug
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=50
)

print("Direct SDK test:")
print(f"Content: '{completion.choices[0].message.content}'")
print(f"Reasoning: '{completion.choices[0].message.reasoning}'")