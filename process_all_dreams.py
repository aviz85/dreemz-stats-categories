#!/usr/bin/env python3
"""
Process all dreams from TSV file
Stage 1: Normalize all dreams
Stage 2: Group similar dreams
Stage 3: Create taxonomy for groups
"""

import csv
import json
import time
from datetime import datetime
from collections import defaultdict
from groq_service import GroqService

def load_dreams(filename='full_results.tsv'):
    """Load all dreams from TSV file"""
    dreams = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['post_title'] and len(row['post_title'].strip()) > 0:
                dreams.append({
                    'post_id': row['post_id'],
                    'title': row['post_title'],
                    'username': row.get('username', ''),
                    'normalized': None,
                    'group_id': None
                })
    return dreams

def normalize_dreams(dreams, service, batch_size=100):
    """Stage 1: Normalize all dreams"""
    print("\n" + "="*60)
    print("STAGE 1: NORMALIZING DREAMS")
    print("="*60)
    
    total = len(dreams)
    failed = []
    
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        print(f"\nProcessing batch {i//batch_size + 1}: dreams {i+1}-{batch_end}")
        
        for j, dream in enumerate(dreams[i:batch_end], i):
            norm = service.normalize_dream(dream['title'])
            if norm:
                dream['normalized'] = norm
            else:
                dream['normalized'] = dream['title'].lower()  # Fallback
                failed.append(dream['post_id'])
            
            # Progress
            if (j - i + 1) % 10 == 0:
                print(f"  Normalized {j - i + 1}/{batch_end - i}")
            
            # Rate limiting
            if j % 5 == 0:
                time.sleep(0.05)
        
        # Save progress
        with open(f'normalized_batch_{i//batch_size + 1}.json', 'w', encoding='utf-8') as f:
            json.dump(dreams[i:batch_end], f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Normalized {total} dreams ({len(failed)} failed)")
    return dreams

def group_similar_dreams(dreams, service):
    """Stage 2: Group similar dreams"""
    print("\n" + "="*60)
    print("STAGE 2: GROUPING SIMILAR DREAMS")
    print("="*60)
    
    groups = []
    grouped_ids = set()
    
    # Group by exact match first (fast)
    exact_groups = defaultdict(list)
    for dream in dreams:
        if dream['normalized']:
            exact_groups[dream['normalized']].append(dream)
    
    print(f"Found {len(exact_groups)} unique normalized phrases")
    
    # Convert exact matches to groups
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
            grouped_ids.add(dream['post_id'])
    
    print(f"Created {len(groups)} groups from exact matches")
    
    # Now check similarity between group representatives (much fewer comparisons)
    print("\nMerging similar groups...")
    merged_count = 0
    
    for i in range(len(groups)):
        if i >= len(groups):  # Check as list shrinks
            break
            
        for j in range(i + 1, min(i + 50, len(groups))):  # Check next 50 groups
            if j >= len(groups):
                break
                
            if service.check_similarity(groups[i]['representative'], groups[j]['representative']):
                # Merge group j into group i
                groups[i]['members'].extend(groups[j]['members'])
                groups[i]['member_count'] = len(groups[i]['members'])
                
                # Update group IDs
                for dream in groups[j]['members']:
                    dream['group_id'] = groups[i]['id']
                
                # Remove group j
                groups.pop(j)
                merged_count += 1
                
                if merged_count % 10 == 0:
                    print(f"  Merged {merged_count} similar groups")
                
                # Rate limiting
                time.sleep(0.05)
    
    print(f"\n✓ Final: {len(groups)} unique dream groups")
    return groups

def create_taxonomies(groups, service):
    """Stage 3: Create taxonomy for each group"""
    print("\n" + "="*60)
    print("STAGE 3: CREATING TAXONOMIES")
    print("="*60)
    
    for i, group in enumerate(groups):
        taxonomy = service.create_taxonomy(group['representative'])
        group['taxonomy'] = taxonomy
        
        if (i + 1) % 20 == 0:
            print(f"  Classified {i+1}/{len(groups)} groups")
        
        # Rate limiting
        time.sleep(0.05)
    
    print(f"\n✓ Created taxonomy for {len(groups)} groups")
    return groups

def save_results(dreams, groups):
    """Save all results to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save dream mappings (TSV)
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
    
    # Save group summary (TSV)
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
    
    # Save full JSON
    json_file = f"dream_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_dreams': len(dreams),
            'total_groups': len(groups),
            'groups': groups
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved:")
    print(f"  - {mappings_file}")
    print(f"  - {groups_file}")
    print(f"  - {json_file}")

def print_summary(groups):
    """Print analysis summary"""
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    total_dreams = sum(g['member_count'] for g in groups)
    
    # Sort by size
    groups_sorted = sorted(groups, key=lambda g: g['member_count'], reverse=True)
    
    print(f"\n📊 Statistics:")
    print(f"  Total dreams: {total_dreams}")
    print(f"  Unique groups: {len(groups)}")
    print(f"  Average group size: {total_dreams/len(groups):.1f}")
    
    print(f"\n🔝 Top 10 Most Common Dreams:")
    for i, group in enumerate(groups_sorted[:10], 1):
        print(f"  {i}. '{group['representative']}' ({group['member_count']} dreams)")
        if 'taxonomy' in group:
            t = group['taxonomy']
            print(f"     → {t['level1']} > {t['level2']} > {t['level3']}")
    
    # Category distribution
    if groups and 'taxonomy' in groups[0]:
        categories = defaultdict(int)
        for group in groups:
            cat = group['taxonomy']['level1']
            categories[cat] += group['member_count']
        
        print(f"\n📂 Distribution by Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_dreams) * 100
            print(f"  {cat}: {count} dreams ({pct:.1f}%)")

def main():
    """Main processing function"""
    print("\n" + "="*60)
    print("DREAM PROCESSING PIPELINE")
    print("="*60)
    
    # Initialize service
    service = GroqService()
    
    # Load dreams
    print("\nLoading dreams from TSV...")
    dreams = load_dreams()
    print(f"Loaded {len(dreams)} dreams")
    
    # Stage 1: Normalize
    dreams = normalize_dreams(dreams, service)
    
    # Stage 2: Group
    groups = group_similar_dreams(dreams, service)
    
    # Stage 3: Taxonomy
    groups = create_taxonomies(groups, service)
    
    # Save results
    save_results(dreams, groups)
    
    # Print summary
    print_summary(groups)
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    # Test with small sample first
    response = input("\nRun on full dataset? (yes for full, no for 100 sample): ")
    
    if response.lower() in ['yes', 'y']:
        main()
    else:
        # Test mode - process only first 100
        print("\nTEST MODE: Processing first 100 dreams only")
        
        service = GroqService()
        dreams = load_dreams()[:100]
        print(f"Testing with {len(dreams)} dreams")
        
        dreams = normalize_dreams(dreams, service, batch_size=20)
        groups = group_similar_dreams(dreams, service)
        groups = create_taxonomies(groups, service)
        
        save_results(dreams, groups)
        print_summary(groups)