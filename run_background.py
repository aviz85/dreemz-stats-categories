#!/usr/bin/env python3
"""
Background processing script for the complete dream analysis pipeline.
Runs continuously without timeout constraints.
"""

import json
import csv
import os
import time
from datetime import datetime
from collections import defaultdict
from groq_service import GroqService

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open('pipeline.log', 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def normalize_all_dreams():
    """Normalize all dreams in batches"""
    log("Starting normalization of all dreams...")
    
    # Load existing progress if available
    if os.path.exists('normalized_dreams.json'):
        with open('normalized_dreams.json', 'r') as f:
            dreams = json.load(f)
        log(f"Loaded {len(dreams)} dreams from checkpoint")
        # Count how many are already done
        done = sum(1 for d in dreams if d.get('normalized') and d['normalized'] != "")
        log(f"Already normalized: {done} dreams")
    else:
        # Start fresh - don't pre-fill with nulls
        dreams = []
        log("Starting fresh normalization")
    
    # Load raw dreams from TSV
    raw_dreams = []
    with open('full_results.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['post_title'] and row['post_title'].strip():
                raw_dreams.append({
                    'post_id': row['post_id'],
                    'user_id': row.get('username', ''),
                    'category_id': row.get('categories', ''),
                    'title': row['post_title']
                })
    
    log(f"Total dreams to process: {len(raw_dreams)}")
    
    # Track what's already done
    done_ids = set(d['post_id'] for d in dreams if d.get('normalized'))
    
    # Process in batches
    service = GroqService()
    batch_size = 10
    processed = 0
    
    for dream in raw_dreams:
        # Skip if already done
        if dream['post_id'] in done_ids:
            continue
        
        # Process this dream
        try:
                try:
                    normalized = service.normalize_dream(dream['title'])
                    # NEVER store null - always have a fallback
                    if normalized is None or normalized == "":
                        # Fallback: add "to" to original
                        dream['normalized'] = "to " + dream['title'].lower()
                    else:
                        dream['normalized'] = normalized
                    processed += 1
                    
                    # Save checkpoint every 100 dreams
                    if processed % 100 == 0:
                        with open('normalized_dreams.json', 'w') as f:
                            json.dump(dreams, f, ensure_ascii=False, indent=2)
                        log(f"Normalized {processed} dreams (checkpoint saved)")
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    log(f"Error normalizing dream {dream['post_id']}: {e}")
                    dream['normalized'] = dream['title'].lower()
        
        # Progress update
        if (i + batch_size) % 1000 == 0:
            log(f"Progress: {min(i + batch_size, len(dreams))}/{len(dreams)} dreams")
    
    # Final save
    with open('normalized_dreams.json', 'w') as f:
        json.dump(dreams, f, ensure_ascii=False, indent=2)
    
    log(f"Normalization complete! Processed {processed} new dreams")
    return dreams

def group_dreams(dreams):
    """Group dreams by exact match"""
    log("Starting grouping of dreams...")
    
    groups_dict = defaultdict(list)
    for dream in dreams:
        key = dream.get('normalized', dream['title'].lower())
        groups_dict[key].append(dream)
    
    # Convert to list with metadata
    groups = []
    for gid, (representative, members) in enumerate(groups_dict.items()):
        groups.append({
            'group_id': f"group_{gid:05d}",
            'representative': representative,
            'member_count': len(members),
            'members': [d['post_id'] for d in members]
        })
    
    # Sort by size
    groups.sort(key=lambda g: g['member_count'], reverse=True)
    
    # Save groups
    with open('dream_groups.json', 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    
    log(f"Grouping complete! Created {len(groups)} unique groups")
    return groups

def add_taxonomy(groups):
    """Add taxonomy to all groups"""
    log("Starting taxonomy creation...")
    
    service = GroqService()
    processed = 0
    
    for i, group in enumerate(groups):
        if 'taxonomy' not in group:
            try:
                group['taxonomy'] = service.create_taxonomy(group['representative'])
                processed += 1
                
                # Save checkpoint every 100 groups
                if processed % 100 == 0:
                    with open('dream_groups.json', 'w') as f:
                        json.dump(groups, f, ensure_ascii=False, indent=2)
                    log(f"Added taxonomy to {processed} groups (checkpoint saved)")
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
                
            except Exception as e:
                log(f"Error creating taxonomy for group {group['group_id']}: {e}")
                group['taxonomy'] = {
                    'level1': 'Personal',
                    'level2': 'Goals',
                    'level3': 'General'
                }
        
        # Progress update
        if (i + 1) % 1000 == 0:
            log(f"Progress: {i + 1}/{len(groups)} groups")
    
    # Final save
    with open('dream_groups.json', 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    
    log(f"Taxonomy complete! Processed {processed} new groups")
    return groups

def export_results(dreams, groups):
    """Export final results to TSV files"""
    log("Exporting results...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create group lookup
    group_lookup = {}
    for group in groups:
        for member_id in group['members']:
            group_lookup[member_id] = group
    
    # Export enhanced dreams
    with open(f'final_dreams_enhanced_{timestamp}.tsv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['post_id', 'user_id', 'category_id', 'original_title', 'normalized_title', 
                     'group_id', 'group_size', 'level1', 'level2', 'level3']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for dream in dreams:
            group = group_lookup.get(dream['post_id'])
            if group and 'taxonomy' in group:
                writer.writerow({
                    'post_id': dream['post_id'],
                    'user_id': dream['user_id'],
                    'category_id': dream['category_id'],
                    'original_title': dream['title'],
                    'normalized_title': dream.get('normalized', ''),
                    'group_id': group['group_id'],
                    'group_size': group['member_count'],
                    'level1': group['taxonomy']['level1'],
                    'level2': group['taxonomy']['level2'],
                    'level3': group['taxonomy']['level3']
                })
    
    # Export group summary
    with open(f'final_dream_groups_{timestamp}.tsv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['group_id', 'representative', 'member_count', 'level1', 'level2', 'level3']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for group in groups:
            if 'taxonomy' in group:
                writer.writerow({
                    'group_id': group['group_id'],
                    'representative': group['representative'],
                    'member_count': group['member_count'],
                    'level1': group['taxonomy']['level1'],
                    'level2': group['taxonomy']['level2'],
                    'level3': group['taxonomy']['level3']
                })
    
    log(f"Export complete! Generated files with timestamp {timestamp}")

def main():
    """Run the complete pipeline"""
    log("="*60)
    log("DREAM ANALYSIS PIPELINE - BACKGROUND PROCESSING")
    log("="*60)
    
    try:
        # Step 1: Normalize
        dreams = normalize_all_dreams()
        
        # Step 2: Group
        groups = group_dreams(dreams)
        
        # Step 3: Add taxonomy
        groups = add_taxonomy(groups)
        
        # Step 4: Export
        export_results(dreams, groups)
        
        # Final statistics
        log("="*60)
        log("PIPELINE COMPLETE!")
        log(f"Total dreams processed: {len(dreams)}")
        log(f"Unique groups created: {len(groups)}")
        log(f"Top 10 dream groups:")
        for i, group in enumerate(groups[:10], 1):
            log(f"  {i}. '{group['representative'][:50]}' ({group['member_count']} dreams)")
        log("="*60)
        
    except Exception as e:
        log(f"CRITICAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()