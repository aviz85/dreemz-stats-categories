#!/usr/bin/env python3
"""
Dream Grouping Service - Normalize and group similar dreams using Groq
"""

import csv
import json
import time
import os
from typing import List, Dict, Any, Tuple
from groq_service import GroqService
from collections import defaultdict
import hashlib

class DreamGroupingService:
    def __init__(self, groq_service: GroqService = None):
        self.groq = groq_service or GroqService(model="openai/gpt-oss-20b")
        self.normalized_cache = {}  # Cache normalized phrases
        self.similarity_cache = {}  # Cache similarity results
        self.groups = []  # List of dream groups
        self.progress_file = "grouping_progress.json"
        
    def load_tsv_data(self, filepath: str) -> List[Dict[str, Any]]:
        """Load dreams from TSV file"""
        dreams = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['post_title'] and len(row['post_title'].strip()) > 0:
                    dreams.append({
                        'post_id': row['post_id'],
                        'title': row['post_title'],
                        'username': row.get('username', ''),
                        'post_type': row.get('post_type', '')
                    })
        return dreams
    
    def normalize_dream(self, dream_title: str) -> str:
        """Normalize a dream title to standard English phrase"""
        # Check cache first
        if dream_title in self.normalized_cache:
            return self.normalized_cache[dream_title]
        
        # Check if already in English (simple heuristic)
        if not any(ord(c) > 1487 and ord(c) < 1515 for c in dream_title):
            # Already in English, just normalize
            normalized = dream_title.lower().strip()
            self.normalized_cache[dream_title] = normalized
            return normalized
            
        prompt = f"Translate this Hebrew phrase to English: {dream_title}\n\nEnglish translation:"
        
        try:
            response = self.groq.get_completion(
                prompt=prompt,
                temperature=0.3,
                max_tokens=50
            )
            
            # Debug print
            print(f"  [DEBUG] Raw response: '{response}'")
            
            # Clean the response - remove quotes, periods, and normalize
            normalized = response.strip()
            # Remove common artifacts
            normalized = normalized.strip('"\'.,!').lower()
            # Remove "to" at the beginning if present
            if normalized.startswith('to '):
                normalized = normalized[3:]
            
            # Cache the result
            self.normalized_cache[dream_title] = normalized
            return normalized
            
        except Exception as e:
            print(f"Error normalizing '{dream_title}': {e}")
            return dream_title.lower()  # Fallback to lowercase original
    
    def check_similarity(self, phrase1: str, phrase2: str) -> bool:
        """Check if two normalized phrases are similar"""
        # Create a cache key
        cache_key = tuple(sorted([phrase1, phrase2]))
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Quick check for exact match
        if phrase1 == phrase2:
            self.similarity_cache[cache_key] = True
            return True
        
        prompt = f"Are these two dreams essentially the same? '{phrase1}' and '{phrase2}'\nReply with ONLY 'y' for yes or 'n' for no."
        
        try:
            response = self.groq.get_completion(
                prompt=prompt,
                temperature=0,
                max_tokens=2
            )
            
            # Extract just the first character that's y or n
            clean_response = response.strip().lower()
            result = clean_response.startswith('y')
            
            self.similarity_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Error checking similarity: {e}")
            return False
    
    def create_taxonomy(self, representative_phrase: str) -> Dict[str, str]:
        """Create 3-level taxonomy for a dream group"""
        prompt = f"Categorize '{representative_phrase}' into 3 levels. Reply ONLY: Level1|Level2|Level3"
        
        try:
            response = self.groq.get_completion(
                prompt=prompt,
                temperature=0.1,
                max_tokens=30
            )
            
            parts = response.strip().split('|')
            if len(parts) == 3:
                return {
                    'level1': parts[0].strip(),
                    'level2': parts[1].strip(),
                    'level3': parts[2].strip()
                }
            else:
                return self._fallback_taxonomy(representative_phrase)
                
        except Exception as e:
            print(f"Error creating taxonomy: {e}")
            return self._fallback_taxonomy(representative_phrase)
    
    def _fallback_taxonomy(self, phrase: str) -> Dict[str, str]:
        """Fallback taxonomy based on keywords"""
        phrase_lower = phrase.lower()
        
        if any(word in phrase_lower for word in ['youtube', 'tiktok', 'instagram', 'influencer']):
            return {'level1': 'Career', 'level2': 'Digital Creator', 'level3': 'Social Media'}
        elif any(word in phrase_lower for word in ['doctor', 'lawyer', 'engineer', 'teacher']):
            return {'level1': 'Career', 'level2': 'Professional', 'level3': 'Traditional'}
        elif any(word in phrase_lower for word in ['rich', 'money', 'millionaire']):
            return {'level1': 'Financial', 'level2': 'Wealth', 'level3': 'Personal'}
        elif any(word in phrase_lower for word in ['travel', 'visit', 'trip']):
            return {'level1': 'Travel', 'level2': 'Exploration', 'level3': 'Personal'}
        elif any(word in phrase_lower for word in ['marry', 'family', 'children']):
            return {'level1': 'Relationships', 'level2': 'Family', 'level3': 'Personal'}
        else:
            return {'level1': 'Personal Goals', 'level2': 'General', 'level3': 'Other'}
    
    def group_dreams(self, dreams: List[Dict[str, Any]], batch_size: int = 100) -> List[Dict[str, Any]]:
        """Group similar dreams together"""
        groups = []
        grouped_ids = set()
        
        print(f"Starting to group {len(dreams)} dreams...")
        
        for i, dream in enumerate(dreams):
            if dream['post_id'] in grouped_ids:
                continue
            
            # Normalize the dream
            normalized = self.normalize_dream(dream['title'])
            
            # Create a new group
            group = {
                'id': f"group_{len(groups)+1:04d}",
                'representative': normalized,
                'members': [dream],
                'member_ids': [dream['post_id']]
            }
            grouped_ids.add(dream['post_id'])
            
            # Find similar dreams
            for other_dream in dreams[i+1:]:
                if other_dream['post_id'] in grouped_ids:
                    continue
                
                other_normalized = self.normalize_dream(other_dream['title'])
                
                if self.check_similarity(normalized, other_normalized):
                    group['members'].append(other_dream)
                    group['member_ids'].append(other_dream['post_id'])
                    grouped_ids.add(other_dream['post_id'])
            
            groups.append(group)
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"Processed {i+1}/{len(dreams)} dreams, found {len(groups)} groups")
                self.save_progress(groups, grouped_ids)
            
            # Rate limiting
            if i % 5 == 0:
                time.sleep(0.1)
        
        return groups
    
    def save_progress(self, groups: List[Dict], grouped_ids: set):
        """Save progress to file"""
        progress = {
            'groups': groups,
            'grouped_ids': list(grouped_ids),
            'timestamp': time.time()
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def test_normalization(self, test_dreams: List[str]):
        """Test normalization on sample dreams"""
        print("\n=== Testing Normalization ===")
        for dream in test_dreams:
            normalized = self.normalize_dream(dream)
            print(f"'{dream}' → '{normalized}'")
        print()
    
    def test_similarity(self, test_pairs: List[Tuple[str, str]]):
        """Test similarity checking on sample pairs"""
        print("\n=== Testing Similarity ===")
        for phrase1, phrase2 in test_pairs:
            similar = self.check_similarity(phrase1, phrase2)
            print(f"'{phrase1}' vs '{phrase2}': {'Similar' if similar else 'Different'}")
        print()
    
    def test_taxonomy(self, test_phrases: List[str]):
        """Test taxonomy creation on sample phrases"""
        print("\n=== Testing Taxonomy ===")
        for phrase in test_phrases:
            taxonomy = self.create_taxonomy(phrase)
            print(f"'{phrase}':")
            print(f"  L1: {taxonomy['level1']}")
            print(f"  L2: {taxonomy['level2']}")
            print(f"  L3: {taxonomy['level3']}")
        print()