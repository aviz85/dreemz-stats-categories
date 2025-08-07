#!/usr/bin/env python3
"""
Test the full pipeline with just the first 100 dreams
"""

import json
import csv
import os
from collections import defaultdict
from groq_service import GroqService

print("TESTING WITH SAMPLE DATA")
print("="*60)

# Check what we have normalized
if os.path.exists('normalized_dreams.json'):
    with open('normalized_dreams.json', 'r') as f:
        dreams = json.load(f)
    
    # Count normalized
    normalized_count = sum(1 for d in dreams if d.get('normalized'))
    print(f"Found {normalized_count} normalized dreams out of {len(dreams)}")
    
    # Use first 100 with normalization
    sample = [d for d in dreams[:100] if d.get('normalized')]
else:
    print("No normalized dreams found. Running fresh sample...")
    # Load first 100 from TSV
    sample = []
    service = GroqService()
    
    with open('full_results.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i >= 100:
                break
            if row['post_title'] and row['post_title'].strip():
                dream = {
                    'post_id': row['post_id'],
                    'title': row['post_title'],
                    'normalized': service.normalize_dream(row['post_title'])
                }
                sample.append(dream)
                if (i+1) % 10 == 0:
                    print(f"Normalized {i+1} dreams")

print(f"\nWorking with {len(sample)} dreams")

# Group by exact match
print("\nGrouping dreams...")
groups_dict = defaultdict(list)
for dream in sample:
    key = dream.get('normalized', dream['title'].lower())
    groups_dict[key].append(dream)

# Convert to groups list
groups = []
for representative, members in groups_dict.items():
    groups.append({
        'representative': representative,
        'member_count': len(members),
        'members': [d['post_id'] for d in members]
    })

# Sort by size
groups.sort(key=lambda g: g['member_count'], reverse=True)

print(f"Created {len(groups)} groups")

# Add taxonomy
print("\nAdding taxonomy to top groups...")
service = GroqService()
for i, group in enumerate(groups[:20]):  # Only top 20
    group['taxonomy'] = service.create_taxonomy(group['representative'])
    print(f"  {i+1}. '{group['representative'][:40]}' -> {group['taxonomy']['level1']}")

# Summary
print("\n" + "="*60)
print("SAMPLE RESULTS")
print("="*60)

print(f"\nTotal dreams: {len(sample)}")
print(f"Unique groups: {len(groups)}")

print("\nTop 10 groups:")
for i, group in enumerate(groups[:10], 1):
    print(f"{i:2}. '{group['representative'][:50]}' ({group['member_count']} dreams)")
    if 'taxonomy' in group:
        t = group['taxonomy']
        print(f"    → {t['level1']} > {t['level2']} > {t['level3']}")

# Category distribution
categories = defaultdict(int)
for group in groups:
    if 'taxonomy' in group:
        cat = group['taxonomy']['level1']
        categories[cat] += group['member_count']

if categories:
    print("\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} dreams")

print("\n✅ Sample test complete!")