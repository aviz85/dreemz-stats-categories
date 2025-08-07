#!/usr/bin/env python3
"""
Simple Groq Service - ONLY uses openai/gpt-oss-20b
"""

import os
import re
from dotenv import load_dotenv
from groq import Groq
from typing import Optional

class GroqService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.client = Groq(api_key=api_key)
        # Using best model for Hebrew translation
        self.model = "llama-3.3-70b-versatile"
    
    def call_api(self, prompt: str, max_tokens: int = 100) -> str:
        """Direct API call - returns whatever the model outputs"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens  # Use 100+ to get content field
            )
            
            # Get content first (available with enough tokens)
            content = completion.choices[0].message.content
            
            # If content is empty, try to extract from reasoning
            if not content and hasattr(completion.choices[0].message, 'reasoning'):
                reasoning = completion.choices[0].message.reasoning
                content = self.extract_from_reasoning(reasoning)
            
            return content or ""
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return ""
    
    def extract_from_reasoning(self, reasoning: str) -> str:
        """Extract answer from reasoning field when content is empty"""
        if not reasoning:
            return ""
        
        # Look for explicit answer patterns
        patterns = [
            r'answer:\s*"([^"]+)"',
            r'means\s+"([^"]+)"',
            r'translation:\s*"([^"]+)"',
            r'"([^"]+)"\s*$'  # Last quoted text
        ]
        
        for pattern in patterns:
            match = re.search(pattern, reasoning, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def normalize_dream(self, dream_title: str) -> str:
        """Normalize dream to English with 'to verb' format"""
        if not dream_title or dream_title.strip() == "":
            return None
            
        # Check if it's Hebrew
        is_hebrew = any(ord(c) > 1487 and ord(c) < 1515 for c in dream_title)
        
        if is_hebrew:
            prompt = f"""Translate this Hebrew dream to a simple, generic English phrase.
Remove specific details like: locations, numbers, names, years, specific brands.
Keep only the core dream concept.
Format: "to [verb] [object]"

Examples:
"להתחתן ושיהיו לי ילדים השנה" → "to get married"
"לקנות 3 נכסי נדלן" → "to buy property"
"לפתוח עסק מצליח כמו שיין" → "to open a business"

Hebrew: {dream_title}
Reply with ONLY the simplified English phrase:"""
        else:
            # For English, simplify and normalize
            prompt = f"""Simplify this dream to its core concept.
Remove: locations, numbers, names, specific details, brands.
Format: "to [verb] [object]"

Examples:
"build an animal rescue farm in Belgium" → "to build an animal rescue farm"
"buy 3 houses in Tel Aviv" → "to buy property"
"become a YouTube star with 1M subscribers" → "to become a content creator"

Input: {dream_title}
Reply with ONLY the simplified phrase:"""
        
        response = self.call_api(prompt, max_tokens=100)
        
        # If API failed, try to handle it ourselves for English
        if not response or response == "null" or response.strip() == "":
            if not is_hebrew:
                # For English, add "to" if missing
                clean = dream_title.lower().strip()
                if not clean.startswith("to "):
                    return "to " + clean
                return clean
            return None
        
        # Clean the response
        if response:
            # Remove any "normalized:" variations
            response = response.lower()
            for prefix in ["to normalized:", "normalized:", "english:", "translation:", "simplified:"]:
                if prefix in response:
                    response = response.split(prefix)[-1].strip()
            
            # Remove quotes if present
            response = response.strip('"').strip("'")
            
            # Remove various formatting artifacts
            if "→" in response:
                response = response.split("→")[-1].strip()
            if "–" in response:
                response = response.split("–")[-1].strip()
            
            # Remove asterisks and extract from quotes if present
            response = response.strip("*").strip()
            
            # Extract English translation from various patterns
            import re
            
            # First check for italics which often contain the translation
            italics = re.findall(r'\*([^*]+)\*', response)
            if italics:
                # Find English in italics (no Hebrew)
                english_italics = [i for i in italics if not any(ord(c) > 1487 and ord(c) < 1515 for c in i)]
                if english_italics:
                    response = english_italics[0]
            
            # Pattern 1: quoted text
            quotes = re.findall(r'"([^"]+)"', response)
            if quotes:
                # Find English quotes (no Hebrew)
                english_quotes = [q for q in quotes if not any(ord(c) > 1487 and ord(c) < 1515 for c in q)]
                if english_quotes:
                    response = english_quotes[0]
            
            # Pattern 2: After "=" sign
            if "=" in response:
                response = response.split("=")[-1].strip()
            
            # Clean and normalize
            response = response.strip('"').strip("'").strip("*").lower()
            
            # Remove parenthetical alternatives
            response = re.sub(r'\([^)]+\)', '', response).strip()
            
            # Ensure "to" format but avoid double "to"
            if response:
                # Remove double "to to"
                response = response.replace("to to ", "to ")
                
                # Only add "to" if not present
                if not response.startswith("to "):
                    # Common patterns to fix
                    if response.startswith("become "):
                        response = "to " + response
                    elif response.startswith("be "):
                        response = "to " + response
                    elif response.startswith("get "):
                        response = "to " + response
                    elif response.startswith("buy "):
                        response = "to " + response
                    elif response.startswith("have "):
                        response = "to " + response
                    elif not any(response.startswith(w) for w in ["a ", "the "]):
                        # If it's just a verb or noun, add "to"
                        response = "to " + response
            
            # Final cleanup
            response = response.strip().strip('.')
            
            # If response is Hebrew (translation failed), fallback
            if response and any(ord(c) > 1487 and ord(c) < 1515 for c in response):
                # Fallback for Hebrew that didn't translate
                return "to " + dream_title.lower()
            
            # Ensure it returns something valid
            if response and len(response) > 2:
                return response
            
            # Final fallback - add "to" to original
            clean_title = dream_title.lower().strip()
            if not clean_title.startswith("to "):
                return "to " + clean_title
            return clean_title
        
        # Should never reach here, but just in case
        return "to " + dream_title.lower()
    
    def check_similarity(self, phrase1: str, phrase2: str) -> bool:
        """Check if two phrases are similar - return True/False"""
        if phrase1 == phrase2:
            return True
        
        prompt = f"Are '{phrase1}' and '{phrase2}' similar? Reply with only one word: yes or no"
        response = self.call_api(prompt, max_tokens=100)
        
        # Check for yes/no in response
        response_lower = response.lower()
        return "yes" in response_lower and "no" not in response_lower
    
    def create_taxonomy(self, phrase: str) -> dict:
        """Create 3-level taxonomy"""
        prompt = f"Categorize '{phrase}' into 3 levels. Reply ONLY with format: Category|Subcategory|Specific"
        response = self.call_api(prompt, max_tokens=100)
        
        # Clean the response first
        if response:
            # Look for pipe-separated values
            import re
            # Find pattern like XXX|YYY|ZZZ
            match = re.search(r'([A-Za-z\s]+)\|([A-Za-z\s]+)\|([A-Za-z\s]+)', response)
            if match:
                return {
                    'level1': match.group(1).strip(),
                    'level2': match.group(2).strip(),
                    'level3': match.group(3).strip()
                }
            
            # If response mentions categories but not in right format, try fallback
            if any(word in response.lower() for word in ['career', 'personal', 'health', 'travel']):
                # Extract what we can
                lines = response.split('\n')
                if len(lines) >= 3:
                    return {
                        'level1': lines[0].strip(),
                        'level2': lines[1].strip() if len(lines) > 1 else 'General',
                        'level3': lines[2].strip() if len(lines) > 2 else 'Specific'
                    }
        
        # Fallback categories
        return self.fallback_taxonomy(phrase)
    
    def fallback_taxonomy(self, phrase: str) -> dict:
        """Fallback taxonomy based on keywords"""
        phrase_lower = phrase.lower()
        
        if any(word in phrase_lower for word in ['youtube', 'tiktok', 'instagram', 'influencer']):
            return {'level1': 'Career', 'level2': 'Digital Creator', 'level3': 'Social Media'}
        elif any(word in phrase_lower for word in ['doctor', 'lawyer', 'engineer', 'teacher']):
            return {'level1': 'Career', 'level2': 'Professional', 'level3': 'Traditional'}
        elif any(word in phrase_lower for word in ['rich', 'money', 'millionaire']):
            return {'level1': 'Financial', 'level2': 'Wealth', 'level3': 'Personal'}
        elif any(word in phrase_lower for word in ['travel', 'visit', 'trip']):
            return {'level1': 'Travel', 'level2': 'Adventure', 'level3': 'Exploration'}
        elif any(word in phrase_lower for word in ['marry', 'married', 'wedding', 'love']):
            return {'level1': 'Relationships', 'level2': 'Romance', 'level3': 'Marriage'}
        elif any(word in phrase_lower for word in ['fit', 'gym', 'weight', 'muscle']):
            return {'level1': 'Health', 'level2': 'Fitness', 'level3': 'Physical'}
        else:
            return {'level1': 'Personal', 'level2': 'Goals', 'level3': 'General'}