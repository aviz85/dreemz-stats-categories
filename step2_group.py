#!/usr/bin/env python3
"""
Step 2: Group similar dreams
Run after step1_normalize.py is complete
"""

import json
from collections import defaultdict
from groq_service import GroqService
import time

print("STEP 2: GROUPING DREAMS")
print("="*60)

# Load normalized dreams
print("Loading normalized dreams...")
with open('normalized_dreams.json', 'r', encoding='utf-8') as f:
    dreams = json.load(f)

print(f"Loaded {len(dreams)} dreams")

# Group by exact match first
print("\nGrouping by exact match...")
exact_groups = defaultdict(list)
for dream in dreams:
    if dream.get('normalized'):
        exact_groups[dream['normalized']].append(dream)
    else:
        exact_groups[dream['title'].lower()].append(dream)

print(f"Found {len(exact_groups)} unique phrases")

# Convert to groups
groups = []
for norm_phrase, group_dreams in exact_groups.items():
    group_id = f"group_{len(groups)+1:05d}"
    groups.append({
        'id': group_id,
        'representative': norm_phrase,
        'members': [d['post_id'] for d in group_dreams],  # Store only IDs to save space
        'member_count': len(group_dreams)
    })
    
    # Update dreams with group ID
    for dream in group_dreams:
        dream['group_id'] = group_id

# Save grouped dreams
print("\nSaving grouped dreams...")
with open('grouped_dreams.json', 'w', encoding='utf-8') as f:
    json.dump(dreams, f, ensure_ascii=False, indent=2)

# Save groups
with open('groups.json', 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

# Sort groups by size
groups_sorted = sorted(groups, key=lambda g: g['member_count'], reverse=True)

print("\n✅ Grouping complete!")
print(f"Total groups: {len(groups)}")
print(f"\nTop 10 most common dreams:")
for i, group in enumerate(groups_sorted[:10], 1):
    print(f"{i}. '{group['representative'][:50]}...' ({group['member_count']} dreams)")

print("\nRun step3_similarity.py next to merge similar groups")