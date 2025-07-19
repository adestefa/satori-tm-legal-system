#!/usr/bin/env python3
"""
Comprehensive Test Runner for TM iSync Adapter System

This script runs the complete test suite including:
- Integration tests
- Error scenario tests
- Performance benchmarks
- Documentation validation
- System health checks

Usage:
    python3 run_all_tests.py                    # Run all tests
    python3 run_all_tests.py --quick            # Run essential tests only
    python3 run_all_tests.py --performance      # Run performance tests
    python3 run_all_tests.py --docs             # Validate documentation
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class TestRunner:
    """Comprehensive test runner for the TM iSync adapter system"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.results = {}
        self.start_time = time.time()
        
    def run_command(self, cmd: List[str], timeout: int = 300) -> Dict:
        """Run a command and return results"""
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.base_dir
            )
            
            return {
                "success": result.returncode == 0,
                "duration": time.time() - start_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": 124
            }
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": str(e),
                "returncode": 1
            }
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        prerequisites = [
            ("Python 3", ["python3", "--version"]),
            ("Dashboard availability", ["curl", "-s", "http://127.0.0.1:8000/api/health"]),
            ("Test scripts exist", ["ls", "test_sync.py", "test_errors.py"]),
        ]
        
        all_good = True
        for name, cmd in prerequisites:
            result = self.run_command(cmd, timeout=10)
            if result["success"]:
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ {name}: {result['stderr'][:100]}")
                all_good = False
        
        return all_good
    
    def run_integration_tests(self) -> Dict:
        """Run integration tests"""
        print("\n🧪 Running integration tests...")
        
        test_categories = ["dashboard", "package", "installation", "binary", "sync", "performance"]
        results = {}
        
        for category in test_categories:
            print(f"  Testing {category}...")
            result = self.run_command([
                "python3", "test_sync.py", 
                "--test", category,
                "--output", f"integration_test_{category}.txt"
            ])
            
            results[category] = {
                "success": result["success"],
                "duration": result["duration"]
            }
            
            if result["success"]:
                print(f"    ✅ {category} tests passed ({result['duration']:.1f}s)")
            else:
                print(f"    ❌ {category} tests failed ({result['duration']:.1f}s)")
                print(f"       Error: {result['stderr'][:200]}")
        
        return results
    
    def run_error_scenario_tests(self) -> Dict:
        """Run error scenario tests"""
        print("\n🚨 Running error scenario tests...")
        
        error_scenarios = ["network", "auth", "filesystem", "service", "config", "resource"]
        results = {}
        
        for scenario in error_scenarios:
            print(f"  Testing {scenario} errors...")
            result = self.run_command([
                "python3", "test_errors.py",
                "--scenario", scenario,
                "--output", f"error_test_{scenario}.txt"
            ])
            
            results[scenario] = {
                "success": result["success"],
                "duration": result["duration"]
            }
            
            if result["success"]:
                print(f"    ✅ {scenario} error handling passed ({result['duration']:.1f}s)")
            else:
                print(f"    ❌ {scenario} error handling failed ({result['duration']:.1f}s)")
                print(f"       Error: {result['stderr'][:200]}")
        
        return results
    
    def run_adapter_tests(self) -> Dict:
        """Run Go adapter unit tests"""
        print("\n⚙️  Running adapter unit tests...")
        
        # Change to adapter directory
        adapter_dir = self.base_dir / "adapter"
        if not adapter_dir.exists():
            return {"success": False, "message": "Adapter directory not found"}
        
        # Run Go tests
        result = self.run_command(
            ["go", "test", "-v", "./..."],
            timeout=120
        )
        
        if result["success"]:
            print(f"    ✅ Go tests passed ({result['duration']:.1f}s)")
        else:
            print(f"    ❌ Go tests failed ({result['duration']:.1f}s)")
            print(f"       Error: {result['stderr'][:200]}")
        
        return {
            "success": result["success"],
            "duration": result["duration"],
            "output": result["stdout"]
        }
    
    def run_build_tests(self) -> Dict:
        """Test build process"""
        print("\n🔨 Testing build process...")
        
        adapter_dir = self.base_dir / "adapter"
        if not adapter_dir.exists():
            return {"success": False, "message": "Adapter directory not found"}
        
        # Test build
        result = self.run_command(["make", "build"], timeout=120)
        
        if result["success"]:
            print(f"    ✅ Build successful ({result['duration']:.1f}s)")
            
            # Test binary
            binary_test = self.run_command([
                "./build/tm-isync-adapter", "--help"
            ], timeout=10)
            
            if binary_test["success"]:
                print("    ✅ Binary test passed")
                return {"success": True, "duration": result["duration"]}
            else:
                print(f"    ❌ Binary test failed: {binary_test['stderr'][:100]}")
                return {"success": False, "duration": result["duration"]}
        else:
            print(f"    ❌ Build failed ({result['duration']:.1f}s)")
            print(f"       Error: {result['stderr'][:200]}")
            return {"success": False, "duration": result["duration"]}
    
    def validate_documentation(self) -> Dict:
        """Validate documentation files"""
        print("\n📚 Validating documentation...")
        
        docs_to_check = [
            "USER_GUIDE.md",
            "TROUBLESHOOTING.md", 
            "DEVELOPER.md",
            "test_cases/README.md"
        ]
        
        results = {}
        for doc in docs_to_check:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                # Check file size (should be substantial)
                size = doc_path.stat().st_size
                if size > 1000:  # At least 1KB
                    print(f"    ✅ {doc} ({size:,} bytes)")
                    results[doc] = {"exists": True, "size": size, "valid": True}
                else:
                    print(f"    ⚠️  {doc} is too small ({size} bytes)")
                    results[doc] = {"exists": True, "size": size, "valid": False}
            else:
                print(f"    ❌ {doc} missing")
                results[doc] = {"exists": False, "size": 0, "valid": False}
        
        all_valid = all(r["valid"] for r in results.values())
        return {"success": all_valid, "files": results}
    
    def run_performance_benchmarks(self) -> Dict:
        """Run performance benchmarks"""
        print("\n🚀 Running performance benchmarks...")
        
        # Test Dashboard API performance
        api_tests = [
            "/api/health",
            "/api/icloud/config", 
            "/api/icloud/status"
        ]
        
        results = {}
        for endpoint in api_tests:
            print(f"  Benchmarking {endpoint}...")
            
            # Run multiple requests to get average
            times = []
            for _ in range(5):
                result = self.run_command([
                    "curl", "-w", "%{time_total}",
                    "-o", "/dev/null", "-s",
                    f"http://127.0.0.1:8000{endpoint}"
                ], timeout=10)
                
                if result["success"]:
                    try:
                        response_time = float(result["stdout"].strip())
                        times.append(response_time)
                    except ValueError:
                        pass
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                results[endpoint] = {
                    "avg_response_time": avg_time,
                    "max_response_time": max_time,
                    "success": avg_time < 1.0  # Should be under 1 second
                }
                
                if avg_time < 0.1:
                    print(f"    ✅ {endpoint}: {avg_time:.3f}s avg (excellent)")
                elif avg_time < 0.5:
                    print(f"    ✅ {endpoint}: {avg_time:.3f}s avg (good)")
                elif avg_time < 1.0:
                    print(f"    ⚠️  {endpoint}: {avg_time:.3f}s avg (acceptable)")
                else:
                    print(f"    ❌ {endpoint}: {avg_time:.3f}s avg (slow)")
            else:
                results[endpoint] = {"success": False, "error": "No valid responses"}
                print(f"    ❌ {endpoint}: failed to get response times")
        
        return results
    
    def run_system_health_check(self) -> Dict:
        """Run comprehensive system health check"""
        print("\n🏥 Running system health check...")
        
        health_checks = {
            "dashboard_responsive": self.check_dashboard_health(),
            "adapter_binary_exists": self.check_adapter_binary(),
            "test_data_available": self.check_test_data(),
            "disk_space_adequate": self.check_disk_space(),
            "network_connectivity": self.check_network()
        }
        
        for check_name, result in health_checks.items():
            if result["success"]:
                print(f"    ✅ {check_name}")
            else:
                print(f"    ❌ {check_name}: {result.get('message', 'Failed')}")
        
        return health_checks
    
    def check_dashboard_health(self) -> Dict:
        """Check Dashboard health"""
        result = self.run_command([
            "curl", "-s", "http://127.0.0.1:8000/api/health"
        ], timeout=5)
        return {"success": result["success"]}
    
    def check_adapter_binary(self) -> Dict:
        """Check if adapter binary exists and is executable"""
        binary_path = self.base_dir / "adapter" / "build" / "tm-isync-adapter"
        exists = binary_path.exists()
        executable = exists and os.access(binary_path, os.X_OK)
        
        return {
            "success": exists and executable,
            "message": "Binary exists and is executable" if executable else 
                      "Binary missing or not executable"
        }
    
    def check_test_data(self) -> Dict:
        """Check if test data is available"""
        test_cases_dir = self.base_dir / "test_cases"
        has_test_data = test_cases_dir.exists() and any(test_cases_dir.iterdir())
        
        return {
            "success": has_test_data,
            "message": "Test data available" if has_test_data else "Test data missing"
        }
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            import shutil
            free_space = shutil.disk_usage(self.base_dir).free
            # Need at least 1GB free
            adequate = free_space > 1024 * 1024 * 1024
            
            return {
                "success": adequate,
                "message": f"{free_space // (1024*1024)} MB free",
                "free_space_mb": free_space // (1024*1024)
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def check_network(self) -> Dict:
        """Check network connectivity"""
        result = self.run_command(["ping", "-c", "1", "google.com"], timeout=5)
        return {
            "success": result["success"],
            "message": "Network accessible" if result["success"] else "Network unreachable"
        }
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive test summary report"""
        total_duration = time.time() - self.start_time
        
        report = []
        report.append("=" * 80)
        report.append("TM iSync Adapter - Comprehensive Test Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Duration: {total_duration:.1f} seconds")
        report.append("")
        
        # Test Summary
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.results.items():
            if isinstance(results, dict):
                if "success" in results:
                    total_tests += 1
                    if results["success"]:
                        passed_tests += 1
                else:
                    # Multiple sub-tests
                    for sub_result in results.values():
                        if isinstance(sub_result, dict) and "success" in sub_result:
                            total_tests += 1
                            if sub_result["success"]:
                                passed_tests += 1
        
        report.append(f"Overall Result: {passed_tests}/{total_tests} tests passed")
        report.append("")
        
        # Detailed Results
        for category, results in self.results.items():
            report.append(f"\n{category.upper().replace('_', ' ')}:")
            report.append("-" * 40)
            
            if isinstance(results, dict) and "success" in results:
                status = "✅ PASS" if results["success"] else "❌ FAIL"
                duration = results.get("duration", 0)
                report.append(f"{status} ({duration:.1f}s)")
            else:
                for sub_name, sub_result in results.items():
                    if isinstance(sub_result, dict) and "success" in sub_result:
                        status = "✅ PASS" if sub_result["success"] else "❌ FAIL"
                        duration = sub_result.get("duration", 0)
                        report.append(f"  {status} {sub_name} ({duration:.1f}s)")
        
        # Recommendations
        report.append("\n\nRECOMMENDATIONS:")
        report.append("-" * 20)
        
        if passed_tests == total_tests:
            report.append("🎉 All tests passed! System is ready for production use.")
        else:
            report.append("⚠️  Some tests failed. Review failed tests before deployment.")
            report.append("📝 Check individual test reports for detailed error information.")
            report.append("🔧 Run troubleshooting guide for failed components.")
        
        report.append("\n📚 Documentation available:")
        report.append("   - USER_GUIDE.md: Complete user documentation")
        report.append("   - TROUBLESHOOTING.md: Problem resolution guide")
        report.append("   - DEVELOPER.md: Technical implementation details")
        
        return "\n".join(report)
    
    def run_quick_tests(self):
        """Run essential tests only"""
        print("🚀 Running quick test suite...")
        
        self.results["prerequisites"] = {"success": self.check_prerequisites()}
        self.results["health_check"] = self.run_system_health_check()
        self.results["build_test"] = self.run_build_tests()
        self.results["basic_integration"] = self.run_command([
            "python3", "test_sync.py", "--test", "dashboard"
        ])
    
    def run_full_tests(self):
        """Run complete test suite"""
        print("🎯 Running complete test suite...")
        
        # Prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Cannot continue.")
            return False
        
        # All test categories
        self.results["health_check"] = self.run_system_health_check()
        self.results["build_test"] = self.run_build_tests()
        self.results["adapter_tests"] = self.run_adapter_tests()
        self.results["integration_tests"] = self.run_integration_tests()
        self.results["error_tests"] = self.run_error_scenario_tests()
        self.results["performance_tests"] = self.run_performance_benchmarks()
        self.results["documentation"] = self.validate_documentation()
        
        return True

def main():
    parser = argparse.ArgumentParser(description="TM iSync Adapter Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--docs", action="store_true", help="Validate documentation only")
    parser.add_argument("--output", default="comprehensive_test_report.txt", 
                       help="Output file for test report")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.docs:
            print("📚 Validating documentation only...")
            runner.results["documentation"] = runner.validate_documentation()
        elif args.performance:
            print("🚀 Running performance tests only...")
            runner.results["performance_tests"] = runner.run_performance_benchmarks()
        elif args.quick:
            runner.run_quick_tests()
        else:
            success = runner.run_full_tests()
            if not success:
                sys.exit(1)
        
        # Generate and save report
        report = runner.generate_summary_report()
        
        # Print to console
        print("\n" + report)
        
        # Save to file
        with open(args.output, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Detailed test report saved to: {args.output}")
        
        # Exit with appropriate code
        failed_tests = 0
        for results in runner.results.values():
            if isinstance(results, dict):
                if "success" in results and not results["success"]:
                    failed_tests += 1
                else:
                    for sub_result in results.values():
                        if isinstance(sub_result, dict) and "success" in sub_result and not sub_result["success"]:
                            failed_tests += 1
        
        sys.exit(1 if failed_tests > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test run failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()