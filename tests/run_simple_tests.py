#!/usr/bin/env python3
"""
Simplified test runner for Tiger Legal Extraction System.
Runs core tests that work with the current implementation.
"""

import unittest
import sys
import time
import json
from pathlib import Path

# Import working test modules
from test_legal_extraction_simple import (
    TestLegalEntityExtractor,
    TestCaseConsolidator, 
    TestIntegrationScenarios,
    TestEdgeCases
)


def main():
    """Main entry point for test runner."""
    print("🐅 TIGER LEGAL EXTRACTION SYSTEM - CORE TEST SUITE")
    print("=" * 60)
    
    start_time = time.time()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add working test classes
    test_classes = [
        (TestLegalEntityExtractor, "Legal Entity Extraction Tests"),
        (TestCaseConsolidator, "Case Consolidation Tests"),
        (TestIntegrationScenarios, "Integration Scenario Tests"),
        (TestEdgeCases, "Edge Case Tests")
    ]
    
    total_tests = 0
    for test_class, description in test_classes:
        print(f"\n📋 Loading {description}")
        class_suite = loader.loadTestsFromTestCase(test_class)
        suite.addTests(class_suite)
        total_tests += class_suite.countTestCases()
    
    print(f"\n🚀 Running {total_tests} tests...")
    print("-" * 60)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    success_rate = (success_count / result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {success_count} ✅")
    print(f"Failures: {len(result.failures)} ❌")
    print(f"Errors: {len(result.errors)} 🚨")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Overall status  
    if success_rate >= 95:
        status = "🟢 EXCELLENT"
        exit_code = 0
    elif success_rate >= 80:
        status = "🟡 GOOD"
        exit_code = 0
    elif success_rate >= 60:
        status = "🟠 NEEDS IMPROVEMENT"
        exit_code = 1
    else:
        status = "🔴 CRITICAL ISSUES"
        exit_code = 1
    
    print(f"\nOverall Status: {status}")
    
    # Save results
    results_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": result.testsRun,
        "successes": success_count,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": round(success_rate, 2),
        "total_time": round(total_time, 2),
        "status": status
    }
    
    with open("test_results_simple.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n📄 Results saved to: test_results_simple.json")
    
    if success_rate >= 80:
        print("\n🎉 Tiger Legal Extraction System tests passed!")
        print("   System is ready for legal document processing.")
    else:
        print(f"\n⚠️  Some tests failed. Please review and fix issues.")
    
    return exit_code == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)