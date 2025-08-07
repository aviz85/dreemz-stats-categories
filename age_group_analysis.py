#!/usr/bin/env python3
"""
Analyze dreams by age groups
Groups: 13-18 (born 2007-2012) and 18-30 (born 1995-2007)
"""

import json
import csv
import os
from datetime import datetime
from collections import defaultdict

print("DREAM ANALYSIS BY AGE GROUPS")
print("="*60)

# Load full data with birth dates
dreams_with_users = []
with open('full_results.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['post_title'] and row['post_title'].strip() and row['date_of_birth']:
            dreams_with_users.append({
                'post_id': row['post_id'],
                'title': row['post_title'],
                'date_of_birth': row['date_of_birth'],
                'username': row['username']
            })

print(f"Loaded {len(dreams_with_users)} dreams with user data")

# Calculate ages in 2025
current_year = 2025
age_groups = {
    '13-18': [],
    '18-30': [],
    'other': []
}

for dream in dreams_with_users:
    try:
        birth_year = int(dream['date_of_birth'].split('-')[0])
        age = current_year - birth_year
        
        if 13 <= age <= 18:
            age_groups['13-18'].append(dream)
        elif 18 < age <= 30:
            age_groups['18-30'].append(dream)
        else:
            age_groups['other'].append(dream)
    except:
        age_groups['other'].append(dream)

print(f"\nAge distribution:")
print(f"  13-18 years: {len(age_groups['13-18'])} dreams")
print(f"  18-30 years: {len(age_groups['18-30'])} dreams")
print(f"  Other ages:  {len(age_groups['other'])} dreams")

# Load normalized dreams and groups
normalized_dreams = {}
if os.path.exists('normalized_dreams.json'):
    with open('normalized_dreams.json', 'r') as f:
        dreams_data = json.load(f)
        for dream in dreams_data:
            if dream.get('normalized'):
                normalized_dreams[dream['post_id']] = dream['normalized']
            else:
                normalized_dreams[dream['post_id']] = dream['title'].lower()

# If no normalized data, use original titles
if not normalized_dreams:
    print("\nNo normalized data found, using original titles...")
    for dream in dreams_with_users:
        normalized_dreams[dream['post_id']] = dream['title'].lower()

# Group dreams by normalized title for each age group
groups_by_age = {
    '13-18': defaultdict(list),
    '18-30': defaultdict(list)
}

for age_key, dreams in [('13-18', age_groups['13-18']), ('18-30', age_groups['18-30'])]:
    for dream in dreams:
        normalized = normalized_dreams.get(dream['post_id'], dream['title'].lower())
        groups_by_age[age_key][normalized].append(dream)

# Find common dreams between age groups
all_dream_types = set()
for age_key in ['13-18', '18-30']:
    all_dream_types.update(groups_by_age[age_key].keys())

# Calculate statistics for each dream type
dream_stats = []
for dream_type in all_dream_types:
    count_13_18 = len(groups_by_age['13-18'][dream_type])
    count_18_30 = len(groups_by_age['18-30'][dream_type])
    total = count_13_18 + count_18_30
    
    if total > 1:  # Only include dreams with multiple occurrences
        dream_stats.append({
            'dream': dream_type[:80],  # Truncate long dreams
            'count_13_18': count_13_18,
            'count_18_30': count_18_30,
            'total': total,
            'ratio_young': count_13_18 / total if total > 0 else 0
        })

# Sort by total count
dream_stats.sort(key=lambda x: x['total'], reverse=True)

# Display top dreams overall
print("\n" + "="*60)
print("TOP 20 DREAMS BY TOTAL COUNT")
print("="*60)
print(f"{'Dream':<50} {'13-18':<10} {'18-30':<10} {'Total':<10}")
print("-"*80)

for i, stat in enumerate(dream_stats[:20], 1):
    print(f"{i:2}. {stat['dream'][:47]:<47} {stat['count_13_18']:<10} {stat['count_18_30']:<10} {stat['total']:<10}")

# Display dreams popular with teens (13-18)
print("\n" + "="*60)
print("TOP 10 DREAMS POPULAR WITH TEENS (13-18)")
print("="*60)

teen_dreams = sorted([s for s in dream_stats if s['count_13_18'] > 0], 
                     key=lambda x: (x['count_13_18'], -x['count_18_30']), reverse=True)

print(f"{'Dream':<50} {'13-18':<10} {'18-30':<10} {'Ratio':<10}")
print("-"*80)

for i, stat in enumerate(teen_dreams[:10], 1):
    ratio = f"{stat['ratio_young']*100:.1f}%"
    print(f"{i:2}. {stat['dream'][:47]:<47} {stat['count_13_18']:<10} {stat['count_18_30']:<10} {ratio:<10}")

# Display dreams popular with young adults (18-30)
print("\n" + "="*60)
print("TOP 10 DREAMS POPULAR WITH YOUNG ADULTS (18-30)")
print("="*60)

adult_dreams = sorted([s for s in dream_stats if s['count_18_30'] > 0], 
                      key=lambda x: (x['count_18_30'], -x['count_13_18']), reverse=True)

print(f"{'Dream':<50} {'13-18':<10} {'18-30':<10} {'Ratio':<10}")
print("-"*80)

for i, stat in enumerate(adult_dreams[:10], 1):
    ratio = f"{(1-stat['ratio_young'])*100:.1f}%"
    print(f"{i:2}. {stat['dream'][:47]:<47} {stat['count_13_18']:<10} {stat['count_18_30']:<10} {ratio:<10}")

# Dreams unique to each age group
print("\n" + "="*60)
print("DREAMS UNIQUE TO EACH AGE GROUP")
print("="*60)

unique_13_18 = [s for s in dream_stats if s['count_13_18'] > 0 and s['count_18_30'] == 0]
unique_18_30 = [s for s in dream_stats if s['count_18_30'] > 0 and s['count_13_18'] == 0]

print(f"\nUnique to 13-18 (top 5):")
for i, stat in enumerate(unique_13_18[:5], 1):
    print(f"  {i}. {stat['dream'][:60]} ({stat['count_13_18']} dreams)")

print(f"\nUnique to 18-30 (top 5):")
for i, stat in enumerate(unique_18_30[:5], 1):
    print(f"  {i}. {stat['dream'][:60]} ({stat['count_18_30']} dreams)")

# Export to TSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'age_group_analysis_{timestamp}.tsv'

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['dream', 'count_13_18', 'count_18_30', 'total', 'ratio_young']
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(dream_stats[:100])  # Top 100

print(f"\n✅ Analysis exported to: {output_file}")

import os