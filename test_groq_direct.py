#!/usr/bin/env python3
"""
Direct test of Groq API
"""

from groq_service import GroqService

def main():
    groq = GroqService()
    
    # Test 1: Simple prompt
    print("Test 1: Simple completion")
    response = groq.get_completion("Say hello")
    print(f"Response: '{response}'")
    print()
    
    # Test 2: Translation prompt
    print("Test 2: Translation")
    prompt = "Translate and simplify this dream into a short English phrase: 'להיות יוטיובר'\nReply with ONLY the English phrase, nothing else."
    response = groq.get_completion(prompt, temperature=0.1, max_tokens=30)
    print(f"Prompt: {prompt}")
    print(f"Response: '{response}'")
    print()
    
    # Test 3: Direct API call
    print("Test 3: Direct API call")
    messages = [{"role": "user", "content": "What is 2+2? Reply with just the number."}]
    response = groq.chat_completion(messages, max_tokens=10)
    print(f"Full response: {response}")

if __name__ == "__main__":
    main()