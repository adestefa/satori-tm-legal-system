#!/usr/bin/env python3

"""
TM Browser PDF Generator - Python Integration Wrapper

This module provides a Python interface to the Node.js headless browser PDF generation service.
Designed for seamless integration with the existing Tiger-Monkey system while leveraging
the superior rendering capabilities of Chromium.

Author: Dr. Spock, Systems Architect
System: Tiger-Monkey Legal Document Processing Platform
"""

import subprocess
import os
import json
import time
import sys
from pathlib import Path
from typing import Optional, Dict, List, Union
import logging

class BrowserPDFGenerator:
    """
    Python wrapper for the Node.js headless browser PDF generation service.
    
    This class provides a clean Python API while delegating the actual PDF generation
    to the optimized Node.js/Puppeteer implementation.
    """
    
    def __init__(self, service_path: Optional[str] = None):
        """
        Initialize the PDF generator wrapper.
        
        Args:
            service_path: Path to the Node.js service directory. 
                         Defaults to current directory or TM/browser/
        """
        self.service_path = self._find_service_path(service_path)
        self.node_script = os.path.join(self.service_path, "pdf-generator.js")
        self.logger = self._setup_logging()
        
        # Validate service availability
        self._validate_service()
    
    def _find_service_path(self, provided_path: Optional[str]) -> str:
        """Find the Node.js service directory."""
        if provided_path and os.path.exists(provided_path):
            return provided_path
            
        # Check current directory
        if os.path.exists("pdf-generator.js"):
            return "."
            
        # Check TM/browser/ relative path
        browser_path = os.path.join("..", "browser")
        if os.path.exists(os.path.join(browser_path, "pdf-generator.js")):
            return browser_path
            
        # Check if we're in TM root and browser/ exists
        if os.path.exists("browser/pdf-generator.js"):
            return "browser"
            
        raise FileNotFoundError(
            "PDF generation service not found. "
            "Ensure you're running from TM/browser/ or TM/ directory."
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the PDF generator."""
        logger = logging.getLogger("tm_pdf_generator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _validate_service(self):
        """Validate that the Node.js service is available."""
        if not os.path.exists(self.node_script):
            raise FileNotFoundError(f"Node.js service not found: {self.node_script}")
            
        # Check if Node.js is available
        try:
            subprocess.run(["node", "--version"], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError("Node.js not found. Please install Node.js to use PDF generation.")
    
    def generate_pdf(self, 
                    html_file: str, 
                    output_file: str,
                    timeout: int = 30) -> Dict[str, Union[bool, str, int]]:
        """
        Generate a PDF from an HTML file.
        
        Args:
            html_file: Path to the HTML file to convert
            output_file: Path where the PDF should be saved
            timeout: Maximum time to wait for generation (seconds)
            
        Returns:
            Dictionary with generation results:
            {
                'success': bool,
                'output_path': str,
                'processing_time_ms': int,
                'file_size_bytes': int,
                'error_message': str (if failed)
            }
        """
        start_time = time.time()
        
        # Validate input file
        if not os.path.exists(html_file):
            return {
                'success': False,
                'error_message': f"HTML file not found: {html_file}"
            }
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:  # Only create directory if there is one
            os.makedirs(output_dir, exist_ok=True)
        
        # Also ensure the main browser output directory exists
        browser_output_dir = os.path.join(os.path.dirname(self.service_path), 'outputs', 'browser')
        os.makedirs(browser_output_dir, exist_ok=True)
        
        self.logger.info(f"Generating PDF: {html_file} -> {output_file}")
        
        # Convert relative paths to absolute paths
        abs_html_file = os.path.abspath(html_file)
        abs_output_file = os.path.abspath(output_file)
        
        try:
            # Execute Node.js PDF generator
            result = subprocess.run([
                "node", 
                "pdf-generator.js",  # Use just the filename since we set cwd
                abs_html_file,
                abs_output_file
            ], 
            cwd=self.service_path,
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=True)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Verify PDF was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                
                self.logger.info(f"PDF generated successfully: {file_size} bytes in {processing_time}ms")
                
                return {
                    'success': True,
                    'output_path': output_file,
                    'processing_time_ms': processing_time,
                    'file_size_bytes': file_size,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'success': False,
                    'error_message': "PDF file was not created",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_message': f"PDF generation timed out after {timeout} seconds"
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error_message': f"PDF generation failed: {e}",
                'stdout': e.stdout,
                'stderr': e.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error_message': f"Unexpected error: {str(e)}"
            }
    
    def batch_generate(self, 
                      input_dir: str, 
                      output_dir: str,
                      timeout: int = 120) -> Dict[str, Union[bool, int, List]]:
        """
        Generate PDFs for all HTML files in a directory.
        
        Args:
            input_dir: Directory containing HTML files
            output_dir: Directory to save PDF files
            timeout: Maximum time to wait for batch processing (seconds)
            
        Returns:
            Dictionary with batch results:
            {
                'success': bool,
                'total_files': int,
                'successful_files': int,
                'failed_files': int,
                'processing_time_ms': int,
                'results': List[Dict]
            }
        """
        start_time = time.time()
        
        if not os.path.exists(input_dir):
            return {
                'success': False,
                'error_message': f"Input directory not found: {input_dir}"
            }
        
        self.logger.info(f"Batch generating PDFs: {input_dir} -> {output_dir}")
        
        try:
            # Execute Node.js batch processor
            result = subprocess.run([
                "node",
                self.node_script,
                "--batch",
                input_dir,
                output_dir
            ],
            cwd=self.service_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Count results
            pdf_files = list(Path(output_dir).glob("*.pdf"))
            html_files = list(Path(input_dir).glob("*.html"))
            
            return {
                'success': True,
                'total_files': len(html_files),
                'successful_files': len(pdf_files),
                'failed_files': len(html_files) - len(pdf_files),
                'processing_time_ms': processing_time,
                'output_directory': output_dir,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_message': f"Batch processing timed out after {timeout} seconds"
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error_message': f"Batch processing failed: {e}",
                'stdout': e.stdout,
                'stderr': e.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error_message': f"Unexpected error: {str(e)}"
            }
    
    def test_service(self) -> Dict[str, Union[bool, str]]:
        """
        Test the PDF generation service with sample files.
        
        Returns:
            Dictionary with test results
        """
        self.logger.info("Testing PDF generation service...")
        
        try:
            result = subprocess.run([
                "node",
                self.node_script,
                "--test"
            ],
            cwd=self.service_path,
            capture_output=True,
            text=True,
            timeout=60,
            check=True)
            
            return {
                'success': True,
                'message': "Service test completed successfully",
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': f"Service test failed: {str(e)}"
            }


def main():
    """CLI interface for the Python wrapper."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TM Browser PDF Generator - Python Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python print.py single input.html output.pdf
  python print.py batch input_dir/ output_dir/
  python print.py test
  
Integration with TM System:
  from browser.print import BrowserPDFGenerator
  
  generator = BrowserPDFGenerator()
  result = generator.generate_pdf("complaint.html", "complaint.pdf")
  if result['success']:
      print(f"PDF generated: {result['output_path']}")
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single file command
    single_parser = subparsers.add_parser('single', help='Generate PDF from single HTML file')
    single_parser.add_argument('html_file', help='Input HTML file')
    single_parser.add_argument('pdf_file', help='Output PDF file')
    single_parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Generate PDFs from directory of HTML files')
    batch_parser.add_argument('input_dir', help='Input directory with HTML files')
    batch_parser.add_argument('output_dir', help='Output directory for PDF files')
    batch_parser.add_argument('--timeout', type=int, default=120, help='Timeout in seconds')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test the PDF generation service')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        generator = BrowserPDFGenerator()
        
        if args.command == 'single':
            # Use centralized output directory if no specific output file provided
            if not hasattr(args, 'pdf_file') or args.pdf_file == args.html_file.replace('.html', '.pdf'):
                browser_output_dir = os.path.join('..', 'outputs', 'browser')
                os.makedirs(browser_output_dir, exist_ok=True)
                default_output = os.path.join(browser_output_dir, os.path.basename(args.html_file).replace('.html', '.pdf'))
                pdf_file = getattr(args, 'pdf_file', default_output)
            else:
                pdf_file = args.pdf_file
                
            result = generator.generate_pdf(args.html_file, pdf_file, args.timeout)
            
            if result['success']:
                print(f"✅ PDF generated successfully: {result['output_path']}")
                print(f"   Processing time: {result['processing_time_ms']}ms")
                print(f"   File size: {result['file_size_bytes']} bytes")
            else:
                print(f"❌ PDF generation failed: {result['error_message']}")
                sys.exit(1)
                
        elif args.command == 'batch':
            result = generator.batch_generate(args.input_dir, args.output_dir, args.timeout)
            
            if result['success']:
                print(f"✅ Batch processing completed successfully")
                print(f"   Total files: {result['total_files']}")
                print(f"   Successful: {result['successful_files']}")
                print(f"   Failed: {result['failed_files']}")
                print(f"   Processing time: {result['processing_time_ms']}ms")
            else:
                print(f"❌ Batch processing failed: {result['error_message']}")
                sys.exit(1)
                
        elif args.command == 'test':
            result = generator.test_service()
            
            if result['success']:
                print("✅ Service test completed successfully")
                print(result['stdout'])
            else:
                print(f"❌ Service test failed: {result['error_message']}")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()