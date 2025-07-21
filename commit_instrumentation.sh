#!/bin/bash
git commit -m "fix(persistence): Add error logging for manifest parsing

The case state was failing to persist across refreshes because of a silent failure in parsing the case status from the manifest file.

This commit instruments the parsing logic within `data_manager.py` to log a critical error if an unknown status is encountered. This will allow for precise diagnosis of the state persistence failure. It also adds `.strip()` to make parsing more robust against whitespace issues."
