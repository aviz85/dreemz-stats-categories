#!/usr/bin/env python3
"""
Main script to run dream grouping and analysis
"""

import csv
import json
import time
from dream_grouping_service import DreamGroupingService
from groq_service import GroqService

def get_test_dreams():
    """Get diverse test dreams from the dataset"""
    return [
        "להיות יוטיובר",
        "להיות יוטיוברית מצליחה",
        "להגיע 100,000 סאבים ביוטיוב",
        "ליצור ערוץ טיק טוק מצליח",
        "להיות מפורסמת",
        "להיות כדורגלן",
        "שחקן כדורגל בליגה לאומית",
        "לקנות דירה",
        "לרכוש 3 נכסי נדל״ן",
        "להיות עשיר",
        "להרוויח מלא כסף",
        "לטייל בעולם",
        "לטוס לדרום אמריקה",
        "להתחתן",
        "למצוא אהבה",
        "להיות רופא",
        "להיות אורטודנט שיניים",
        "לרזות 10 קילו",
        "להיות בכושר",
        "become a famous author",
        "WWE wrestler",
        "Building a shed in my backyard",
        "transition to mtf",
        "make music",
        "להיות זמרת"
    ]

def run_tests(service: DreamGroupingService):
    """Run tests on the service before processing full dataset"""
    
    print("="*60)
    print("RUNNING TESTS ON SAMPLE DATA")
    print("="*60)
    
    # Test 1: Normalization
    test_dreams = get_test_dreams()[:10]
    service.test_normalization(test_dreams)
    
    # Small delay to avoid rate limiting
    time.sleep(1)
    
    # Test 2: Similarity
    test_pairs = [
        ("become a youtuber", "be a successful youtuber"),
        ("become a youtuber", "create tiktok channel"),
        ("become a football player", "play soccer professionally"),
        ("buy a house", "purchase real estate"),
        ("become rich", "make lots of money"),
        ("travel the world", "visit south america"),
        ("become a doctor", "be an orthodontist"),
        ("lose weight", "get fit"),
        ("become famous", "be a youtuber"),
        ("find love", "get married")
    ]
    service.test_similarity(test_pairs)
    
    # Small delay
    time.sleep(1)
    
    # Test 3: Taxonomy
    test_phrases = [
        "become a youtuber",
        "become a doctor",
        "travel the world",
        "get married",
        "become rich",
        "lose weight"
    ]
    service.test_taxonomy(test_phrases)
    
    print("="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print()

def process_sample_dataset(service: DreamGroupingService, num_samples: int = 100):
    """Process a sample of the dataset first"""
    
    print(f"Processing first {num_samples} dreams as a pilot...")
    
    # Load data
    dreams = service.load_tsv_data('full_results.tsv')[:num_samples]
    print(f"Loaded {len(dreams)} dreams for pilot")
    
    # Group dreams
    groups = service.group_dreams(dreams, batch_size=10)
    
    # Add taxonomy to each group
    print("\nAdding taxonomy to groups...")
    for group in groups:
        group['taxonomy'] = service.create_taxonomy(group['representative'])
        time.sleep(0.1)  # Rate limiting
    
    # Save pilot results
    save_pilot_results(dreams, groups, service)
    
    # Print summary
    print_summary(groups)
    
    return groups

def save_pilot_results(dreams, groups, service):
    """Save pilot results to files"""
    
    # Create dream mappings
    mappings = []
    for dream in dreams:
        normalized = service.normalize_dream(dream['title'])
        
        # Find which group this dream belongs to
        group_id = None
        for group in groups:
            if dream['post_id'] in group['member_ids']:
                group_id = group['id']
                break
        
        mappings.append({
            'post_id': dream['post_id'],
            'original_title': dream['title'],
            'normalized_phrase': normalized,
            'group_id': group_id or 'ungrouped'
        })
    
    # Save mappings
    with open('pilot_dream_mappings.tsv', 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['post_id', 'original_title', 'normalized_phrase', 'group_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(mappings)
    
    # Save groups
    group_summary = []
    for group in groups:
        group_summary.append({
            'group_id': group['id'],
            'representative_phrase': group['representative'],
            'level1': group['taxonomy']['level1'],
            'level2': group['taxonomy']['level2'],
            'level3': group['taxonomy']['level3'],
            'member_count': len(group['members'])
        })
    
    with open('pilot_dream_groups.tsv', 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['group_id', 'representative_phrase', 'level1', 'level2', 'level3', 'member_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(group_summary)
    
    print("\nPilot results saved to:")
    print("  - pilot_dream_mappings.tsv")
    print("  - pilot_dream_groups.tsv")

def print_summary(groups):
    """Print summary of grouping results"""
    print("\n" + "="*60)
    print("GROUPING SUMMARY")
    print("="*60)
    
    # Count members
    total_dreams = sum(len(g['members']) for g in groups)
    
    print(f"Total dreams processed: {total_dreams}")
    print(f"Number of groups: {len(groups)}")
    print(f"Average dreams per group: {total_dreams/len(groups):.1f}")
    
    # Find largest groups
    sorted_groups = sorted(groups, key=lambda g: len(g['members']), reverse=True)
    
    print("\nTop 10 largest groups:")
    for i, group in enumerate(sorted_groups[:10], 1):
        print(f"{i}. '{group['representative']}' - {len(group['members'])} dreams")
        print(f"   Taxonomy: {group['taxonomy']['level1']} > {group['taxonomy']['level2']} > {group['taxonomy']['level3']}")
    
    # Taxonomy distribution
    level1_counts = {}
    for group in groups:
        level1 = group['taxonomy']['level1']
        level1_counts[level1] = level1_counts.get(level1, 0) + len(group['members'])
    
    print("\nDreams by main category:")
    for category, count in sorted(level1_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} dreams")

def main():
    """Main function"""
    
    print("DREAM GROUPING AND NORMALIZATION SERVICE")
    print("="*60)
    
    # Initialize service
    groq = GroqService(model="openai/gpt-oss-20b")
    service = DreamGroupingService(groq)
    
    # Step 1: Run tests
    run_tests(service)
    
    # Wait for user confirmation
    response = input("\nTests completed. Proceed with pilot (100 dreams)? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    # Step 2: Process pilot dataset
    groups = process_sample_dataset(service, num_samples=100)
    
    # Step 3: Ask about full processing
    response = input("\nPilot completed. Review the files and proceed with full dataset? (y/n): ")
    if response.lower() != 'y':
        print("Stopping at pilot. Results saved.")
        return
    
    # Step 4: Process full dataset
    print("\nProcessing full dataset...")
    print("This will take some time...")
    
    # Load all dreams
    all_dreams = service.load_tsv_data('full_results.tsv')
    print(f"Loaded {len(all_dreams)} total dreams")
    
    # Process in batches to save progress
    batch_size = 1000
    all_groups = []
    
    for i in range(0, len(all_dreams), batch_size):
        batch = all_dreams[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, len(all_dreams))})")
        
        batch_groups = service.group_dreams(batch)
        
        # Add taxonomy
        for group in batch_groups:
            group['taxonomy'] = service.create_taxonomy(group['representative'])
        
        all_groups.extend(batch_groups)
        
        # Save intermediate results
        with open(f'groups_batch_{i//batch_size + 1}.json', 'w', encoding='utf-8') as f:
            json.dump(batch_groups, f, ensure_ascii=False, indent=2)
        
        print(f"Batch complete. Total groups so far: {len(all_groups)}")
    
    print("\n" + "="*60)
    print("FULL PROCESSING COMPLETE")
    print("="*60)
    print_summary(all_groups)

if __name__ == "__main__":
    main()