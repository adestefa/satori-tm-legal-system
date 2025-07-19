#!/bin/bash

# Cases Report Generator - JSON output
# Called by cases.sh -r

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"
CASES_DIR="$TM_ROOT/test-data/sync-test-cases"
OUTPUT_FILE="$1"

if [[ -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <output_file.json>"
    exit 1
fi

# Generate JSON report
cat > "$OUTPUT_FILE" << EOF
{
  "report_metadata": {
    "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "hostname": "$(hostname)",
    "ip_address": "$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'unknown')",
    "tm_version": "2.1.1",
    "cases_directory": "$CASES_DIR"
  },
  "summary": {
    "total_cases": $(find "$CASES_DIR" -maxdepth 1 -type d -not -name "sync-test-cases" -not -name "outputs" -not -name ".*" 2>/dev/null | wc -l | tr -d ' '),
    "total_source_files": $(find "$CASES_DIR" -name "outputs" -prune -o -type f -not -name ".*" -print 2>/dev/null | wc -l | tr -d ' '),
    "total_size_bytes": $(du -s "$CASES_DIR" 2>/dev/null | cut -f1 | awk '{print $1 * 512}')
  },
  "cases": [
EOF

# Add case details
first_case=true
find "$CASES_DIR" -maxdepth 1 -type d -not -name "sync-test-cases" -not -name "outputs" -not -name ".*" 2>/dev/null | \
while read -r case_dir; do
    if [[ -n "$case_dir" && -d "$case_dir" ]]; then
        case_name=$(basename "$case_dir")
        
        # Add comma separator for JSON array
        if [[ "$first_case" != "true" ]]; then
            echo "    ," >> "$OUTPUT_FILE"
        fi
        first_case=false
        
        # Case metadata
        mod_time=$(stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%SZ" "$case_dir" 2>/dev/null || echo "unknown")
        file_count=$(find "$case_dir" -type f -not -name ".*" 2>/dev/null | wc -l | tr -d ' ')
        size_bytes=$(du -s "$case_dir" 2>/dev/null | cut -f1 | awk '{print $1 * 512}')
        
        cat >> "$OUTPUT_FILE" << EOF
    {
      "name": "$case_name",
      "path": "$case_dir",
      "last_modified": "$mod_time",
      "source_files": {
        "count": $file_count,
        "size_bytes": $size_bytes,
        "files": [
EOF
        
        # Source files list
        first_file=true
        find "$case_dir" -type f -not -name ".*" 2>/dev/null | sort | while read -r file; do
            if [[ "$first_file" != "true" ]]; then
                echo "," >> "$OUTPUT_FILE"
            fi
            first_file=false
            
            file_size=$(stat -f "%z" "$file" 2>/dev/null || echo "0")
            echo -n "          {\"name\": \"$(basename "$file")\", \"size_bytes\": $file_size}" >> "$OUTPUT_FILE"
        done
        
        cat >> "$OUTPUT_FILE" << EOF

        ]
      },
      "generated_outputs": {
        "tiger_outputs": $(find "$TM_ROOT/outputs/tests/$case_name" -type f 2>/dev/null | wc -l | tr -d ' '),
        "dashboard_outputs": $(find "$TM_ROOT/dashboard/outputs/$case_name" -type f 2>/dev/null | wc -l | tr -d ' '),
        "browser_pdfs": $(find "$TM_ROOT/outputs/browser" -name "*${case_name}*" -type f 2>/dev/null | wc -l | tr -d ' ')
      }
    }
EOF
    fi
done

# Close JSON structure
cat >> "$OUTPUT_FILE" << EOF
  ]
}
EOF