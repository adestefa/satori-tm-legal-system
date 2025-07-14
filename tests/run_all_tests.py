#!/usr/bin/env python3
"""
Comprehensive test runner for Tiger Legal Extraction System.
Runs all test suites and generates detailed reports.
"""

import unittest
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from io import StringIO

# Import all test modules
from test_legal_extraction import (
    TestLegalEntityExtractor,
    TestCaseConsolidator, 
    TestIntegrationScenarios,
    TestEdgeCases
)
from test_performance import TestPerformance, TestScalabilityLimits
from test_data_validation import (
    TestComplaintJsonValidation,
    TestDataIntegrity,
    TestLegalStandardsCompliance
)


class TestResult:
    """Custom test result class to capture detailed test information."""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.successes = []
        self.start_time = None
        self.end_time = None 
        self.performance_metrics = {}
    
    def start_test(self, test):
        """Called when a test starts."""
        if self.start_time is None:
            self.start_time = time.time()
    
    def stop_test(self, test):
        """Called when a test stops."""
        self.end_time = time.time()
        self.tests_run += 1
    
    def add_success(self, test):
        """Called when a test passes."""
        self.successes.append(test)
    
    def add_failure(self, test, traceback):
        """Called when a test fails."""
        self.failures.append((test, traceback))
    
    def add_error(self, test, traceback):
        """Called when a test has an error."""
        self.errors.append((test, traceback))
    
    def add_skip(self, test, reason):
        """Called when a test is skipped."""
        self.skipped.append((test, reason))
    
    @property
    def total_time(self):
        """Total execution time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    @property
    def success_rate(self):
        """Calculate success rate as percentage."""
        if self.tests_run == 0:
            return 0
        return (len(self.successes) / self.tests_run) * 100
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        return {
            "total_tests": self.tests_run,
            "successes": len(self.successes),
            "failures": len(self.failures),
            "errors": len(self.errors),
            "skipped": len(self.skipped),
            "success_rate": round(self.success_rate, 2),
            "total_time": round(self.total_time, 2),
            "performance_metrics": self.performance_metrics
        }


class ComprehensiveTestRunner:
    """Main test runner that orchestrates all test suites."""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.results = TestResult()
        
    def run_test_suite(self, test_class, suite_name: str):
        """Run a specific test suite."""
        print(f"\n{'='*60}")
        print(f"RUNNING {suite_name.upper()}")
        print(f"{'='*60}")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        # Capture output for analysis
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream, 
            verbosity=self.verbosity,
            buffer=True
        )
        
        suite_start_time = time.time()
        result = runner.run(suite)
        suite_end_time = time.time()
        
        # Update overall results
        self.results.tests_run += result.testsRun
        self.results.failures.extend(result.failures)
        self.results.errors.extend(result.errors)
        self.results.skipped.extend(getattr(result, 'skipped', []))
        
        # Calculate successes
        suite_successes = result.testsRun - len(result.failures) - len(result.errors)
        self.results.successes.extend([f"{suite_name}_success"] * suite_successes)
        
        # Print results
        output = stream.getvalue()
        print(output)
        
        # Suite summary
        suite_time = suite_end_time - suite_start_time
        print(f"\n{suite_name} Summary:")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Successes: {suite_successes}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Time: {suite_time:.2f}s")
        
        if result.failures:
            print(f"  Failed tests:")
            for test, _ in result.failures:
                print(f"    - {test}")
        
        if result.errors:
            print(f"  Error tests:")
            for test, _ in result.errors:
                print(f"    - {test}")
        
        return result
    
    def run_all_tests(self):
        """Run all test suites in order."""
        print("🐅 TIGER LEGAL EXTRACTION SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        
        overall_start_time = time.time()
        
        # Define test suites in order of execution
        test_suites = [
            (TestLegalEntityExtractor, "Legal Entity Extraction Tests"),
            (TestCaseConsolidator, "Case Consolidation Tests"), 
            (TestIntegrationScenarios, "Integration Scenario Tests"),
            (TestEdgeCases, "Edge Case Tests"),
            (TestComplaintJsonValidation, "Complaint JSON Validation Tests"),
            (TestDataIntegrity, "Data Integrity Tests"),
            (TestLegalStandardsCompliance, "Legal Standards Compliance Tests"),
            (TestPerformance, "Performance Tests"),
            (TestScalabilityLimits, "Scalability Limit Tests")
        ]
        
        # Run each test suite
        for test_class, suite_name in test_suites:
            try:
                self.run_test_suite(test_class, suite_name)
            except Exception as e:
                print(f"CRITICAL ERROR in {suite_name}: {e}")
                self.results.errors.append((suite_name, str(e)))
        
        overall_end_time = time.time()
        
        # Generate final report
        self.results.start_time = overall_start_time
        self.results.end_time = overall_end_time
        
        self.print_final_report()
        self.save_test_report()
        
        return self.results.success_rate >= 80  # Return True if >= 80% success rate
    
    def print_final_report(self):
        """Print comprehensive final test report."""
        print("\n" + "=" * 80)
        print("🐅 TIGER LEGAL EXTRACTION SYSTEM - FINAL TEST REPORT")
        print("=" * 80)
        
        summary = self.results.generate_summary()
        
        print(f"Total Tests Run: {summary['total_tests']}")
        print(f"Successes: {summary['successes']} ✅")
        print(f"Failures: {summary['failures']} ❌")
        print(f"Errors: {summary['errors']} 🚨")
        print(f"Skipped: {summary['skipped']} ⏭️")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Time: {summary['total_time']:.2f}s")
        
        # Status indicator
        if summary['success_rate'] >= 95:
            status = "🟢 EXCELLENT"
        elif summary['success_rate'] >= 80:
            status = "🟡 GOOD"
        elif summary['success_rate'] >= 60:
            status = "🟠 NEEDS IMPROVEMENT"
        else:
            status = "🔴 CRITICAL ISSUES"
        
        print(f"\nOverall Status: {status}")
        
        # Detailed failure analysis
        if self.results.failures:
            print(f"\n{'='*40}")
            print("FAILURE ANALYSIS")
            print(f"{'='*40}")
            
            failure_categories = {}
            for test, traceback in self.results.failures:
                test_name = str(test).split('.')[-1].split()[0]
                category = test_name.split('_')[1] if '_' in test_name else 'other'
                
                if category not in failure_categories:
                    failure_categories[category] = []
                failure_categories[category].append(test_name)
            
            for category, tests in failure_categories.items():
                print(f"\n{category.upper()} Issues ({len(tests)} tests):")
                for test in tests:
                    print(f"  - {test}")
        
        # Performance insights
        print(f"\n{'='*40}")
        print("PERFORMANCE INSIGHTS")
        print(f"{'='*40}")
        print(f"Average test execution time: {summary['total_time']/summary['total_tests']:.3f}s")
        
        if summary['total_time'] > 60:
            print("⚠️  Test suite takes longer than 1 minute - consider optimization")
        elif summary['total_time'] < 10:
            print("✅ Fast test execution - good for CI/CD")
        
        # Recommendations
        print(f"\n{'='*40}")
        print("RECOMMENDATIONS")
        print(f"{'='*40}")
        
        if summary['success_rate'] < 80:
            print("🔴 Critical: Fix failing tests before production deployment")
        
        if summary['failures'] > 0:
            print(f"🟡 Address {summary['failures']} failing test(s)")
        
        if summary['errors'] > 0:
            print(f"🚨 Fix {summary['errors']} test error(s) - these indicate code issues")
        
        if summary['success_rate'] >= 95:
            print("🟢 Excellent test coverage - system ready for production")
    
    def save_test_report(self):
        """Save detailed test report to JSON file."""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": self.results.generate_summary(),
            "failures": [
                {"test": str(test), "traceback": traceback} 
                for test, traceback in self.results.failures
            ],
            "errors": [
                {"test": str(test), "traceback": traceback}
                for test, traceback in self.results.errors
            ]
        }
        
        report_file = Path("test_results.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📊 Detailed test report saved to: {report_file}")


def main():
    """Main entry point for test runner."""
    runner = ComprehensiveTestRunner(verbosity=2)
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()