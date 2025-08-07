#!/usr/bin/env python3
"""
Fix bad normalizations - retry all dreams that:
1. Have normalized == original title (Hebrew)
2. Have normalized == "null" or None
"""

import json
import time
from groq_service import GroqService

print("Loading normalized dreams...")
with open('normalized_dreams.json', 'r') as f:
    dreams = json.load(f)

# Find dreams that need fixing
needs_fixing = []
for i, dream in enumerate(dreams):
    normalized = dream.get('normalized')
    title = dream['title']
    
    # Check if normalization failed
    if (
        not normalized or 
        normalized == "null" or
        normalized == title or  # Same as original (Hebrew)
        (normalized and any(ord(c) > 1487 and ord(c) < 1515 for c in normalized))  # Contains Hebrew
    ):
        needs_fixing.append(i)

print(f"Found {len(needs_fixing)} dreams that need re-normalization")

if needs_fixing:
    service = GroqService()
    fixed = 0
    errors = 0
    
    print(f"Starting to fix {len(needs_fixing)} dreams...")
    
    for idx in needs_fixing:
        dream = dreams[idx]
        original_title = dream['title']
        
        try:
            # Retry normalization
            normalized = service.normalize_dream(original_title)
            
            if normalized and normalized != original_title:
                dream['normalized'] = normalized
                fixed += 1
            else:
                # If still failing, mark as None (not original text!)
                dream['normalized'] = None
                errors += 1
            
            # Progress update
            if (fixed + errors) % 100 == 0:
                print(f"Progress: {fixed + errors}/{len(needs_fixing)} - Fixed: {fixed}, Failed: {errors}")
                # Save checkpoint
                with open('normalized_dreams.json', 'w') as f:
                    json.dump(dreams, f, ensure_ascii=False, indent=2)
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing dream {idx}: {e}")
            dream['normalized'] = None
            errors += 1

    # Final save
    with open('normalized_dreams.json', 'w') as f:
        json.dump(dreams, f, ensure_ascii=False, indent=2)
    
    print(f"\nFixed {fixed} dreams, {errors} still failed")
    print("Saved to normalized_dreams.json")
else:
    print("No dreams need fixing!")

# Show statistics
total = len(dreams)
normalized = sum(1 for d in dreams if d.get('normalized') and d['normalized'] != "null")
failed = total - normalized

print(f"\nFinal statistics:")
print(f"  Total dreams: {total}")
print(f"  Successfully normalized: {normalized} ({normalized/total*100:.1f}%)")
print(f"  Failed: {failed} ({failed/total*100:.1f}%)")