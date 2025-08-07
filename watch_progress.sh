#!/bin/bash
# Continuously monitor the pipeline progress

echo "Starting pipeline monitor (Press Ctrl+C to stop)"
echo ""

while true; do
    clear
    python monitor_progress.py
    echo ""
    echo "Auto-refreshing every 30 seconds..."
    sleep 30
done