#!/usr/bin/env python3
"""
Step 3: Merge similar groups (optional - can be slow)
Run in batches to check similarity between groups
"""

import json
import os
import time
from groq_service import GroqService

# Load checkpoint if exists
checkpoint_file = "similarity_checkpoint.json"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        checkpoint = json.load(f)
    start_index = checkpoint['last_index']
else:
    start_index = 0

# Load groups
print("Loading groups...")
with open('groups.json', 'r', encoding='utf-8') as f:
    groups = json.load(f)

# Sort by representative for better similarity checking
groups.sort(key=lambda g: g['representative'])

print(f"Loaded {len(groups)} groups")
print(f"Starting from index {start_index}")

# Process a batch
service = GroqService()
batch_size = 20  # Check 20 groups at a time
merged_count = 0

end_index = min(start_index + batch_size, len(groups))
print(f"\nChecking groups {start_index} to {end_index-1}")

for i in range(start_index, end_index):
    if i >= len(groups):
        break
    
    # Check next 10 groups for similarity
    for j in range(i + 1, min(i + 10, len(groups))):
        if j >= len(groups):
            break
        
        # Quick heuristic: if first words are very different, skip
        words1 = groups[i]['representative'].split()
        words2 = groups[j]['representative'].split()
        if words1 and words2:
            if words1[0][:3] != words2[0][:3]:  # First 3 letters different
                continue
        
        try:
            if service.check_similarity(groups[i]['representative'], groups[j]['representative']):
                # Merge j into i
                groups[i]['members'].extend(groups[j]['members'])
                groups[i]['member_count'] = len(groups[i]['members'])
                groups[i]['merged'] = True
                groups[j]['to_delete'] = True
                merged_count += 1
                print(f"  Merged: '{groups[j]['representative'][:30]}' -> '{groups[i]['representative'][:30]}'")
        except:
            pass
        
        time.sleep(0.05)

# Remove merged groups
groups = [g for g in groups if not g.get('to_delete')]

# Save updated groups
with open('groups_merged.json', 'w', encoding='utf-8') as f:
    json.dump(groups, f, ensure_ascii=False, indent=2)

# Save checkpoint
with open(checkpoint_file, 'w') as f:
    json.dump({'last_index': end_index}, f)

print(f"\n✅ Batch complete!")
print(f"Merged {merged_count} groups in this batch")
print(f"Processed: {end_index}/{len(groups)} groups")

if end_index >= len(groups):
    print("\n🎉 SIMILARITY CHECK COMPLETE!")
    print("Run step4_taxonomy.py next")
else:
    print(f"\n⏳ {len(groups) - end_index} groups remaining")
    print("Run this script again to continue (or skip to step4_taxonomy.py)")