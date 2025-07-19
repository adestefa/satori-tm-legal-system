#!/bin/bash
# Development helper to clean test cases
# WARNING: Only use in development!

# Target directory
CASE_DIR="/Users/corelogic/satori-dev/TM/test-data/sync-test-cases"

# Function to display cases
show_cases() {
    echo ""
    echo "Current test cases:"
    echo "==================="
    cases=($(ls -1 "$CASE_DIR" | grep -v "^outputs$" 2>/dev/null))
    
    if [ ${#cases[@]} -eq 0 ]; then
        echo "No test cases found."
        return 1
    fi
    
    # Display numbered list
    for i in "${!cases[@]}"; do
        echo "$((i+1)). ${cases[$i]}"
    done
    echo ""
    echo "0. DELETE ALL CASES"
    echo "q. Quit"
    echo ""
    return 0
}

# Main loop
while true; do
    clear
    echo "🧪 DEV MODE: Case Cleanup Tool"
    echo "================================"
    echo "This will remove test cases from local TM"
    
    show_cases
    if [ $? -ne 0 ]; then
        echo ""
        echo "Press any key to exit..."
        read -n 1
        exit 0
    fi
    
    # Get user choice
    read -p "Enter number to delete (or q to quit): " choice
    
    # Handle quit
    if [ "$choice" = "q" ] || [ "$choice" = "Q" ]; then
        echo "Exiting..."
        exit 0
    fi
    
    # Handle empty input (skip)
    if [ -z "$choice" ]; then
        continue
    fi
    
    # Re-read cases array for current selection
    cases=($(ls -1 "$CASE_DIR" | grep -v "^outputs$"))
    
    # Handle delete all
    if [ "$choice" = "0" ]; then
        echo ""
        read -p "⚠️  Delete ALL test cases? Type 'yes' to confirm: " confirm
        if [ "$confirm" = "yes" ]; then
            for case in "${cases[@]}"; do
                rm -rf "$CASE_DIR/$case"
                echo "  ✅ Deleted: $case"
            done
            echo ""
            echo "All test cases deleted!"
            echo "Press any key to continue..."
            read -n 1
        fi
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#cases[@]}" ]; then
        # Delete specific case
        case_name="${cases[$((choice-1))]}"
        echo ""
        read -p "Delete '$case_name'? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$CASE_DIR/$case_name"
            echo "✅ Deleted: $case_name"
            echo "Press any key to continue..."
            read -n 1
        fi
    else
        echo ""
        echo "❌ Invalid selection"
        echo "Press any key to continue..."
        read -n 1
    fi
done