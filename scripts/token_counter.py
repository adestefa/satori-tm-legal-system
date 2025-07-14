import os
import json
from typing import Dict, List, Any

# A simple heuristic for token counting: 1 token ~= 4 characters.
# This is a rough approximation.
TOKEN_ESTIMATE_FACTOR = 4

def estimate_tokens(byte_size: int) -> int:
    """Estimates the number of tokens from the byte size of a file."""
    return byte_size // TOKEN_ESTIMATE_FACTOR

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Gets the byte size and estimated token count for a file."""
    try:
        byte_size = os.path.getsize(file_path)
        return {
            "path": file_path,
            "byte_size": byte_size,
            "token_count": estimate_tokens(byte_size),
        }
    except FileNotFoundError:
        return None

def analyze_directories(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyzes all files in the configured directories."""
    all_file_info = []
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for dir_to_scan in config.get("directories_to_scan", []):
        full_dir_path = os.path.join(base_path, dir_to_scan)
        if not os.path.isdir(full_dir_path):
            print(f"Warning: Directory not found: {full_dir_path}")
            continue

        for root, _, files in os.walk(full_dir_path):
            for file in files:
                if any(ex in file for ex in config.get("exclude_patterns", [])):
                    continue
                
                file_path = os.path.join(root, file)
                info = get_file_info(file_path)
                if info:
                    all_file_info.append(info)

    for file_to_scan in config.get("files_to_scan", []):
        full_file_path = os.path.join(base_path, file_to_scan)
        info = get_file_info(full_file_path)
        if info:
            all_file_info.append(info)
            
    return all_file_info

def rate_token_size(total_tokens: int) -> str:
    """Rates the total token size."""
    if total_tokens < 10000:
        return "SMALL"
    elif total_tokens < 50000:
        return "MEDIUM"
    else:
        return "LARGE"

def main():
    """Main function to run the token counter."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        return

    all_files = analyze_directories(config)
    
    if not all_files:
        print("No files found to analyze.")
        return

    total_files = len(all_files)
    total_byte_size = sum(f["byte_size"] for f in all_files)
    total_tokens = sum(f["token_count"] for f in all_files)

    print("--- Token Counter Analysis ---")
    print("\nFiles included in analysis:")
    for file_info in sorted(all_files, key=lambda x: x['path']):
        print(f"  - {file_info['path']} ({file_info['byte_size']} bytes, ~{file_info['token_count']} tokens)")

    print("\n--- Summary ---")
    print(f"Total Files Scanned: {total_files}")
    print(f"Total Byte Size: {total_byte_size} bytes")
    print(f"Estimated Total Tokens: {total_tokens}")

    token_rating = rate_token_size(total_tokens)
    print(f"\n--- Context Window Impact Assessment ---")
    print(f"Impact Rating: {token_rating}")
    
    if token_rating == "SMALL":
        print("Assessment: The memory context is small. This is highly efficient and allows for a large amount of room for conversational context and complex instructions.")
    elif token_rating == "MEDIUM":
        print("Assessment: The memory context is of a medium size. This is manageable, but it consumes a noticeable portion of the available context window. Efficiency may be impacted in very long or complex sessions.")
    else:
        print("Assessment: The memory context is large. This will consume a significant portion of the context window. There is a higher risk of context truncation in long conversations, which could lead to loss of memory or capability. It is logical to consider summarizing or consolidating some of the memory files.")

if __name__ == "__main__":
    main()
