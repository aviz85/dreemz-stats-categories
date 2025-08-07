#!/usr/bin/env python3
"""
Auto-run normalization in small batches
Runs continuously until all dreams are normalized
"""

import subprocess
import json
import os
import time

def get_progress():
    """Get current progress"""
    if os.path.exists('normalize_checkpoint.json'):
        with open('normalize_checkpoint.json', 'r') as f:
            checkpoint = json.load(f)
        return checkpoint['last_index']
    return 0

def get_total():
    """Get total number of dreams"""
    import csv
    count = 0
    with open('full_results.tsv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['post_title'] and len(row['post_title'].strip()) > 0:
                count += 1
    return count

print("AUTO-NORMALIZER")
print("="*60)

total = get_total()
print(f"Total dreams to process: {total}")

batch_count = 0
start_time = time.time()

while True:
    current = get_progress()
    
    if current >= total:
        print("\n🎉 ALL NORMALIZATION COMPLETE!")
        break
    
    batch_count += 1
    print(f"\n--- Batch {batch_count} ---")
    print(f"Progress: {current}/{total} ({100*current/total:.1f}%)")
    
    # Run one batch
    result = subprocess.run(['python', 'step1_normalize.py'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error in batch: {result.stderr}")
        break
    
    # Show time estimate
    if batch_count % 10 == 0:
        elapsed = time.time() - start_time
        rate = current / elapsed
        remaining = (total - current) / rate if rate > 0 else 0
        print(f"Time elapsed: {elapsed/60:.1f} min")
        print(f"Estimated remaining: {remaining/60:.1f} min")

print(f"\nProcessed {get_progress()} dreams in {batch_count} batches")
print("Run step2_group.py next")