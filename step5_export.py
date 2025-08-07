#!/usr/bin/env python3
"""
Step 5: Export final results
Run after all processing is complete
"""

import json
import csv
from datetime import datetime
from collections import defaultdict

print("STEP 5: EXPORTING RESULTS")
print("="*60)

# Load all data
print("Loading processed data...")

# Load grouped dreams
with open('grouped_dreams.json', 'r', encoding='utf-8') as f:
    dreams = json.load(f)

# Load groups with taxonomy
with open('groups_with_taxonomy.json', 'r', encoding='utf-8') as f:
    groups = json.load(f)

print(f"Loaded {len(dreams)} dreams and {len(groups)} groups")

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Export 1: Dream mappings (TSV)
print("\nExporting dream mappings...")
mappings_file = f"final_dream_mappings_{timestamp}.tsv"
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

# Export 2: Group summary (TSV)
print("Exporting group summary...")
groups_file = f"final_dream_groups_{timestamp}.tsv"
with open(groups_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f,
                            fieldnames=['group_id', 'representative', 'member_count', 
                                       'level1', 'level2', 'level3'],
                            delimiter='\t')
    writer.writeheader()
    for group in groups:
        if 'taxonomy' in group:
            writer.writerow({
                'group_id': group['id'],
                'representative': group['representative'],
                'member_count': group['member_count'],
                'level1': group['taxonomy']['level1'],
                'level2': group['taxonomy']['level2'],
                'level3': group['taxonomy']['level3']
            })
print(f"✓ Saved {groups_file}")

# Export 3: Enhanced results (combine original TSV with new data)
print("Creating enhanced results...")
enhanced_file = f"final_enhanced_dreams_{timestamp}.tsv"

# Create lookup dictionaries
dream_lookup = {d['post_id']: d for d in dreams}
group_lookup = {g['id']: g for g in groups}

with open('full_results.tsv', 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile, delimiter='\t')
    fieldnames = reader.fieldnames + ['normalized_title', 'group_id', 'group_representative', 
                                      'taxonomy_level1', 'taxonomy_level2', 'taxonomy_level3']
    
    with open(enhanced_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for row in reader:
            post_id = row['post_id']
            if post_id in dream_lookup:
                dream = dream_lookup[post_id]
                row['normalized_title'] = dream.get('normalized', '')
                row['group_id'] = dream.get('group_id', '')
                
                if dream.get('group_id') in group_lookup:
                    group = group_lookup[dream['group_id']]
                    row['group_representative'] = group['representative']
                    if 'taxonomy' in group:
                        row['taxonomy_level1'] = group['taxonomy']['level1']
                        row['taxonomy_level2'] = group['taxonomy']['level2']
                        row['taxonomy_level3'] = group['taxonomy']['level3']
            
            writer.writerow(row)

print(f"✓ Saved {enhanced_file}")

# Print final summary
print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)

# Statistics
total_dreams = len(dreams)
groups_sorted = sorted(groups, key=lambda g: g['member_count'], reverse=True)

print(f"\n📊 Statistics:")
print(f"  Total dreams: {total_dreams}")
print(f"  Unique groups: {len(groups)}")
print(f"  Average group size: {total_dreams/len(groups):.1f}")

print(f"\n🔝 Top 20 Most Common Dreams:")
for i, group in enumerate(groups_sorted[:20], 1):
    print(f"  {i:2}. '{group['representative'][:50]}' ({group['member_count']} dreams)")
    if 'taxonomy' in group:
        t = group['taxonomy']
        print(f"      → {t['level1']} > {t['level2']} > {t['level3']}")

# Category distribution
if groups and 'taxonomy' in groups[0]:
    categories = defaultdict(int)
    for group in groups:
        if 'taxonomy' in group:
            cat = group['taxonomy']['level1']
            categories[cat] += group['member_count']
    
    print(f"\n📂 Distribution by Main Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_dreams) * 100
        print(f"  {cat}: {count} dreams ({pct:.1f}%)")

print("\n" + "="*60)
print("✅ ALL PROCESSING COMPLETE!")
print("="*60)
print("\nFinal files generated:")
print(f"  1. {mappings_file} - Dream to group mappings")
print(f"  2. {groups_file} - Group summaries with taxonomy")
print(f"  3. {enhanced_file} - Original data enhanced with analysis")