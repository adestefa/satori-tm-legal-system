"""
Monkey CLI Commands
Command-line interface for the Monkey Document Builder Service
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime



# Add monkey directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.document_builder import MonkeyDocumentBuilder
from core.validators import DocumentValidator
from core.output_manager import OutputManager
from core.html_engine import HtmlEngine

class MonkeyCLI:
    """Command Line Interface for Monkey Document Builder Service"""
    
    def __init__(self):
        self.setup_logging()
        self.builder = None
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        
        # Reduce noise from third-party libraries
        logging.getLogger('jinja2').setLevel(logging.WARNING)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='satori-monkey',
            description='Monkey Document Builder Service - Transform Tiger\'s legal data into court-ready documents',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  satori-monkey build-complaint complaint.json                    # Generate complaint document
  satori-monkey build-complaint complaint.json --with-pdf        # Generate complaint with PDF
  satori-monkey review complaint.json                             # Generate HTML review file
  satori-monkey build-complaint complaint.json --all             # Generate full document package  
  satori-monkey validate complaint.json                          # Validate complaint data
  satori-monkey preview complaint.json                           # Preview complaint document
  satori-monkey templates                                        # List available templates

For more information, visit: https://github.com/satori-dev/beaver-builder
            """
        )
        
        parser.add_argument(
            '--version', 
            action='version',
            version='Monkey Document Builder v1.1.2 - Unified Case File Structure with Direct PDF Serving'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress non-essential output'
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Build-complaint command
        build_parser = subparsers.add_parser(
            'build-complaint',
            help='Build complaint document package from Tiger JSON'
        )
        build_parser.add_argument(
            'complaint_json',
            help='Path to complaint JSON file from Tiger'
        )
        build_parser.add_argument(
            '-o', '--output',
            help='Output directory (default: outputs/monkey/)'
        )
        build_parser.add_argument(
            '--all',
            action='store_true',
            help='Generate complete document package (complaint, summons, cover sheet)'
        )
        build_parser.add_argument(
            '--format',
            choices=['txt', 'docx', 'pdf', 'html'],
            default='html',
            help='Output format (default: html)'
        )
        build_parser.add_argument(
            '--template',
            help='Specify a custom template file to use'
        )
        build_parser.add_argument(
            '--with-pdf',
            action='store_true',
            help='Generate PDF version of complaint using browser service'
        )

        # Review command
        review_parser = subparsers.add_parser(
            'review',
            help='Generate HTML review file from Tiger JSON'
        )
        review_parser.add_argument(
            'complaint_json',
            help='Path to complaint JSON file from Tiger'
        )
        review_parser.add_argument(
            '-o', '--output',
            help='Output file path (default: review.html)'
        )
        
        # Generate-summons command
        summons_parser = subparsers.add_parser(
            'generate-summons',
            help='Generate summons documents for each defendant from Tiger JSON'
        )
        summons_parser.add_argument(
            'complaint_json',
            help='Path to complaint JSON file from Tiger'
        )
        summons_parser.add_argument(
            '-o', '--output',
            help='Output directory for summons files (default: outputs/summons/)'
        )
        
        # Validate command
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate complaint JSON data'
        )
        validate_parser.add_argument(
            'complaint_json',
            help='Path to complaint JSON file'
        )
        
        # Preview command
        preview_parser = subparsers.add_parser(
            'preview',
            help='Preview complaint document without generating files'
        )
        preview_parser.add_argument(
            'complaint_json',
            help='Path to complaint JSON file'
        )
        preview_parser.add_argument(
            '--lines',
            type=int,
            default=50,
            help='Number of lines to show in preview (default: 50)'
        )
        
        # Templates command
        templates_parser = subparsers.add_parser(
            'templates',
            help='List available document templates'
        )
        templates_parser.add_argument(
            '--pattern',
            help='Filter templates by pattern'
        )
        
        # Test command
        test_parser = subparsers.add_parser(
            'test',
            help='Test Monkey functionality'
        )
        test_parser.add_argument(
            '--quick',
            action='store_true',
            help='Run quick test only'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None):
        """Main entry point"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Update logging level based on verbosity
        if parsed_args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        elif parsed_args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        
        # Initialize document builder
        self.builder = MonkeyDocumentBuilder()
        
        # Route to appropriate command
        if parsed_args.command == 'build-complaint':
            return self.cmd_build_complaint(parsed_args)
        elif parsed_args.command == 'review':
            return self.cmd_review(parsed_args)
        elif parsed_args.command == 'generate-summons':
            return self.cmd_generate_summons(parsed_args)
        elif parsed_args.command == 'validate':
            return self.cmd_validate(parsed_args)
        elif parsed_args.command == 'preview':
            return self.cmd_preview(parsed_args)
        elif parsed_args.command == 'templates':
            return self.cmd_templates(parsed_args)
        elif parsed_args.command == 'test':
            return self.cmd_test(parsed_args)
        else:
            parser.print_help()
            return 1
    
    def cmd_review(self, args) -> int:
        """Review command handler"""
        complaint_json = args.complaint_json
        output_file = args.output or "review.html"
        
        print(f"🐒 Monkey Document Review")
        print(f"📄 Input: {complaint_json}")
        print(f"📁 Output: {output_file}")
        print()
        
        if not os.path.exists(complaint_json):
            print(f"❌ Error: Complaint JSON file not found: {complaint_json}")
            return 1
        
        try:
            with open(complaint_json, 'r') as f:
                data = json.load(f)
            
            html_engine = HtmlEngine()
            html_content = html_engine.render_template('case_review.html', data)
            
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            print(f"🎉 HTML review file generated successfully: {output_file}")
            return 0
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in review command")
            return 1

    def cmd_build_complaint(self, args) -> int:
        """Build complaint command handler"""
        complaint_json = args.complaint_json
        
        print(f"🐒 Monkey Document Builder")
        print(f"📄 Input: {complaint_json}")
        print(f"📁 Output Base: {args.output or 'outputs/monkey'}")
        print(f"📋 Format: {args.format}")
        
        if args.template:
            print(f"🎨 Template: {args.template}")
        
        print()
        
        if not os.path.exists(complaint_json):
            print(f"❌ Error: Complaint JSON file not found: {complaint_json}")
            return 1
        
        try:
            # Initialize OutputManager for this run
            output_manager = OutputManager(output_dir=args.output)
            print()

            # Determine document types
            document_types = ['complaint']
            if args.all:
                document_types = ['complaint', 'summons', 'cover_sheet']
            
            # Generate documents
            print("🔄 Building document package...")
            
            template_name = args.template
            if template_name and not template_name.startswith('html/'):
                template_name = f"html/{template_name}"

            result = self.builder.build_complaint_package(
                complaint_json,
                document_types,
                format=args.format,
                template_override=template_name,
                with_pdf=getattr(args, 'with_pdf', False)
            )
            
            if not result.success:
                print(f"❌ Document generation failed:")
                for error in result.errors:
                    print(f"   - {error}")
                return 1
            
            # Save documents using OutputManager
            print("💾 Saving documents...")
            files_saved = []
            
            # Save complaint
            if result.package.complaint:
                actual_html_path = output_manager.save_output('complaint', result.package.complaint, True)
                files_saved.append('complaint')
                print(f"   ✅ Complaint: complaint.{args.format}")
                
                # Generate PDF if requested
                if getattr(args, 'with_pdf', False) and actual_html_path:
                    # Generate case-specific PDF path in the case folder for standardized access
                    case_id = self._extract_case_id_from_json(complaint_json)
                    if case_id:
                        # Save PDF in the same directory as the HTML output file
                        html_output_dir = Path(actual_html_path).parent
                        pdf_filename = f"{case_id}_complaint.pdf"
                        pdf_file_path = html_output_dir / pdf_filename
                    else:
                        # Fallback: same directory as HTML
                        pdf_file_path = Path(actual_html_path).parent / "complaint.pdf"
                    
                    # Generate PDF using browser service
                    pdf_result = self._generate_pdf_from_html(actual_html_path, str(pdf_file_path))
                    
                    if pdf_result:
                        try:
                            pdf_relative_path = pdf_file_path.relative_to(Path.cwd())
                        except ValueError:
                            pdf_relative_path = pdf_file_path
                        print(f"   📄 Complaint PDF: {pdf_file_path.name}")
                        print(f"      📁 PDF Path: {pdf_relative_path}")
                        # Store PDF path in result for packet display
                        result.package.complaint_pdf = str(pdf_file_path)
                    else:
                        print(f"   ⚠️  PDF generation failed - HTML available for manual printing")
            
            # Save summons
            if result.package.summons:
                output_manager.save_output('summons', result.package.summons, True)
                files_saved.append('summons')
                print(f"   ✅ Summons: summons.{args.format}")
            
            # Save cover sheet
            if result.package.cover_sheet:
                output_manager.save_output('cover_sheet', result.package.cover_sheet, True)
                files_saved.append('cover_sheet')
                print(f"   ✅ Cover Sheet: cover_sheet.{args.format}")
            
            # Save metadata
            output_manager.save_metadata('package', result.package.metadata, True)
            files_saved.append('package')
            print(f"   ✅ Metadata: package.json")
            
            print()
            print(f"📊 Generation Summary")
            print(f"{'='*40}")
            print(f"✅ Documents Generated: {len(files_saved)}")
            print(f"⏱️ Generation Time: {result.generation_time:.2f} seconds")
            
            if result.warnings:
                print(f"⚠️ Warnings: {len(result.warnings)}")
                for warning in result.warnings[:3]:
                    print(f"   - {warning}")
            
            # Get source case info from metadata
            metadata = result.package.metadata
            if metadata.get('case_information'):
                case_info = metadata['case_information']
                if case_info.get('case_number'):
                    print(f"⚖️ Case Number: {case_info['case_number']}")
                if case_info.get('plaintiff_name'):
                    print(f"👤 Plaintiff: {case_info['plaintiff_name']}")
            
            # Document Package Tab - Complete file listing
            print(f"\n📁 Document Package")
            print(f"{'='*30}")
            
            # Helper function to get safe relative path
            def safe_relative_path(path):
                try:
                    return str(path.relative_to(Path.cwd()))
                except ValueError:
                    return str(path)
            
            # HTML documents
            today = datetime.now().strftime("%Y-%m-%d")
            output_base = output_manager.processed_path / today
            
            if result.package.complaint:
                html_path = output_base / f"complaint.{args.format}"
                if html_path.exists():
                    print(f"📄 Complaint HTML: {safe_relative_path(html_path)}")
            
            # PDF documents  
            if result.package.complaint_pdf:
                pdf_path = Path(result.package.complaint_pdf)
                if pdf_path.exists():
                    print(f"📄 Complaint PDF:  {safe_relative_path(pdf_path)}")
            
            # Additional documents
            if result.package.summons:
                summons_path = output_base / f"summons.{args.format}"
                if summons_path.exists():
                    print(f"📄 Summons:        {safe_relative_path(summons_path)}")
                    
            if result.package.cover_sheet:
                cover_path = output_base / f"cover_sheet.{args.format}"
                if cover_path.exists():
                    print(f"📄 Cover Sheet:    {safe_relative_path(cover_path)}")
            
            # Metadata
            metadata_path = output_manager.metadata_path / today / "package.json"
            if metadata_path.exists():
                print(f"📋 Metadata:       {safe_relative_path(metadata_path)}")
            
            print(f"\n🎉 Document package ready for legal review!")
            return 0
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in build-complaint command")
            return 1
    
    def cmd_generate_summons(self, args) -> int:
        """Generate summons command handler"""
        complaint_json = args.complaint_json
        output_dir = args.output or "outputs/summons/"
        
        print(f"🏛️ Monkey Summons Generator")
        print(f"📄 Input: {complaint_json}")
        print(f"📁 Output: {output_dir}")
        print()
        
        if not os.path.exists(complaint_json):
            print(f"❌ Error: Complaint JSON file not found: {complaint_json}")
            return 1
        
        try:
            # Load case data
            with open(complaint_json, 'r') as f:
                case_data = json.load(f)
            
            # Import summons generator
            from core.summons_generator import generate_summons_documents
            
            print("🔄 Generating summons documents...")
            
            # Generate summons for all defendants
            summons_files = generate_summons_documents(case_data, output_dir)
            
            print(f"✅ Successfully generated {len(summons_files)} summons documents:")
            for file_path in summons_files:
                print(f"   📄 {os.path.basename(file_path)}")
            print()
            print(f"🎉 Summons documents ready in: {output_dir}")
            return 0
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in generate-summons command")
            return 1
    
    def cmd_validate(self, args) -> int:
        """Validate command handler"""
        complaint_json = args.complaint_json
        
        print(f"🔍 Monkey Data Validation")
        print(f"📄 File: {complaint_json}")
        print()
        
        if not os.path.exists(complaint_json):
            print(f"❌ Error: File not found: {complaint_json}")
            return 1
        
        try:
            # Load and validate data
            validator = DocumentValidator()
            
            with open(complaint_json, 'r') as f:
                data = json.load(f)
            
            result = validator.validate_complaint_data(data)
            
            print(f"📊 Validation Results")
            print(f"{'='*30}")
            print(f"Status: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
            print(f"Score: {result.score:.1f}/100")
            print()
            
            # Show errors
            if result.errors:
                print(f"❌ Errors ({len(result.errors)}):")
                for error in result.errors:
                    print(f"   - {error}")
                print()
            
            # Show warnings
            if result.warnings:
                print(f"⚠️ Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"   - {warning}")
                print()
            
            # Show data summary
            print(f"📋 Data Summary")
            print(f"{'='*20}")
            case_info = data.get('case_information', {})
            if case_info.get('case_number'):
                print(f"Case Number: {case_info['case_number']}")
            if case_info.get('court_district'):
                print(f"Court: {case_info['court_district']}")
            
            plaintiff = data.get('plaintiff', {})
            if plaintiff.get('name'):
                print(f"Plaintiff: {plaintiff['name']}")
            
            defendants = data.get('defendants', [])
            print(f"Defendants: {len(defendants)}")
            
            return 0 if result.is_valid else 1
            
        except Exception as e:
            print(f"💥 Validation Error: {e}")
            logging.exception("Error in validate command")
            return 1
    
    def cmd_preview(self, args) -> int:
        """Preview command handler"""
        complaint_json = args.complaint_json
        
        print(f"👁️ Monkey Document Preview")
        print(f"📄 File: {complaint_json}")
        print(f"📏 Lines: {args.lines}")
        print()
        
        if not os.path.exists(complaint_json):
            print(f"❌ Error: File not found: {complaint_json}")
            return 1
        
        try:
            preview = self.builder.preview_complaint(complaint_json, args.lines)
            
            print("📄 Document Preview")
            print("=" * 60)
            print(preview)
            print("=" * 60)
            
            return 0
            
        except Exception as e:
            print(f"💥 Preview Error: {e}")
            logging.exception("Error in preview command")
            return 1
    
    def cmd_templates(self, args) -> int:
        """Templates command handler"""
        print(f"📋 Available Templates")
        print(f"{'='*30}")
        
        try:
            html_engine = HtmlEngine()
            templates = html_engine.list_templates(args.pattern)
            
            if not templates:
                print("No templates found.")
                return 1
            
            for template in templates:
                info = html_engine.get_template_info(template)
                status = "✅" if info['valid'] else "❌"
                size_kb = info['size'] / 1024 if info['size'] else 0
                
                print(f"{status} {template} ({size_kb:.1f} KB)")
                
                if not info['valid'] and info['error']:
                    print(f"    Error: {info['error']}")
            
            print(f"\nTotal templates: {len(templates)}")
            return 0
            
        except Exception as e:
            print(f"💥 Templates Error: {e}")
            logging.exception("Error in templates command")
            return 1
    
    def cmd_test(self, args) -> int:
        """Test command handler"""
        print(f"🧪 Monkey Service Test")
        print(f"{'='*25}")
        
        try:
            # Test 1: Template engine initialization
            print(f"1. Template Engine... ", end="")
            html_engine = HtmlEngine()
            templates = html_engine.list_templates()
            print("✅ OK" if templates else "⚠️ No templates")
            
            # Test 2: Validator
            print(f"2. Document Validator... ", end="")
            validator = DocumentValidator()
            test_data = {'case_information': {}, 'plaintiff': {}, 'defendants': []}
            result = validator.validate_complaint_data(test_data)
            print("✅ OK")
            
            # Test 3: Template validation
            print(f"3. Template Validation... ", end="")
            fcra_template = html_engine.validate_template('fcra/complaint.html')
            print("✅ OK" if fcra_template else "❌ FAILED")
            
            if not args.quick:
                # Test 4: Document generation (if test data exists)
                print(f"4. Document Generation... ", end="")
                test_json_path = Path("test-data/test-json/complete-cases")
                if test_json_path.exists():
                    test_files = list(test_json_path.glob("*.json"))
                    if test_files:
                        result = self.builder.build_complaint_package(str(test_files[0]))
                        print("✅ OK" if result.success else "❌ FAILED")
                    else:
                        print("⏭️ No test files")
                else:
                    print("⏭️ No test data directory")
            
            print(f"\n🎉 Monkey service test completed!")
            return 0
            
        except Exception as e:
            print(f"❌ FAILED")
            print(f"💥 Test Error: {e}")
            logging.exception("Error in test command")
            return 1
    
    def _extract_case_id_from_json(self, json_path: str) -> Optional[str]:
        """Extract case ID from the JSON file path or content"""
        try:
            # Try to extract from filename first
            filename = Path(json_path).stem
            if 'FCRA_' in filename:
                parts = filename.split('_')
                if len(parts) >= 3:
                    return parts[2].lower()  # e.g., YOUSSEF from hydrated_FCRA_YOUSSEF_EMAN_20250714
            
            # Fallback: try to read from JSON content
            with open(json_path, 'r') as f:
                data = json.load(f)
                tiger_metadata = data.get('tiger_metadata', {})
                if tiger_metadata.get('case_id'):
                    return tiger_metadata['case_id'].lower()
                
                # Try to extract from plaintiff name
                plaintiff = data.get('parties', {}).get('plaintiff', {})
                if plaintiff.get('name'):
                    return plaintiff['name'].split()[0].lower()
                    
        except Exception as e:
            self.logger.warning(f"Could not extract case ID from {json_path}: {e}")
        
        return None
    
    def _generate_pdf_from_html(self, html_file_path: str, pdf_file_path: str) -> bool:
        """Generate PDF from HTML using browser service"""
        try:
            browser_service_path = Path(__file__).parent.parent / "browser" / "print.py"
            if not browser_service_path.exists():
                self.logger.warning("Browser PDF service not available")
                return False
            
            result = subprocess.run([
                sys.executable, str(browser_service_path), 'single', html_file_path, pdf_file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and Path(pdf_file_path).exists():
                self.logger.info(f"PDF generated successfully: {pdf_file_path}")
                return True
            else:
                self.logger.error(f"PDF generation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("PDF generation timed out")
            return False
        except Exception as e:
            self.logger.error(f"PDF generation error: {str(e)}")
            return False

def main():
    """Main CLI entry point"""
    cli = MonkeyCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())
