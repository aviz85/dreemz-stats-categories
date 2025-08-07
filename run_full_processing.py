#!/usr/bin/env python3
"""
Run full processing on all dreams - optimized for large dataset
"""

import csv
import json
import time
import os
from datetime import datetime
from collections import defaultdict
from groq_service import GroqService

print("\n" + "="*60)
print("STARTING FULL DREAM PROCESSING")
print(f"Time: {datetime.now()}")
print("="*60)

# Initialize service
service = GroqService()

# Load all dreams
print("\n📥 Loading dreams from TSV...")
dreams = []
with open('full_results.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['post_title'] and len(row['post_title'].strip()) > 0:
            dreams.append({
                'post_id': row['post_id'],
                'title': row['post_title'],
                'normalized': None,
                'group_id': None
            })

total_dreams = len(dreams)
print(f"✓ Loaded {total_dreams} dreams")

# STAGE 1: Normalize all dreams
print("\n" + "="*60)
print("STAGE 1: NORMALIZING DREAMS")
print("="*60)

batch_size = 500
failed_count = 0

for batch_num, i in enumerate(range(0, total_dreams, batch_size), 1):
    batch_end = min(i + batch_size, total_dreams)
    print(f"\nBatch {batch_num}: Processing dreams {i+1}-{batch_end}")
    
    for j in range(i, batch_end):
        dream = dreams[j]
        try:
            norm = service.normalize_dream(dream['title'])
            if norm:
                dream['normalized'] = norm
            else:
                dream['normalized'] = dream['title'].lower()
                failed_count += 1
        except Exception as e:
            dream['normalized'] = dream['title'].lower()
            failed_count += 1
        
        # Progress
        if (j - i + 1) % 50 == 0:
            print(f"  Normalized {j - i + 1}/{batch_end - i}")
        
        # Rate limiting
        if j % 10 == 0:
            time.sleep(0.01)
    
    # Save batch progress
    with open(f'batch_normalized_{batch_num}.json', 'w', encoding='utf-8') as f:
        json.dump(dreams[i:batch_end], f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Batch {batch_num} complete")

print(f"\n✅ Stage 1 Complete: Normalized {total_dreams} dreams ({failed_count} failed)")

# STAGE 2: Group similar dreams
print("\n" + "="*60)
print("STAGE 2: GROUPING SIMILAR DREAMS")
print("="*60)

# First, group by exact match (very fast)
exact_groups = defaultdict(list)
for dream in dreams:
    if dream['normalized']:
        exact_groups[dream['normalized']].append(dream)

print(f"Found {len(exact_groups)} unique normalized phrases")

# Convert to group format
groups = []
for norm_phrase, group_dreams in exact_groups.items():
    group_id = f"group_{len(groups)+1:05d}"
    groups.append({
        'id': group_id,
        'representative': norm_phrase,
        'members': group_dreams,
        'member_count': len(group_dreams)
    })
    
    for dream in group_dreams:
        dream['group_id'] = group_id

print(f"Created {len(groups)} initial groups")

# For similarity checking, only check groups with similar starting words
print("\nChecking similarity between groups...")
merged = 0

# Sort groups by representative for better similarity checking
groups.sort(key=lambda g: g['representative'])

for i in range(len(groups)):
    if i >= len(groups):
        break
    
    # Only check next 20 groups (they're sorted, so similar ones are nearby)
    for j in range(i + 1, min(i + 20, len(groups))):
        if j >= len(groups):
            break
        
        # Quick heuristic: if first word is different, skip
        words1 = groups[i]['representative'].split()
        words2 = groups[j]['representative'].split()
        if words1 and words2 and words1[0] != words2[0]:
            continue
        
        # Check similarity
        try:
            if service.check_similarity(groups[i]['representative'], groups[j]['representative']):
                # Merge j into i
                groups[i]['members'].extend(groups[j]['members'])
                groups[i]['member_count'] = len(groups[i]['members'])
                
                for dream in groups[j]['members']:
                    dream['group_id'] = groups[i]['id']
                
                groups.pop(j)
                merged += 1
                
                if merged % 10 == 0:
                    print(f"  Merged {merged} similar groups")
                
                time.sleep(0.01)
        except:
            pass

print(f"\n✅ Stage 2 Complete: {len(groups)} final groups (merged {merged})")

# STAGE 3: Create taxonomy
print("\n" + "="*60)
print("STAGE 3: CREATING TAXONOMIES")
print("="*60)

for i, group in enumerate(groups):
    try:
        taxonomy = service.create_taxonomy(group['representative'])
        group['taxonomy'] = taxonomy
    except:
        group['taxonomy'] = service.fallback_taxonomy(group['representative'])
    
    if (i + 1) % 50 == 0:
        print(f"  Classified {i+1}/{len(groups)} groups")
    
    if i % 10 == 0:
        time.sleep(0.01)

print(f"\n✅ Stage 3 Complete: Classified {len(groups)} groups")

# Save final results
print("\n" + "="*60)
print("SAVING RESULTS")
print("="*60)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save dream mappings
mappings_file = f"dream_mappings_{timestamp}.tsv"
with open(mappings_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, 
                            fieldnames=['post_id', 'original_title', 'normalized', 'group_id'],
                            delimiter='\t')
    writer.writeheader()
    for dream in dreams:
        writer.writerow({
            'post_id': dream['post_id'],
            'original_title': dream['title'],
            'normalized': dream.get('normalized', ''),
            'group_id': dream.get('group_id', '')
        })

print(f"✓ Saved {mappings_file}")

# Save group summary
groups_file = f"dream_groups_{timestamp}.tsv"
with open(groups_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f,
                            fieldnames=['group_id', 'representative', 'member_count', 
                                       'level1', 'level2', 'level3'],
                            delimiter='\t')
    writer.writeheader()
    for group in groups:
        writer.writerow({
            'group_id': group['id'],
            'representative': group['representative'],
            'member_count': group['member_count'],
            'level1': group['taxonomy']['level1'],
            'level2': group['taxonomy']['level2'],
            'level3': group['taxonomy']['level3']
        })

print(f"✓ Saved {groups_file}")

# Print summary
print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)

total_dreams = sum(g['member_count'] for g in groups)
groups_sorted = sorted(groups, key=lambda g: g['member_count'], reverse=True)

print(f"\n📊 Statistics:")
print(f"  Total dreams: {total_dreams}")
print(f"  Unique groups: {len(groups)}")
print(f"  Average group size: {total_dreams/len(groups):.1f}")

print(f"\n🔝 Top 10 Most Common Dreams:")
for i, group in enumerate(groups_sorted[:10], 1):
    print(f"  {i}. '{group['representative']}' ({group['member_count']} dreams)")
    t = group['taxonomy']
    print(f"     → {t['level1']} > {t['level2']} > {t['level3']}")

# Category distribution
categories = defaultdict(int)
for group in groups:
    cat = group['taxonomy']['level1']
    categories[cat] += group['member_count']

print(f"\n📂 Distribution by Category:")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    pct = (count / total_dreams) * 100
    print(f"  {cat}: {count} dreams ({pct:.1f}%)")

print("\n" + "="*60)
print("✅ PROCESSING COMPLETE!")
print(f"Time: {datetime.now()}")
print("="*60)