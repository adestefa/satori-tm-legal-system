#!/bin/bash
#
# This script runs the token_counter.py script to analyze the project's
# memory files and provide an assessment of the context window impact.

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the python script from the same directory
python3 "${SCRIPT_DIR}/token_counter.py"
