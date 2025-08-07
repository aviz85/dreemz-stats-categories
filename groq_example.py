#!/usr/bin/env python3
"""
Example usage of the Groq service
"""

from groq_service import GroqService
import json

def main():
    # Initialize the service
    groq = GroqService()
    
    print("=== Groq LLM Service Example ===\n")
    
    # Example 1: Simple completion
    print("1. Simple completion:")
    print("-" * 40)
    response = groq.get_completion(
        prompt="Explain the importance of fast language models in 2 sentences."
    )
    print(response)
    print()
    
    # Example 2: Chat with system prompt
    print("2. Chat with system prompt:")
    print("-" * 40)
    response = groq.get_completion(
        prompt="What are the key benefits?",
        system_prompt="You are an AI expert. Be concise and technical."
    )
    print(response)
    print()
    
    # Example 3: Full chat completion with multiple messages
    print("3. Multi-turn conversation:")
    print("-" * 40)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"},
        {"role": "assistant", "content": "Machine learning is a subset of AI that enables systems to learn from data."},
        {"role": "user", "content": "Can you give me a simple example?"}
    ]
    
    response = groq.chat_completion(messages)
    print(json.dumps(response, indent=2))
    print()
    
    # Example 4: Text analysis
    print("4. Text analysis (summary):")
    print("-" * 40)
    sample_text = """
    Artificial intelligence has revolutionized many industries. 
    From healthcare to finance, AI systems are improving efficiency 
    and accuracy. Machine learning models can now process vast amounts 
    of data and identify patterns humans might miss. This has led to 
    breakthroughs in drug discovery, fraud detection, and personalized 
    recommendations.
    """
    
    summary = groq.analyze_text(sample_text, analysis_type="summary")
    print(f"Summary: {summary}")
    print()
    
    # Example 5: Available models
    print("5. Available models:")
    print("-" * 40)
    models = groq.available_models()
    for model in models:
        print(f"  - {model}")

if __name__ == "__main__":
    main()