#!/usr/bin/env python3
"""
Monitor the dream analysis pipeline progress
"""

import json
import os
import time
from datetime import datetime, timedelta
import subprocess

def get_process_status():
    """Check if the background process is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'run_background.py' in result.stdout
    except:
        return False

def get_progress():
    """Get current normalization progress"""
    if os.path.exists('normalized_dreams.json'):
        with open('normalized_dreams.json', 'r') as f:
            dreams = json.load(f)
            normalized = sum(1 for d in dreams if d.get('normalized'))
            return normalized, len(dreams)
    return 0, 115626

def get_last_log_time():
    """Get the last log update time"""
    if os.path.exists('pipeline.log'):
        try:
            # Get last modified time
            mtime = os.path.getmtime('pipeline.log')
            return datetime.fromtimestamp(mtime)
        except:
            pass
    return None

def calculate_eta(processed, total, start_time):
    """Calculate estimated time of completion"""
    if processed == 0:
        return None
    
    elapsed = datetime.now() - start_time
    rate = processed / elapsed.total_seconds()  # dreams per second
    
    if rate > 0:
        remaining = total - processed
        eta_seconds = remaining / rate
        eta = datetime.now() + timedelta(seconds=eta_seconds)
        return eta, rate * 60  # Return ETA and rate per minute
    return None, 0

def format_time_remaining(eta):
    """Format time remaining in human readable format"""
    if not eta:
        return "Unknown"
    
    remaining = eta - datetime.now()
    total_seconds = int(remaining.total_seconds())
    
    if total_seconds < 0:
        return "Should be complete"
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def main():
    print("="*60)
    print("DREAM PIPELINE MONITOR")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check process status
    is_running = get_process_status()
    print(f"Process Status: {'🟢 RUNNING' if is_running else '🔴 STOPPED'}")
    
    # Get progress
    processed, total = get_progress()
    percentage = (processed / total * 100) if total > 0 else 0
    
    print(f"\nNormalization Progress:")
    print(f"  Processed: {processed:,} / {total:,} dreams")
    print(f"  Progress:  {percentage:.1f}%")
    
    # Progress bar
    bar_length = 40
    filled = int(bar_length * processed / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"  [{bar}]")
    
    # Calculate rate and ETA
    if os.path.exists('pipeline.log'):
        # Try to get start time from first log entry
        with open('pipeline.log', 'r') as f:
            first_line = f.readline()
            if first_line:
                try:
                    start_str = first_line[1:20]  # Extract timestamp
                    start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                    
                    eta, rate = calculate_eta(processed, total, start_time)
                    
                    print(f"\nPerformance:")
                    print(f"  Rate: {rate:.1f} dreams/minute")
                    print(f"  Time Elapsed: {datetime.now() - start_time}")
                    
                    if eta:
                        print(f"  ETA: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  Time Remaining: {format_time_remaining(eta)}")
                except:
                    pass
    
    # Last update
    last_log = get_last_log_time()
    if last_log:
        ago = datetime.now() - last_log
        ago_minutes = int(ago.total_seconds() / 60)
        print(f"\nLast Update: {ago_minutes} minutes ago")
        
        if ago_minutes > 5 and is_running:
            print("⚠️  Warning: No updates in over 5 minutes")
    
    # Check for rate limit errors
    if os.path.exists('pipeline_output.log'):
        with open('pipeline_output.log', 'r') as f:
            content = f.read()
            if 'rate_limit_exceeded' in content[-1000:]:  # Check last 1000 chars
                print("\n⚠️  RATE LIMIT ISSUES DETECTED - Check if billing upgrade is active")
    
    print("\n" + "="*60)
    
    # Summary
    if is_running:
        if percentage < 100:
            print(f"Status: Processing... {percentage:.1f}% complete")
            if eta:
                print(f"Estimated completion: {format_time_remaining(eta)}")
        else:
            print("Status: Normalization complete! Moving to grouping phase...")
    else:
        if percentage < 100:
            print("Status: Process stopped. Run ./start_background.sh to resume")
        else:
            print("Status: Pipeline complete! Check final_* files for results")

if __name__ == "__main__":
    main()