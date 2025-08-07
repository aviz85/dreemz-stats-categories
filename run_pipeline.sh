#!/bin/bash
# Run the complete pipeline step by step

echo "DREAM ANALYSIS PIPELINE"
echo "======================="
echo ""

# Step 1: Normalize (run in batches)
echo "Step 1: Normalizing dreams..."
echo "This will take a while. Running in batches of 10..."

# Run 100 batches (1000 dreams) as a start
for i in {1..100}; do
    python step1_normalize.py > /dev/null 2>&1
    if [ $((i % 10)) -eq 0 ]; then
        echo "  Processed $((i * 10)) dreams..."
    fi
done

echo "  Normalized 1000 dreams (sample)"
echo ""

# Step 2: Group
echo "Step 2: Grouping dreams..."
python step2_group.py

# Step 3: Skip similarity for now (optional)
echo "Step 3: Skipping similarity check (optional)"

# Step 4: Taxonomy
echo "Step 4: Creating taxonomy..."
for i in {1..20}; do
    python step4_taxonomy.py > /dev/null 2>&1
done

# Step 5: Export
echo "Step 5: Exporting results..."
python step5_export.py

echo ""
echo "Pipeline complete!"
echo "Check final_* files for results"