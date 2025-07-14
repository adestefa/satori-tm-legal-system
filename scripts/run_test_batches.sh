#!/bin/bash

# Activate the virtual environment
echo "Activating Python virtual environment..."
source venv/bin/activate
echo

# --- Test Functions ---

run_legal_entity_tests() {
    echo "--- Running Test Suite: TestLegalEntityExtractor ---"
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_case_number_federal
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_case_number_state
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_court_southern_district
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_parties_simple
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_parties_multiple_defendants
    python3 -m unittest tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_denial_information
   
}

run_consolidation_tests() {
    echo "--- Running Test Suite: TestCaseConsolidator ---"
    python3 -m unittest tests.test_legal_extraction.TestCaseConsolidator.test_consolidate_single_document
    python3 -m unittest tests.test_legal_extraction.TestCaseConsolidator.test_consolidate_multiple_documents_consistent
    python3 -m unittest tests.test_legal_extraction.TestCaseConsolidator.test_consolidate_conflicting_information
    python3 -m unittest tests.test_legal_extraction.TestCaseConsolidator.test_confidence_calculation
    python3 -m unittest tests.test_legal_extraction.TestCaseConsolidator.test_empty_results
   
}

run_integration_tests() {
    echo "--- Running Test Suite: TestIntegrationScenarios ---"
    python3 -m unittest tests.test_legal_extraction.TestIntegrationScenarios.test_fcra_case_workflow
    python3 -m unittest tests.test_legal_extraction.TestIntegrationScenarios.test_complaint_json_generation
  

run_edge_case_tests() {
    echo "--- Running Test Suite: TestEdgeCases ---"
    python3 -m unittest tests.test_legal_extraction.TestEdgeCases.test_malformed_case_numbers
    python3 -m unittest tests.test_legal_extraction.TestEdgeCases.test_empty_document
    python3 -m unittest tests.test_legal_extraction.TestEdgeCases.test_non_legal_document
    python3 -m unittest tests.test_legal_extraction.TestEdgeCases.test_mixed_document_types
    
}

run_validation_tests() {
    echo "--- Running Test Suite: TestComplaintJsonValidation ---"
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_valid_complaint_json_structure
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_case_number_format_validation
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_court_district_validation
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_party_name_validation
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_confidence_score_validation
    python3 -m unittest tests.test_data_validation.TestComplaintJsonValidation.test_address_format_validation
    echo "--- Running Test Suite: TestDataIntegrity ---"
    python3 -m unittest tests.test_data_validation.TestDataIntegrity.test_case_number_consistency
    python3 -m unittest tests.test_data_validation.TestDataIntegrity.test_party_name_consistency
    python3 -m unittest tests.test_data_validation.TestDataIntegrity.test_date_format_consistency
    echo "--- Running Test Suite: TestLegalStandardsCompliance ---"
    python3 -m unittest tests.test_data_validation.TestLegalStandardsCompliance.test_fcra_case_requirements
    python3 -m unittest tests.test_data_validation.TestLegalStandardsCompliance.test_federal_court_jurisdiction_requirements
    python3 -m unittest tests.test_data_validation.TestLegalStandardsCompliance.test_complaint_completeness_validation
    
}

run_performance_tests() {
    echo "--- Running Test Suite: TestPerformance ---"
    python3 -m unittest tests.test_performance.TestPerformance.test_extraction_performance_small_document
    python3 -m unittest tests.test_performance.TestPerformance.test_extraction_performance_medium_document
    python3 -m unittest tests.test_performance.TestPerformance.test_extraction_performance_large_document
    python3 -m unittest tests.test_performance.TestPerformance.test_batch_processing_performance
    python3 -m unittest tests.test_performance.TestPerformance.test_consolidation_performance
    python3 -m unittest tests.test_performance.TestPerformance.test_memory_leak_detection
    python3 -m unittest tests.test_performance.TestPerformance.test_regex_performance
    python3 -m unittest tests.test_performance.TestPerformance.test_concurrent_processing_simulation
    echo "--- Running Test Suite: TestScalabilityLimits ---"
    python3 -m unittest tests.test_performance.TestScalabilityLimits.test_maximum_document_size
    python3 -m unittest tests.test_performance.TestScalabilityLimits.test_maximum_case_folder_size
   
}

# --- Main Execution ---
main() {
    echo "=================================================="
    echo " Satori Tiger - Batched Test Runner"
    echo "=================================================="
    
    run_legal_entity_tests
    run_consolidation_tests
    run_integration_tests
    run_edge_case_tests
    run_validation_tests
    run_performance_tests

    echo
    echo "All test batches complete."
    echo "=================================================="
}

main

# Deactivate the virtual environment
echo
echo "Deactivating Python virtual environment..."
deactivate
