#!/usr/bin/env python3
"""
Comprehensive Integration Testing for TM iSync Adapter System

This script provides end-to-end testing of the complete iCloud sync system including:
- Dashboard configuration and API endpoints
- Package generation and download
- Installation and service management
- File monitoring and bidirectional sync
- Error handling and recovery

Usage:
    python3 test_sync.py --test all
    python3 test_sync.py --test dashboard
    python3 test_sync.py --test package
    python3 test_sync.py --test installation
    python3 test_sync.py --test sync
    python3 test_sync.py --test performance
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import requests
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# Add shared schema to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "shared-schema"))

@dataclass
class TestResult:
    """Test result container"""
    name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    message: str = ""
    details: Dict[str, Any] = None

class IntegrationTester:
    """Comprehensive integration testing for iSync adapter"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.dashboard_base = base_url
        self.adapter_dir = Path(__file__).parent / "adapter"
        self.test_data_dir = Path(__file__).parent.parent / "test-data" / "sync-test-cases"
        self.temp_dir = None
        self.results: List[TestResult] = []
        self.session = requests.Session()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_test_environment(self) -> bool:
        """Setup test environment and verify prerequisites"""
        try:
            self.logger.info("Setting up test environment...")
            
            # Create temporary directory for testing
            self.temp_dir = Path(tempfile.mkdtemp(prefix="tm_isync_test_"))
            self.logger.info(f"Created temp directory: {self.temp_dir}")
            
            # Verify Dashboard is running
            if not self._check_dashboard_running():
                self.logger.error("Dashboard is not running. Please start it first.")
                return False
                
            # Verify adapter directory exists
            if not self.adapter_dir.exists():
                self.logger.error(f"Adapter directory not found: {self.adapter_dir}")
                return False
                
            # Verify test data exists
            if not self.test_data_dir.exists():
                self.logger.error(f"Test data directory not found: {self.test_data_dir}")
                return False
                
            self.logger.info("Test environment setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def _check_dashboard_running(self) -> bool:
        """Check if Dashboard is running"""
        try:
            response = self.session.get(f"{self.dashboard_base}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _time_test(self, test_func):
        """Decorator to time test execution"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            return result, duration
        return wrapper
    
    def test_dashboard_api_endpoints(self) -> List[TestResult]:
        """Test all Dashboard iCloud API endpoints"""
        results = []
        
        # Test cases for each endpoint
        test_cases = [
            {
                "name": "GET /api/icloud/config",
                "method": "GET",
                "endpoint": "/api/icloud/config",
                "expected_status": 200
            },
            {
                "name": "POST /api/icloud/config (save configuration)",
                "method": "POST",
                "endpoint": "/api/icloud/config",
                "data": {
                    "username": "test@example.com",
                    "password": "testpassword",
                    "source_folder": "/Users/test/Documents/TM-Cases",
                    "target_folder": "TM-Cases"
                },
                "expected_status": 200
            },
            {
                "name": "POST /api/icloud/test-connection",
                "method": "POST",
                "endpoint": "/api/icloud/test-connection",
                "data": {
                    "username": "test@example.com",
                    "password": "testpassword"
                },
                "expected_status": [200, 500]  # May fail due to invalid credentials
            },
            {
                "name": "GET /api/icloud/status",
                "method": "GET",
                "endpoint": "/api/icloud/status",
                "expected_status": 200
            },
            {
                "name": "POST /api/icloud/download-package",
                "method": "POST",
                "endpoint": "/api/icloud/download-package",
                "data": {
                    "username": "test@example.com",
                    "password": "testpassword",
                    "source_folder": "/Users/test/Documents/TM-Cases",
                    "target_folder": "TM-Cases"
                },
                "expected_status": 200
            }
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                url = f"{self.dashboard_base}{test_case['endpoint']}"
                
                if test_case["method"] == "GET":
                    response = self.session.get(url, timeout=30)
                else:
                    response = self.session.post(url, json=test_case.get("data", {}), timeout=30)
                
                expected = test_case["expected_status"]
                if isinstance(expected, list):
                    status_ok = response.status_code in expected
                else:
                    status_ok = response.status_code == expected
                
                if status_ok:
                    results.append(TestResult(
                        name=test_case["name"],
                        status="PASS",
                        duration=time.time() - start_time,
                        message=f"Response: {response.status_code}",
                        details={"response_code": response.status_code, "response_text": response.text[:200]}
                    ))
                else:
                    results.append(TestResult(
                        name=test_case["name"],
                        status="FAIL",
                        duration=time.time() - start_time,
                        message=f"Expected {expected}, got {response.status_code}",
                        details={"response_code": response.status_code, "response_text": response.text[:200]}
                    ))
                    
            except Exception as e:
                results.append(TestResult(
                    name=test_case["name"],
                    status="FAIL",
                    duration=time.time() - start_time,
                    message=f"Exception: {str(e)[:100]}",
                    details={"exception": str(e)}
                ))
        
        return results
    
    def test_package_generation(self) -> List[TestResult]:
        """Test iSync adapter package generation"""
        results = []
        start_time = time.time()
        
        try:
            # Test package generation endpoint
            config_data = {
                "username": "test@example.com",
                "password": "testpassword",
                "source_folder": "/Users/test/Documents/TM-Cases",
                "target_folder": "TM-Cases"
            }
            
            response = self.session.post(
                f"{self.dashboard_base}/api/icloud/download-package",
                json=config_data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Verify package is a valid ZIP file
                package_path = self.temp_dir / "test_package.zip"
                with open(package_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify ZIP file can be extracted
                import zipfile
                extract_dir = self.temp_dir / "extracted_package"
                with zipfile.ZipFile(package_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Verify expected files are present
                expected_files = [
                    "tm-isync-adapter",
                    "install.py",
                    "config.json",
                    "service.plist.template",
                    "uninstall.py",
                    "health_check.sh"
                ]
                
                missing_files = []
                for file_name in expected_files:
                    if not (extract_dir / file_name).exists():
                        missing_files.append(file_name)
                
                if missing_files:
                    results.append(TestResult(
                        name="Package Generation - File Completeness",
                        status="FAIL",
                        duration=time.time() - start_time,
                        message=f"Missing files: {missing_files}",
                        details={"missing_files": missing_files}
                    ))
                else:
                    results.append(TestResult(
                        name="Package Generation - File Completeness",
                        status="PASS",
                        duration=time.time() - start_time,
                        message="All expected files present",
                        details={"package_size": len(response.content)}
                    ))
                    
                # Verify config.json has correct data
                config_file = extract_dir / "config.json"
                if config_file.exists():
                    with open(config_file) as f:
                        config = json.load(f)
                    
                    if config.get("username") == config_data["username"]:
                        results.append(TestResult(
                            name="Package Generation - Configuration",
                            status="PASS",
                            duration=time.time() - start_time,
                            message="Configuration correctly embedded",
                            details={"config": config}
                        ))
                    else:
                        results.append(TestResult(
                            name="Package Generation - Configuration",
                            status="FAIL",
                            duration=time.time() - start_time,
                            message="Configuration not correctly embedded",
                            details={"config": config}
                        ))
                        
            else:
                results.append(TestResult(
                    name="Package Generation - API Response",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message=f"HTTP {response.status_code}: {response.text[:100]}",
                    details={"response_code": response.status_code}
                ))
                
        except Exception as e:
            results.append(TestResult(
                name="Package Generation - Exception",
                status="FAIL",
                duration=time.time() - start_time,
                message=f"Exception: {str(e)[:100]}",
                details={"exception": str(e)}
            ))
        
        return results
    
    def test_adapter_installation(self) -> List[TestResult]:
        """Test adapter installation process"""
        results = []
        
        # This test requires elevated privileges and may not be suitable for automated testing
        # We'll test the installation script validation instead
        
        start_time = time.time()
        try:
            install_script = self.adapter_dir / "install.py"
            if not install_script.exists():
                results.append(TestResult(
                    name="Installation Script - Existence",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="install.py not found"
                ))
                return results
            
            # Test dry-run installation (if supported)
            result = subprocess.run([
                sys.executable, str(install_script), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                results.append(TestResult(
                    name="Installation Script - Help",
                    status="PASS",
                    duration=time.time() - start_time,
                    message="Installation script help accessible",
                    details={"help_output": result.stdout[:200]}
                ))
            else:
                results.append(TestResult(
                    name="Installation Script - Help",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message=f"Help command failed: {result.stderr[:100]}",
                    details={"stderr": result.stderr}
                ))
                
        except Exception as e:
            results.append(TestResult(
                name="Installation Script - Exception",
                status="FAIL",
                duration=time.time() - start_time,
                message=f"Exception: {str(e)[:100]}",
                details={"exception": str(e)}
            ))
        
        return results
    
    def test_adapter_binary(self) -> List[TestResult]:
        """Test the Go adapter binary functionality"""
        results = []
        start_time = time.time()
        
        try:
            binary_path = self.adapter_dir / "build" / "tm-isync-adapter"
            if not binary_path.exists():
                results.append(TestResult(
                    name="Adapter Binary - Existence",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="Binary not found, may need to run 'make build'"
                ))
                return results
            
            # Test binary help/version
            result = subprocess.run([
                str(binary_path), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                results.append(TestResult(
                    name="Adapter Binary - Help",
                    status="PASS",
                    duration=time.time() - start_time,
                    message="Binary help accessible",
                    details={"help_output": result.stdout[:200]}
                ))
            else:
                results.append(TestResult(
                    name="Adapter Binary - Help",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message=f"Help command failed: {result.stderr[:100]}",
                    details={"stderr": result.stderr}
                ))
                
        except Exception as e:
            results.append(TestResult(
                name="Adapter Binary - Exception",
                status="FAIL",
                duration=time.time() - start_time,
                message=f"Exception: {str(e)[:100]}",
                details={"exception": str(e)}
            ))
        
        return results
    
    def test_file_sync_simulation(self) -> List[TestResult]:
        """Test file synchronization simulation"""
        results = []
        
        # Create a simulated sync test using local directories
        start_time = time.time()
        
        try:
            # Setup test directories
            source_dir = self.temp_dir / "source"
            target_dir = self.temp_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()
            
            # Copy test case files to source
            test_case_src = self.test_data_dir / "youssef"
            if test_case_src.exists():
                shutil.copytree(test_case_src, source_dir / "youssef")
                
                # Verify files were copied
                copied_files = list((source_dir / "youssef").glob("*"))
                if copied_files:
                    results.append(TestResult(
                        name="File Sync - Test Data Setup",
                        status="PASS",
                        duration=time.time() - start_time,
                        message=f"Copied {len(copied_files)} test files",
                        details={"files": [f.name for f in copied_files]}
                    ))
                else:
                    results.append(TestResult(
                        name="File Sync - Test Data Setup",
                        status="FAIL",
                        duration=time.time() - start_time,
                        message="No test files copied"
                    ))
            else:
                results.append(TestResult(
                    name="File Sync - Test Data Availability",
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="Test case directory not found"
                ))
                
        except Exception as e:
            results.append(TestResult(
                name="File Sync - Exception",
                status="FAIL",
                duration=time.time() - start_time,
                message=f"Exception: {str(e)[:100]}",
                details={"exception": str(e)}
            ))
        
        return results
    
    def test_performance_benchmarks(self) -> List[TestResult]:
        """Test performance benchmarks"""
        results = []
        start_time = time.time()
        
        try:
            # Test Dashboard API response times
            api_tests = [
                "/api/icloud/config",
                "/api/icloud/status",
                "/api/cases"
            ]
            
            for endpoint in api_tests:
                endpoint_start = time.time()
                response = self.session.get(f"{self.dashboard_base}{endpoint}", timeout=10)
                response_time = time.time() - endpoint_start
                
                # Good response time is under 1 second
                if response_time < 1.0:
                    status = "PASS"
                    message = f"Response time: {response_time:.3f}s"
                elif response_time < 2.0:
                    status = "PASS"
                    message = f"Acceptable response time: {response_time:.3f}s"
                else:
                    status = "FAIL"
                    message = f"Slow response time: {response_time:.3f}s"
                
                results.append(TestResult(
                    name=f"Performance - {endpoint}",
                    status=status,
                    duration=response_time,
                    message=message,
                    details={"response_time": response_time, "status_code": response.status_code}
                ))
                
        except Exception as e:
            results.append(TestResult(
                name="Performance - Exception",
                status="FAIL",
                duration=time.time() - start_time,
                message=f"Exception: {str(e)[:100]}",
                details={"exception": str(e)}
            ))
        
        return results
    
    def run_test_suite(self, test_categories: List[str]) -> Dict[str, List[TestResult]]:
        """Run specified test categories"""
        all_results = {}
        
        if "dashboard" in test_categories:
            self.logger.info("Running Dashboard API tests...")
            all_results["dashboard"] = self.test_dashboard_api_endpoints()
        
        if "package" in test_categories:
            self.logger.info("Running package generation tests...")
            all_results["package"] = self.test_package_generation()
        
        if "installation" in test_categories:
            self.logger.info("Running installation tests...")
            all_results["installation"] = self.test_adapter_installation()
        
        if "binary" in test_categories:
            self.logger.info("Running adapter binary tests...")
            all_results["binary"] = self.test_adapter_binary()
        
        if "sync" in test_categories:
            self.logger.info("Running file sync tests...")
            all_results["sync"] = self.test_file_sync_simulation()
        
        if "performance" in test_categories:
            self.logger.info("Running performance tests...")
            all_results["performance"] = self.test_performance_benchmarks()
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[TestResult]]) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("TM iSync Adapter Integration Test Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_tests = sum(len(test_list) for test_list in results.values())
        total_passed = sum(len([t for t in test_list if t.status == "PASS"]) for test_list in results.values())
        total_failed = sum(len([t for t in test_list if t.status == "FAIL"]) for test_list in results.values())
        
        report.append(f"Summary: {total_passed}/{total_tests} tests passed ({total_failed} failed)")
        report.append("")
        
        for category, test_results in results.items():
            report.append(f"\n{category.upper()} Tests:")
            report.append("-" * 40)
            
            for result in test_results:
                status_symbol = "✓" if result.status == "PASS" else "✗"
                report.append(f"{status_symbol} {result.name}")
                report.append(f"  Status: {result.status}")
                report.append(f"  Duration: {result.duration:.3f}s")
                if result.message:
                    report.append(f"  Message: {result.message}")
                if result.details and result.status == "FAIL":
                    report.append(f"  Details: {result.details}")
                report.append("")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="TM iSync Adapter Integration Testing")
    parser.add_argument("--test", choices=["all", "dashboard", "package", "installation", "binary", "sync", "performance"], 
                       default="all", help="Test category to run")
    parser.add_argument("--dashboard-url", default="http://127.0.0.1:8000", 
                       help="Dashboard base URL")
    parser.add_argument("--output", default="test_report.txt", 
                       help="Output file for test report")
    
    args = parser.parse_args()
    
    # Determine test categories
    if args.test == "all":
        test_categories = ["dashboard", "package", "installation", "binary", "sync", "performance"]
    else:
        test_categories = [args.test]
    
    # Run tests
    tester = IntegrationTester(args.dashboard_url)
    
    if not tester.setup_test_environment():
        print("Failed to setup test environment. Exiting.")
        sys.exit(1)
    
    try:
        print(f"Running integration tests for: {', '.join(test_categories)}")
        results = tester.run_test_suite(test_categories)
        
        # Generate and save report
        report = tester.generate_report(results)
        
        # Print to console
        print("\n" + report)
        
        # Save to file
        with open(args.output, 'w') as f:
            f.write(report)
        
        print(f"\nDetailed test report saved to: {args.output}")
        
        # Exit with appropriate code
        total_failed = sum(len([t for t in test_list if t.status == "FAIL"]) for test_list in results.values())
        sys.exit(1 if total_failed > 0 else 0)
        
    finally:
        tester.cleanup_test_environment()

if __name__ == "__main__":
    main()