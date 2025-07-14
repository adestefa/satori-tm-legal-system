#!/usr/bin/env python3
"""
Test script for damage extraction functionality
"""

import sys
import os
sys.path.append('/Users/corelogic/satori-dev/TM/tiger')
sys.path.append('/Users/corelogic/satori-dev/TM/shared-schema')

from app.core.extractors.damage_extractor import DamageExtractor, DamageItem

def test_damage_extraction():
    """Test the damage extraction with sample attorney notes"""
    
    # Read the sample attorney notes
    sample_file = '/Users/corelogic/satori-dev/TM/test-data/test-cases/enhanced_atty_notes_sample.txt'
    
    try:
        with open(sample_file, 'r') as f:
            attorney_notes_text = f.read()
        
        print("🔍 Testing Damage Extraction")
        print("=" * 50)
        
        # Initialize damage extractor
        extractor = DamageExtractor()
        
        # Extract damages
        damages = extractor.extract_damages(attorney_notes_text)
        
        print(f"📊 Extracted {len(damages)} damages:")
        print()
        
        # Display each damage
        for i, damage in enumerate(damages, 1):
            print(f"{i}. {damage.category}/{damage.type}")
            print(f"   Entity: {damage.entity}")
            print(f"   Date: {damage.date}")
            print(f"   Evidence: {'✅ Yes' if damage.evidence_available else '❌ No'}")
            print(f"   Description: {damage.description}")
            print()
        
        # Show categorized damages
        categorized = extractor.categorize_damages(damages)
        print("📈 Damage Categories:")
        print("-" * 30)
        for category, items in categorized.items():
            print(f"{category}: {len(items)} damages")
            for item in items:
                evidence_icon = "✅" if item.evidence_available else "⚠️"
                print(f"  {evidence_icon} {item.type}: {item.entity}")
        print()
        
        # Show summary statistics
        summary = extractor.get_damage_summary(damages)
        print("📋 Summary Statistics:")
        print("-" * 30)
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing damage extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_damage_extraction()
    sys.exit(0 if success else 1)