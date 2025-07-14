import sys
from pathlib import Path

# Add app and shared-schema directories to Python path
tiger_dir = Path(__file__).parent.parent / "tiger"
app_dir = tiger_dir / "app"
shared_schema_dir = Path(__file__).parent.parent / "shared-schema"
sys.path.insert(0, str(tiger_dir))
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(shared_schema_dir))

try:
    from satori_schema import HydratedJSON, validate_hydrated_json
    print(f'✅ Shared schema imported successfully')
    
    from core.services.hydrated_json_consolidator import HydratedJSONConsolidator
    print(f'✅ Tiger hydrated JSON consolidator imported successfully')
    
    # Test schema validation
    test_data = {
        'case_information': {'court_name': 'Test', 'court_district': 'Test District', 'case_number': '123', 'document_title': 'Test', 'document_type': 'FCRA'},
        'parties': {'plaintiff': {'name': 'Test', 'address': {'street': '123 Main', 'city': 'Test', 'state': 'NY', 'zip_code': '12345'}, 'residency': 'Test', 'consumer_status': 'Test'}, 'defendants': [{'name': 'Test Defendant', 'short_name': 'Test', 'type': 'Test', 'state_of_incorporation': 'DE', 'business_status': 'Test'}]},
        'jurisdiction_and_venue': {'federal_jurisdiction': {'basis': 'Test', 'citation': 'Test'}, 'supplemental_jurisdiction': {'basis': 'Test', 'citation': 'Test'}, 'venue': {'basis': 'Test', 'citation': 'Test'}},
        'preliminary_statement': 'Test',
        'factual_background': {'summary': 'Test'},
        'causes_of_action': [{'count_number': 1, 'title': 'Test Cause', 'against_defendants': ['Test'], 'allegations': [{'citation': 'Test', 'description': 'Test'}]}],
        'prayer_for_relief': {'damages': ['Test'], 'injunctive_relief': ['Test'], 'costs_and_fees': ['Test']},
        'jury_demand': True,
        'filing_details': {'date': '2025-01-01', 'signature_date': '2025-01-01'},
        'metadata': {'tiger_case_id': 'Test', 'format_version': '3.0'}
    }
    is_valid, errors, warnings = validate_hydrated_json(test_data)
    print(f'✅ Schema validation test: {"PASSED" if is_valid else "FAILED"}')
    
except Exception as e:
    print(f'❌ Schema integration test failed: {e}')
