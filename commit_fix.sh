#!/bin/bash
git commit -m "fix(runner): Ensure final case status is written to correct manifest

A logical flaw was identified where the `run_monkey_generation` function was writing the 'CASE_STATUS|COMPLETE' entry to a manifest in the output directory instead of the source directory. This prevented the frontend poller from ever detecting the completion of a case.

This commit corrects the path resolution logic to ensure the final status is always written to the manifest in the source case directory, allowing the UI to correctly transition to its final state."
