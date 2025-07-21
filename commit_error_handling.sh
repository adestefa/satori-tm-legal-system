#!/bin/bash
git commit -m "fix(processing): Add robust error handling to case processing

The case processing thread was not properly handling exceptions from the Tiger service, causing it to fail silently and leave the case in a perpetual 'processing' state.

This commit wraps the call to the service runner in a try/except block. If Tiger fails, the exception is now caught, the case status is set to 'ERROR', and an event is broadcast to the UI. This ensures the system is resilient and provides accurate feedback to the user."
