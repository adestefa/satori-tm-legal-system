# Tiger-Monkey Services Testing Guide

This guide provides instructions on how to test the Tiger, Monkey, and Browser services, both individually and as an integrated system.

## 1. Critical Note on Virtual Environments

**IMPORTANT:** The project uses separate Python virtual environments (`venv`) for the Tiger and Monkey services. The `run.sh` scripts in each service's directory are designed to run the main application commands (e.g., `hydrated-json`, `build-complaint`) and automatically handle the `venv` activation.

For running **standalone Python scripts** (like utility or conversion scripts), you **must** invoke the Python interpreter directly from the service's `venv`.

*   **Correct way to run a service command:**
    ```bash
    # From within the TM/tiger/ directory
    ./run.sh hydrated-json <args>
    ```

*   **Correct way to run a standalone script (using Tiger's venv):**
    ```bash
    # From the TM/ directory
    ./tiger/venv/bin/python3 ./scripts/my_script.py
    ```

## 2. Automated Testing (Recommended)

The most efficient way to test the application is by using the provided test scripts located in the `scripts/` directory. These scripts cover service-specific functionality, integration, and health checks.

### Running Tests

All test commands should be run from the root of the `TM/` directory.

#### **Service-Specific Tests**

*   **Test Tiger Service:** Runs a full test suite for the Tiger service.
    ```bash
    ./scripts/t.sh
    ```

*   **Test Monkey Service:** Runs a full test suite for the Monkey service.
    ```bash
    ./scripts/m.sh
    ```

*   **Test Browser PDF Service:** Runs a full test suite for the Browser PDF generation service.
    ```bash
    ./browser/run-tests.sh full
    ```

#### **Integration & End-to-End Tests**

*   **Full Integration Test:** Performs a complete end-to-end test of the Tiger to Monkey workflow.
    ```bash
    ./scripts/tm.sh
    ```

*   **Browser PDF Integration Test:** Tests the integrated Monkey + Browser PDF generation workflow.
    ```bash
    ./browser/test-integration.sh
    ```

*   **JSON Engine Test:** A comprehensive test focusing on the JSON generation and consumption pipeline.
    ```bash
    ./scripts/test_json_engine.sh
    ```

#### **Health & Batch Checks**

*   **Quick Health Check:** Runs a fast series of tests to ensure core components are working.
    ```bash
    ./scripts/run_health_check.sh
    ```

*   **Run All Test Batches:** Executes a comprehensive set of batched tests.
    ```bash
    ./scripts/run_test_batches.sh
    ```

*   **Browser PDF Performance Test:** Benchmarks PDF generation performance and quality metrics.
    ```bash
    ./browser/benchmark.sh
    ```

## 3. Manual Testing Instructions

For more granular testing or debugging, you can run commands for each service manually.

### Prerequisites

Before running any manual commands, ensure you have installed all dependencies by running the main installation script from the `TM/` directory:
```bash
./install.sh
```

### Tiger Service Manual Testing

*   **Generate Hydrated JSON for the Youssef Case:**
    ```bash
    /Users/corelogic/satori-dev/TM/tiger/run.sh hydrated-json /Users/corelogic/satori-dev/TM/test-data/cases/youssef -o /Users/corelogic/satori-dev/TM/outputs/tests/
    ```

### Monkey Service Manual Testing

*   **Generate a Complaint Document (HTML only):**
    ```bash
    /Users/corelogic/satori-dev/TM/monkey/run.sh build-complaint /Users/corelogic/satori-dev/TM/outputs/tests/youssef/hydrated_FCRA_YOUSSEF_EMAN_20250714.json --template ground_truth_complaint.html -o /Users/corelogic/satori-dev/TM/outputs/tests/
    ```

*   **Generate a Complaint Document with PDF:**
    ```bash
    /Users/corelogic/satori-dev/TM/monkey/run.sh build-complaint /Users/corelogic/satori-dev/TM/outputs/tests/youssef/hydrated_FCRA_YOUSSEF_EMAN_20250714.json --with-pdf
    ```

### Browser PDF Service Manual Testing

*   **Generate PDF from HTML file:**
    ```bash
    cd /Users/corelogic/satori-dev/TM
    ./browser/print.py single outputs/tests/youssef/complaint_youssef.html outputs/browser/complaint_youssef.pdf
    ```

*   **Test with Node.js service directly:**
    ```bash
    cd /Users/corelogic/satori-dev/TM/browser
    node pdf-generator.js ../outputs/tests/youssef/complaint_youssef.html
    ```

*   **Run single file test:**
    ```bash
    cd /Users/corelogic/satori-dev/TM/browser
    ./test-single.sh ../outputs/tests/youssef/complaint_youssef.html
    ```

*   **Run batch processing test:**
    ```bash
    cd /Users/corelogic/satori-dev/TM/browser
    ./test-batch.sh ../outputs/tests/ ../outputs/browser/
    ```

## 4. Integrated Testing Workflows

### Complete End-to-End Testing (Tiger → Monkey → Browser)

*   **Full workflow test with current case data:**
    ```bash
    # Step 1: Generate hydrated JSON from Tiger
    ./tiger/run.sh hydrated-json test-data/sync-test-cases/youssef -o outputs/tests/youssef/

    # Step 2: Generate HTML and PDF documents from Monkey + Browser
    ./monkey/run.sh build-complaint outputs/tests/youssef/hydrated_FCRA_YOUSSEF_EMAN_20250714.json --with-pdf

    # Step 3: Verify outputs
    ls -la outputs/monkey/processed/$(date +%Y-%m-%d)/
    ls -la outputs/browser/
    ```

### Test Case Data

The system includes several test cases with real legal data:

*   **Youssef Case** (`test-data/sync-test-cases/youssef/`):
    - Complex FCRA case with multiple defendants
    - Includes adverse action letters and attorney notes
    - Generated JSON: `outputs/tests/youssef/hydrated_FCRA_YOUSSEF_EMAN_20250714.json`

*   **Rodriguez Case** (`test-data/sync-test-cases/Rodriguez/`):
    - Multi-defendant FCRA case
    - Generated JSON: `outputs/tests/Rodriguez/hydrated_FCRA_Rodriguez_Carlos_20250714.json`

### Validation and Quality Assurance

*   **Validate generated PDF quality:**
    ```bash
    # Check PDF file properties
    file outputs/browser/complaint.pdf

    # Verify PDF page count and dimensions
    pdfinfo outputs/browser/complaint.pdf
    ```

*   **Compare HTML vs PDF output:**
    ```bash
    # Generate both formats
    ./monkey/run.sh build-complaint outputs/tests/youssef/hydrated_FCRA_YOUSSEF_EMAN_20250714.json
    ./browser/print.py single monkey/outputs/monkey/processed/$(date +%Y-%m-%d)/complaint.html outputs/browser/complaint_comparison.pdf

    # View HTML in browser for comparison
    open monkey/outputs/monkey/processed/$(date +%Y-%m-%d)/complaint.html
    ```

## 5. Test Output Locations

*   **Tiger Outputs**: `outputs/tests/[case_name]/`
*   **Monkey HTML Outputs**: `monkey/outputs/monkey/processed/[date]/`
*   **Browser PDF Outputs**: `outputs/browser/`
*   **Test Artifacts**: `browser/test-outputs/`

## 6. Troubleshooting Common Test Issues

*   **PDF Generation Timeout**: Increase timeout in `browser/print.py` or check system resources
*   **Permission Errors**: Ensure scripts are executable: `chmod +x browser/*.sh`
*   **Node.js Not Found**: Install Node.js: `brew install node` (macOS)
*   **Virtual Environment Issues**: Run `./install.sh` to rebuild environments

