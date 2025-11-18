#!/bin/bash
# Batch process multiple VTT transcript files
# Usage: ./batch_process_transcripts.sh /path/to/vtt/files/*.vtt

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <vtt_file1> [vtt_file2] [...]"
    echo ""
    echo "Examples:"
    echo "  ./batch_process_transcripts.sh ~/Downloads/*.vtt"
    echo "  ./batch_process_transcripts.sh meeting1.vtt meeting2.vtt"
    exit 1
fi

# Create output directory
OUTPUT_DIR="./parsed_transcripts"
mkdir -p "$OUTPUT_DIR"

echo "============================================"
echo "Batch Transcript Processor"
echo "============================================"
echo "Processing $# files..."
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for vtt_file in "$@"; do
    if [ ! -f "$vtt_file" ]; then
        echo "⚠️  Skipping (not found): $vtt_file"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    filename=$(basename "$vtt_file")
    base_name="${filename%.*}"
    output_file="$OUTPUT_DIR/${base_name}_formatted.md"

    echo "Processing: $filename"

    if python parse_vtt.py "$vtt_file" -o "$output_file"; then
        echo "✓ Saved to: $output_file"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "✗ Failed to process: $filename"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""
done

echo "============================================"
echo "Summary"
echo "============================================"
echo "✓ Successful: $SUCCESS_COUNT"
echo "✗ Failed: $FAIL_COUNT"
echo ""
echo "Formatted transcripts saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "1. Review the formatted transcripts"
echo "2. Copy relevant sections into your Obsidian meeting notes"
echo "3. Add manual notes and action items"
