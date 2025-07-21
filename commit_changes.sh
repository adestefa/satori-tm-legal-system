#!/bin/bash
git commit -m "refactor(dashboard): Restore manifest-driven state management

This commit resolves the critical UI and state management defects introduced by a previous agent. The changes restore the system to its intended, logical architecture where processing_manifest.txt is the single source of truth.

Key changes:
- Removed the redundant .case_status.json state file and all associated read/write logic from data_manager.py.
- Eliminated uncontrolled, continuous polling and WebSocket-based refreshing from the frontend in main.js.
- Implemented a new, strictly controlled, self-terminating polling mechanism that is active *only* when a case is in the 'PROCESSING' state. Its sole purpose is to update file-level animations.

This restores UI stability, eliminates excessive network requests, and aligns the implementation with the project's core architectural principles."
