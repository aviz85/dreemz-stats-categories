#!/usr/bin/env python3
"""
Clean data for Cohere embedding
Concatenate title + normalized without prefixes, clean text
"""

import json
import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean text for embedding"""
    if not text:
        return ""
    
    # Remove common prefixes/artifacts
    text = text.strip()
    
    # Remove "to " prefix from normalized text (we'll add it back in concat)
    text = re.sub(r'^to\s+', '', text, flags=re.IGNORECASE)
    
    # Remove quotes and extra spaces
    text = re.sub(r'["\'""]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep Hebrew/English letters and basic punctuation
    text = re.sub(r'[^\w\s\u0590-\u05FF.,!?-]', '', text)
    
    return text.strip()

def create_embedding_text(title: str, normalized: str) -> str:
    """
    Create clean text for embedding by concatenating title and normalized
    without the words "title" or "normalized"
    """
    # Clean both parts
    clean_title = clean_text(title)
    clean_normalized = clean_text(normalized)
    
    # Handle cases where normalized might be similar to title
    if clean_title.lower() == clean_normalized.lower():
        # If they're the same, just use one
        return clean_title
    
    # Concatenate with space separator
    embedding_text = f"{clean_title} {clean_normalized}"
    
    # Final cleanup
    embedding_text = re.sub(r'\s+', ' ', embedding_text).strip()
    
    return embedding_text

def prepare_data_for_embedding(input_file: str, output_file: str) -> List[Dict]:
    """
    Load data, clean it, and prepare for embedding
    """
    print(f"Loading data from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} records...")
    
    cleaned_data = []
    skipped = 0
    
    for i, record in enumerate(data):
        try:
            # Extract title and normalized
            title = record.get('title', '').strip()
            normalized = record.get('normalized', '').strip()
            
            # Skip if either is empty
            if not title or not normalized:
                skipped += 1
                continue
            
            # Create embedding text
            embedding_text = create_embedding_text(title, normalized)
            
            # Skip if embedding text is too short
            if len(embedding_text) < 3:
                skipped += 1
                continue
            
            # Add embedding text to record
            cleaned_record = record.copy()
            cleaned_record['embedding_text'] = embedding_text
            
            cleaned_data.append(cleaned_record)
            
            # Progress indicator
            if (i + 1) % 10000 == 0:
                print(f"Processed {i + 1}/{len(data)} records...")
                
        except Exception as e:
            print(f"Error processing record {i}: {e}")
            skipped += 1
            continue
    
    print(f"Cleaning complete!")
    print(f"Total records: {len(data)}")
    print(f"Cleaned records: {len(cleaned_data)}")
    print(f"Skipped records: {skipped}")
    
    # Save cleaned data
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    # Show samples
    print("\nSample cleaned records:")
    for i in range(min(5, len(cleaned_data))):
        record = cleaned_data[i]
        print(f"\n{i+1}:")
        print(f"  Title: {record['title']}")
        print(f"  Normalized: {record['normalized']}")
        print(f"  Embedding text: {record['embedding_text']}")
    
    return cleaned_data

if __name__ == "__main__":
    # Clean the data
    cleaned_data = prepare_data_for_embedding(
        'normalized_dreams.json',
        'cleaned_dreams_for_embedding.json'
    )
    
    print(f"\nData cleaning complete! Ready for embedding with {len(cleaned_data)} records.")