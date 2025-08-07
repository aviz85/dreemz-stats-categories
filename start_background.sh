#!/bin/bash

echo "Starting dream analysis pipeline in background..."
echo "This will process all 115,626 dreams without timeout issues."
echo ""

# Use conda Python which has groq installed
PYTHON_PATH="/Users/aviz/miniconda3/bin/python"

# Run in background with nohup
nohup $PYTHON_PATH run_background.py > pipeline_output.log 2>&1 &

# Get the process ID
PID=$!

echo "✅ Pipeline started with PID: $PID"
echo ""
echo "Monitor progress with:"
echo "  tail -f pipeline.log"
echo ""
echo "Check full output with:"
echo "  tail -f pipeline_output.log"
echo ""
echo "Stop the process with:"
echo "  kill $PID"
echo ""
echo "The process will run until completion and generate final TSV files."