#!/usr/bin/env python3
"""
Step 1: Normalize all dreams
Run this first - it will save progress and can be resumed
"""

import csv
import json
import time
import os
from groq_service import GroqService

# Check if we have a checkpoint
checkpoint_file = "normalize_checkpoint.json"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        checkpoint = json.load(f)
    start_index = checkpoint['last_index']
    print(f"Resuming from index {start_index}")
else:
    start_index = 0

# Load dreams
print("Loading dreams...")
dreams = []
with open('full_results.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['post_title'] and len(row['post_title'].strip()) > 0:
            dreams.append({
                'post_id': row['post_id'],
                'title': row['post_title'],
                'normalized': None
            })

total = len(dreams)
print(f"Total dreams to process: {total}")
print(f"Starting from: {start_index}")

# Load previous results if exists
if os.path.exists('normalized_dreams.json') and start_index > 0:
    with open('normalized_dreams.json', 'r', encoding='utf-8') as f:
        previous = json.load(f)
    dreams[:start_index] = previous[:start_index]

# Initialize service
service = GroqService()

# Process batch
batch_size = 10  # Very small batch to avoid timeout
end_index = min(start_index + batch_size, total)

print(f"\nProcessing dreams {start_index+1} to {end_index}")
print("-" * 40)

for i in range(start_index, end_index):
    dream = dreams[i]
    
    try:
        norm = service.normalize_dream(dream['title'])
        dream['normalized'] = norm if norm else dream['title'].lower()
    except Exception as e:
        print(f"Error at {i}: {e}")
        dream['normalized'] = dream['title'].lower()
    
    # Progress
    if (i - start_index + 1) % 10 == 0:
        print(f"Processed {i - start_index + 1}/{end_index - start_index}")
    
    # Rate limiting
    time.sleep(0.05)

# Save all results
with open('normalized_dreams.json', 'w', encoding='utf-8') as f:
    json.dump(dreams, f, ensure_ascii=False, indent=2)

# Save checkpoint
with open(checkpoint_file, 'w') as f:
    json.dump({'last_index': end_index}, f)

print(f"\n✅ Batch complete!")
print(f"Processed: {end_index}/{total} ({100*end_index/total:.1f}%)")

if end_index >= total:
    print("\n🎉 ALL NORMALIZATION COMPLETE!")
    print("Run step2_group.py next")
else:
    print(f"\n⏳ {total - end_index} dreams remaining")
    print("Run this script again to continue")