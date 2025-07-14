#!/usr/bin/env python3
"""
Test script for enhanced date extraction
"""

import sys
import os
import json

# Add the tiger app to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.extractors.date_extractor import EnhancedDateExtractor

def test_date_extraction():
    """Test the enhanced date extraction on Wells Fargo text"""
    
    # Sample text from Wells Fargo adverse action letter
    test_text = """
## WELLS FARGO AUTO

Wells Fargo Dealer Services P.O. Box 29704 Phoenix, AZ 85038-9704

Carlos Rodriguez 123 Main Street Brooklyn, NY 11201

## Regarding your recent auto loan application

Dear Carlos Rodriguez,

Thank you for your application for financing. After careful review, we regret that we are unable to approve your application at this time. This decision was based, in whole or in part, on information from your consumer credit report.

Your Credit Score:

595

Date:

04/18/2025

Date: April 20, 2025

## Scores Range From: 300 to 850
"""
    
    # Initialize the enhanced date extractor
    extractor = EnhancedDateExtractor()
    
    # Extract dates
    print("🔍 Testing Enhanced Date Extraction")
    print("=" * 50)
    
    extracted_dates = extractor.extract_dates_from_text(test_text, "denial_letter")
    
    print(f"Found {len(extracted_dates)} dates:")
    print()
    
    for i, date_obj in enumerate(extracted_dates, 1):
        print(f"Date {i}:")
        print(f"  Raw Text: {date_obj.raw_text}")
        print(f"  Parsed Date: {date_obj.parsed_date}")
        print(f"  Context: {date_obj.context.value}")
        print(f"  Confidence: {date_obj.confidence:.2f}")
        print(f"  Source Line: {date_obj.source_line.strip()}")
        print()
    
    # Test timeline extraction
    print("📅 Timeline Dates:")
    print("=" * 30)
    
    timeline_dates = extractor.extract_timeline_dates(test_text, "denial_letter")
    
    for context, dates in timeline_dates.items():
        if dates:
            print(f"{context}:")
            for date_obj in dates:
                print(f"  - {date_obj.parsed_date} (confidence: {date_obj.confidence:.2f})")
    
    # Test chronological validation
    print("\n⏰ Chronological Validation:")
    print("=" * 35)
    
    validation_result = extractor.validate_date_chronology(extracted_dates)
    
    print(f"Valid Timeline: {validation_result['is_valid']}")
    if validation_result['errors']:
        print("Errors:")
        for error in validation_result['errors']:
            print(f"  - {error}")
    
    if validation_result['warnings']:
        print("Warnings:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    print(f"\nTimeline Events: {len(validation_result['timeline'])}")
    for event in validation_result['timeline']:
        print(f"  - {event['date']}: {event['context']} (confidence: {event['confidence']:.2f})")

if __name__ == "__main__":
    test_date_extraction()