#!/usr/bin/env python3
"""
Step 4: Create taxonomy for each group
Run after grouping is complete
"""

import json
import os
import time
from groq_service import GroqService

# Check which groups file to use
if os.path.exists('groups_merged.json'):
    groups_file = 'groups_merged.json'
else:
    groups_file = 'groups.json'

# Load checkpoint if exists
checkpoint_file = "taxonomy_checkpoint.json"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        checkpoint = json.load(f)
    start_index = checkpoint['last_index']
else:
    start_index = 0

# Load groups
print(f"Loading groups from {groups_file}...")
with open(groups_file, 'r', encoding='utf-8') as f:
    groups = json.load(f)

print(f"Loaded {len(groups)} groups")
print(f"Starting from index {start_index}")

# Process batch
service = GroqService()
batch_size = 50
end_index = min(start_index + batch_size, len(groups))

print(f"\nCreating taxonomy for groups {start_index} to {end_index-1}")
print("-" * 40)

for i in range(start_index, end_index):
    group = groups[i]
    
    try:
        taxonomy = service.create_taxonomy(group['representative'])
        group['taxonomy'] = taxonomy
    except:
        group['taxonomy'] = service.fallback_taxonomy(group['representative'])
    
    if (i - start_index + 1) % 10 == 0:
        print(f"Processed {i - start_index + 1}/{end_index - start_index}")
    
    time.sleep(0.05)

# Save groups with taxonomy
with open('groups_with_taxonomy.json', 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

# Save checkpoint
with open(checkpoint_file, 'w') as f:
    json.dump({'last_index': end_index}, f)

print(f"\n✅ Batch complete!")
print(f"Processed: {end_index}/{len(groups)} ({100*end_index/len(groups):.1f}%)")

if end_index >= len(groups):
    print("\n🎉 TAXONOMY COMPLETE!")
    print("Run step5_export.py to generate final files")
else:
    print(f"\n⏳ {len(groups) - end_index} groups remaining")
    print("Run this script again to continue")