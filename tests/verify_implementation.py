"""
Implementation Verification Script

This script verifies that the documented modules and functions in the project's
documentation actually exist in the codebase. This is to prevent "implementation
fraud", where documentation claims the existence of features that have not
actually been implemented.
"""

import re
import importlib
from pathlib import Path

def verify_implementation(prd_file: Path, src_root: Path):
    """
    Verifies the implementation of the documented modules and functions.

    Args:
        prd_file: The path to the PRD file.
        src_root: The path to the source root.
    """
    print("Verifying implementation...")

    with open(prd_file, "r", encoding="utf-8") as f:
        prd_content = f.read()

    # Find all documented modules and functions
    modules = re.findall(r"`([\w./]+)`", prd_content)
    functions = re.findall(r"`([\w.]+)`", prd_content)

    missing_modules = []
    missing_functions = []

    # Verify modules
    for module in modules:
        if "/" in module:
            module_path = src_root / module
            if not module_path.exists():
                missing_modules.append(module)

    # Verify functions
    for function in functions:
        if "." in function:
            module_name, function_name = function.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                if not hasattr(module, function_name):
                    missing_functions.append(function)
            except ImportError:
                missing_modules.append(module_name)

    if not missing_modules and not missing_functions:
        print("Implementation verification successful!")
    else:
        if missing_modules:
            print("\nMissing modules:")
            for module in missing_modules:
                print(f"  - {module}")
        if missing_functions:
            print("\nMissing functions:")
            for function in missing_functions:
                print(f"  - {function}")
        print("\nImplementation verification failed.")

if __name__ == "__main__":
    prd_file = Path("prd/prd.md")
    src_root = Path(".")
    verify_implementation(prd_file, src_root)
