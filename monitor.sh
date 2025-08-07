#!/bin/bash

echo "Starting 5-minute monitoring of dream normalization process..."
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    current_time=$(date '+%H:%M:%S')
    echo "[$current_time] Checking progress..."
    
    # Check if process is still running
    if ! ps aux | grep -E "python.*run_background_clean" | grep -v grep > /dev/null; then
        echo "ERROR: Process not running!"
        break
    fi
    
    # Get current count
    count=$(python -c "import json; data=json.load(open('normalized_dreams.json')); print(len(data))" 2>/dev/null || echo "0")
    
    # Calculate progress
    total=115626
    remaining=$((total - count))
    progress=$(python -c "print(f'{$count/$total*100:.1f}')" 2>/dev/null || echo "0.0")
    
    echo "  Processed: $count dreams"
    echo "  Remaining: $remaining dreams" 
    echo "  Progress: $progress%"
    echo ""
    
    # Wait 5 minutes
    sleep 300
done