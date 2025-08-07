#!/usr/bin/env python3
"""
Clean background processing script - no pre-filled nulls
"""

import json
import csv
import os
import time
from datetime import datetime
from groq_service import GroqService

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open('pipeline.log', 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    """Run the complete pipeline"""
    log("="*60)
    log("DREAM ANALYSIS PIPELINE - CLEAN START")
    log("="*60)
    
    # Check for existing progress
    processed_dreams = []
    if os.path.exists('normalized_dreams.json'):
        with open('normalized_dreams.json', 'r') as f:
            processed_dreams = json.load(f)
        log(f"Resuming from checkpoint: {len(processed_dreams)} dreams already processed")
    else:
        log("Starting fresh - no previous data")
    
    # Track what's already done
    done_ids = set(d['post_id'] for d in processed_dreams)
    
    # Load all dreams from TSV
    log("Loading dreams from TSV...")
    all_dreams = []
    with open('full_results.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['post_title'] and row['post_title'].strip():
                # Skip if already processed
                if row['post_id'] not in done_ids:
                    all_dreams.append({
                        'post_id': row['post_id'],
                        'username': row.get('username', ''),
                        'date_of_birth': row.get('date_of_birth', ''),
                        'title': row['post_title']
                    })
    
    log(f"Dreams to process: {len(all_dreams)}")
    log(f"Already completed: {len(done_ids)}")
    
    if not all_dreams:
        log("All dreams already processed!")
        return processed_dreams
    
    # Process dreams
    service = GroqService()
    count = 0
    
    for dream in all_dreams:
        try:
            # Normalize the dream
            normalized = service.normalize_dream(dream['title'])
            
            # Ensure we never store null
            if not normalized:
                normalized = "to " + dream['title'].lower()
            
            # Add to results
            processed_dreams.append({
                'post_id': dream['post_id'],
                'username': dream['username'],
                'date_of_birth': dream['date_of_birth'],
                'title': dream['title'],
                'normalized': normalized
            })
            
            count += 1
            
            # Save checkpoint every 100 dreams
            if count % 100 == 0:
                with open('normalized_dreams.json', 'w') as f:
                    json.dump(processed_dreams, f, ensure_ascii=False, indent=2)
                log(f"Processed {count} new dreams (total: {len(processed_dreams)})")
            
            # Progress update every 1000
            if count % 1000 == 0:
                log(f"Progress: {len(processed_dreams)}/{len(all_dreams) + len(done_ids)} total dreams")
            
            # Small delay to avoid rate limits
            time.sleep(0.05)
            
        except Exception as e:
            log(f"Error processing dream: {e}")
            # Even on error, add with fallback
            processed_dreams.append({
                'post_id': dream['post_id'],
                'username': dream['username'],
                'date_of_birth': dream['date_of_birth'],
                'title': dream['title'],
                'normalized': "to " + dream['title'].lower()
            })
    
    # Final save
    with open('normalized_dreams.json', 'w') as f:
        json.dump(processed_dreams, f, ensure_ascii=False, indent=2)
    
    log(f"Normalization complete! Total: {len(processed_dreams)} dreams")
    
    # Now group the dreams
    log("Starting grouping phase...")
    groups_dict = defaultdict(list)
    
    for dream in processed_dreams:
        key = dream['normalized'].lower()
        groups_dict[key].append(dream)
    
    # Convert to list
    groups = []
    for gid, (key, members) in enumerate(groups_dict.items()):
        groups.append({
            'group_id': f"group_{gid:05d}",
            'representative': key,
            'member_count': len(members),
            'member_ids': [d['post_id'] for d in members]
        })
    
    # Sort by size
    groups.sort(key=lambda g: g['member_count'], reverse=True)
    
    # Save groups
    with open('dream_groups.json', 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    
    log(f"Grouping complete! {len(groups)} unique groups")
    
    # Add taxonomy
    log("Creating taxonomy for groups...")
    for i, group in enumerate(groups[:1000]):  # Do first 1000 for now
        try:
            group['taxonomy'] = service.create_taxonomy(group['representative'])
            if (i + 1) % 100 == 0:
                log(f"Added taxonomy to {i + 1} groups")
        except:
            group['taxonomy'] = {
                'level1': 'Personal',
                'level2': 'Goals', 
                'level3': 'General'
            }
    
    # Save final results
    with open('dream_groups.json', 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    
    # Export to TSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export groups summary
    with open(f'final_groups_{timestamp}.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['group_id', 'representative', 'count', 'level1', 'level2', 'level3'])
        
        for group in groups[:100]:  # Top 100
            tax = group.get('taxonomy', {})
            writer.writerow([
                group['group_id'],
                group['representative'],
                group['member_count'],
                tax.get('level1', ''),
                tax.get('level2', ''),
                tax.get('level3', '')
            ])
    
    log(f"Exported results to final_groups_{timestamp}.tsv")
    log("="*60)
    log("PIPELINE COMPLETE!")
    log(f"Total dreams: {len(processed_dreams)}")
    log(f"Unique groups: {len(groups)}")
    log("="*60)

from collections import defaultdict

if __name__ == "__main__":
    main()