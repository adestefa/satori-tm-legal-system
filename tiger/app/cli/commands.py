"""
Satori Tiger CLI Commands
Professional command-line interface for legal document processing
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
from typing import Optional



import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.processors.document_processor import DocumentProcessor
from core.processors.case_consolidator import CaseConsolidator
from core.event_broadcaster import ProcessingEventBroadcaster
from config.settings import config
from output.handlers import OutputManager

class SatoriCLI:
    """Command Line Interface for Satori Tiger Document Processing Service"""
    
    def __init__(self):
        self.config = config
        self.setup_logging()
        self.processor = None
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.logging.level.upper(), logging.INFO)
        
        # Create logs directory
        log_dir = Path(self.config.logging.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=self.config.logging.log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_dir / "satori_tiger.log")
            ]
        )
        
        # Reduce noise from third-party libraries
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('torch').setLevel(logging.WARNING)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='satori-tiger',
            description='Satori Tiger Document Processing Service - Professional legal document extraction and analysis',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  satori-tiger process document.pdf                            # Process single document
  satori-tiger process ./documents/ --output-dir ./output/     # Process directory
  satori-tiger batch ./case_files/ --output-dir ./processed/  # Batch process with reports
  satori-tiger case-extract ./case_folder/ -o ./tests/output/  # Test case extraction
  satori-tiger hydrated-json ./case_folder/ -o ./output/      # Generate NY FCRA hydrated JSON
  satori-tiger info                                            # Show service information
  satori-tiger validate document.pdf                          # Quality validation only

For more information, visit: https://github.com/satori-dev/tiger-engine
            """
        )
        
        parser.add_argument(
            '--version', 
            action='version',
            version=f'Satori Tiger v{self.config.version}'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Path to custom configuration file'
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
        
        # Process command
        process_parser = subparsers.add_parser(
            'process',
            help='Process documents (single file or directory)'
        )
        process_parser.add_argument(
            'input',
            help='Input file or directory path'
        )
        process_parser.add_argument(
            '-o', '--output', '--output-dir',
            dest='output_dir',
            help='Output directory (default: data/output)'
        )
        process_parser.add_argument(
            '--format',
            choices=['txt', 'json', 'md', 'html'],
            nargs='+',
            default=['txt', 'json', 'md'],
            help='Output formats (default: txt json md)'
        )
        
        # Batch command
        batch_parser = subparsers.add_parser(
            'batch',
            help='Batch process directory with comprehensive reporting'
        )
        batch_parser.add_argument(
            'input_dir',
            help='Input directory path'
        )
        batch_parser.add_argument(
            '-o', '--output', '--output-dir',
            dest='output_dir',
            help='Output directory (default: data/output)'
        )
        batch_parser.add_argument(
            '--report-name',
            help='Custom name for batch report'
        )
        
        # Validate command
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate document quality without full processing'
        )
        validate_parser.add_argument(
            'input',
            help='Input file path'
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Display service information and status'
        )
        info_parser.add_argument(
            '--engines',
            action='store_true',
            help='Show detailed engine information'
        )
        
        # Test command
        test_parser = subparsers.add_parser(
            'test',
            help='Test service functionality'
        )
        test_parser.add_argument(
            '--quick',
            action='store_true',
            help='Run quick test only'
        )
        
        # Case-extract command
        case_parser = subparsers.add_parser(
            'case-extract',
            help='Extract legal case information and generate complaint.json'
        )
        case_parser.add_argument(
            'case_folder',
            help='Path to case folder containing legal documents'
        )
        case_parser.add_argument(
            '-o', '--output', '--output-dir',
            dest='output_dir',
            help='Output directory (default: data/output)'
        )
        case_parser.add_argument(
            '--complaint-json',
            action='store_true',
            help='Generate complaint.json from extracted case data'
        )
        
        # Hydrated-JSON command
        hydrated_parser = subparsers.add_parser(
            'hydrated-json',
            help='Generate NY FCRA-compliant hydrated JSON from case documents'
        )
        hydrated_parser.add_argument(
            'case_folder',
            help='Path to case folder containing legal documents'
        )
        hydrated_parser.add_argument(
            '-o', '--output', '--output-dir',
            dest='output_dir',
            help='Output directory (default: outputs/tiger/)'
        )
        hydrated_parser.add_argument(
            '--case-name',
            help='Custom case name for the hydrated JSON file'
        )
        hydrated_parser.add_argument(
            '--exclude',
            nargs='+',
            help='List of files to exclude from processing'
        )
        hydrated_parser.add_argument(
            '--dashboard-url',
            help='Dashboard URL for real-time event broadcasting (e.g., http://127.0.0.1:8000)'
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
        
        # Load custom config if provided
        if parsed_args.config and os.path.exists(parsed_args.config):
            self.config.load_from_file(parsed_args.config)
        
        # Initialize processor
        self.processor = DocumentProcessor(self.config)
        
        # Route to appropriate command
        if parsed_args.command == 'process':
            return self.cmd_process(parsed_args)
        elif parsed_args.command == 'batch':
            return self.cmd_batch(parsed_args)
        elif parsed_args.command == 'case-extract':
            return self.cmd_case_extract(parsed_args)
        elif parsed_args.command == 'hydrated-json':
            return self.cmd_hydrated_json(parsed_args)
        elif parsed_args.command == 'validate':
            return self.cmd_validate(parsed_args)
        elif parsed_args.command == 'info':
            return self.cmd_info(parsed_args)
        elif parsed_args.command == 'test':
            return self.cmd_test(parsed_args)
        else:
            parser.print_help()
            return 1
    
    def cmd_process(self, args) -> int:
        """Process command handler"""
        input_path = args.input
        output_dir = args.output_dir or str(self.config.get_data_dirs()['output'])
        
        print(f"🚀 Satori Tiger Document Processing")
        print(f"📁 Input: {input_path}")
        print(f"📤 Output: {output_dir}")
        print(f"📋 Formats: {', '.join(args.format)}")
        print()
        
        # Update output formats in config
        self.config.output.output_formats = args.format
        
        try:
            if os.path.isfile(input_path):
                # Process single file
                result = self.processor.process_document(input_path, output_dir)
                
                if result.success:
                    print(f"✅ Successfully processed: {result.file_name}")
                    print(f"📊 Quality Score: {result.quality_metrics.get('quality_score', 0)}/100")
                    print(f"🎯 Readiness Score: {result.quality_metrics.get('readiness_score', 0)}/100")
                    print(f"📝 Text Length: {result.quality_metrics.get('text_length', 0):,} characters")
                    print(f"⏱️ Processing Time: {result.processing_time:.2f} seconds")
                    
                    warnings = result.quality_metrics.get('warnings', [])
                    if warnings:
                        print(f"⚠️ Warnings: {len(warnings)}")
                        for warning in warnings[:3]:
                            print(f"   - {warning}")
                    
                    return 0
                else:
                    print(f"❌ Failed to process: {result.file_name}")
                    print(f"💥 Error: {result.error}")
                    return 1
                    
            elif os.path.isdir(input_path):
                # Process directory
                batch_result = self.processor.process_directory(input_path, output_dir)
                
                print(f"📊 Batch Processing Complete")
                print(f"📁 Total Files: {batch_result.summary['total_files']}")
                print(f"✅ Successful: {batch_result.summary['successful']}")
                print(f"❌ Failed: {batch_result.summary['failed']}")
                print(f"⚠️ Warnings: {batch_result.summary['warnings']}")
                print(f"📈 Success Rate: {batch_result.summary.get('success_rate', 0):.1f}%")
                print(f"⏱️ Total Time: {batch_result.summary['total_processing_time']:.2f} seconds")
                
                return 0 if batch_result.summary['failed'] == 0 else 1
            else:
                print(f"❌ Error: Input path does not exist: {input_path}")
                return 1
                
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in process command")
            return 1
    
    def cmd_batch(self, args) -> int:
        """Batch command handler"""
        input_dir = args.input_dir
        output_dir = args.output_dir or str(self.config.get_data_dirs()['output'])
        
        print(f"🔄 Satori Tiger Batch Processing")
        print(f"📁 Input Directory: {input_dir}")
        print(f"📤 Output Directory: {output_dir}")
        print()
        
        try:
            # Process directory
            batch_result = self.processor.process_directory(input_dir, output_dir)
            
            # Save comprehensive batch report
            output_manager = OutputManager(self.config)
            if output_dir:
                output_manager.base_output_dir = Path(output_dir)
            report_file = output_manager.save_batch_report(batch_result, args.report_name)
            
            # Display summary
            print(f"📊 Batch Processing Summary")
            print(f"{'='*50}")
            print(f"📁 Total Files: {batch_result.summary['total_files']}")
            print(f"✅ Successful: {batch_result.summary['successful']}")
            print(f"❌ Failed: {batch_result.summary['failed']}")
            print(f"⚠️ With Warnings: {batch_result.summary['warnings']}")
            print(f"📈 Success Rate: {batch_result.summary.get('success_rate', 0):.1f}%")
            print(f"⏱️ Total Processing Time: {batch_result.summary['total_processing_time']:.2f} seconds")
            print()
            
            if report_file:
                print(f"📋 Detailed Report: {report_file}")
            
            # Show quality summary for successful documents
            successful_results = [r for r in batch_result.results if r.success and r.quality_metrics]
            if successful_results:
                quality_scores = [r.quality_metrics.get('quality_score', 0) for r in successful_results]
                avg_quality = sum(quality_scores) / len(quality_scores)
                high_quality = len([s for s in quality_scores if s >= 80])
                
                print(f"🎯 Quality Summary:")
                print(f"   Average Score: {avg_quality:.1f}/100")
                print(f"   High Quality (≥80): {high_quality}/{len(successful_results)}")
            
            return 0 if batch_result.summary['failed'] == 0 else 1
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in batch command")
            return 1
    
    def cmd_validate(self, args) -> int:
        """Validate command handler"""
        input_file = args.input
        
        print(f"🔍 Satori Tiger Quality Validation")
        print(f"📄 File: {input_file}")
        print()
        
        try:
            # Quick extraction for validation
            result = self.processor.process_document(input_file)
            
            if not result.success:
                print(f"❌ Cannot validate - extraction failed: {result.error}")
                return 1
            
            quality = result.quality_metrics
            
            print(f"📊 Quality Assessment")
            print(f"{'='*40}")
            print(f"Quality Score: {quality.get('quality_score', 0)}/100")
            print(f"Text Length: {quality.get('text_length', 0):,} characters")
            print(f"Compression Ratio: {quality.get('compression_ratio', 0):.4f}")
            print(f"Passes Threshold: {'✅ Yes' if quality.get('passes_threshold', False) else '❌ No'}")
            print()
            
            # Legal indicators
            legal = quality.get('legal_indicators', {})
            print(f"⚖️ Legal Content Analysis")
            print(f"{'='*40}")
            print(f"Court Document: {'✅' if legal.get('court_document', False) else '❌'}")
            print(f"Case Number: {'✅' if legal.get('case_number', False) else '❌'}")
            print(f"Legal Entities: {legal.get('legal_entities', {}).get('count', 0)}")
            print(f"Addresses: {legal.get('addresses', {}).get('count', 0)}")
            print(f"Phone Numbers: {legal.get('phone_numbers', {}).get('count', 0)}")
            print()
            
            # Warnings
            warnings = quality.get('warnings', [])
            if warnings:
                print(f"⚠️ Quality Warnings ({len(warnings)})")
                print(f"{'='*40}")
                for warning in warnings:
                    level = "🚨" if "CRITICAL" in warning else "⚠️" if "WARNING" in warning else "ℹ️"
                    print(f"{level} {warning}")
                print()
            
            return 0
            
        except Exception as e:
            print(f"💥 Validation Error: {e}")
            logging.exception("Error in validate command")
            return 1
    
    def cmd_info(self, args) -> int:
        """Info command handler"""
        try:
            service_info = self.processor.get_service_info()
            
            print(f"🐅 {service_info['service_name']} v{service_info['version']}")
            print(f"{'='*60}")
            print()
            
            # Configuration info
            print(f"⚙️ Configuration")
            print(f"{'='*20}")
            print(f"Supported Formats: {', '.join(service_info['supported_formats'])}")
            print(f"Quality Threshold: {service_info['quality_thresholds']['min_quality_score']}")
            print(f"Min Text Length: {service_info['quality_thresholds']['min_text_length']}")
            print()
            
            # Data directories
            print(f"📁 Data Directories")
            print(f"{'='*20}")
            for name, path in service_info['data_directories'].items():
                exists = "✅" if os.path.exists(path) else "❌"
                print(f"{name.title()}: {exists} {path}")
            print()
            
            # Engine information
            if args.engines:
                print(f"🔧 Processing Engines")
                print(f"{'='*25}")
                for engine_name, engine_info in service_info['engines'].items():
                    print(f"\n{engine_name.upper()} Engine:")
                    print(f"  Name: {engine_info['name']}")
                    print(f"  Formats: {', '.join(engine_info['supported_formats'])}")
                    if 'description' in engine_info:
                        print(f"  Description: {engine_info['description']}")
                    if 'features' in engine_info:
                        print(f"  Features:")
                        for feature in engine_info['features'][:3]:
                            print(f"    - {feature}")
            
            return 0
            
        except Exception as e:
            print(f"💥 Error getting service info: {e}")
            logging.exception("Error in info command")
            return 1
    
    def cmd_test(self, args) -> int:
        """Test command handler"""
        print(f"🧪 Satori Tiger Service Test")
        print(f"{'='*30}")
        
        try:
            # Test 1: Service initialization
            print(f"1. Service Initialization... ", end="")
            service_info = self.processor.get_service_info()
            print("✅ OK")
            
            # Test 2: Engine availability
            print(f"2. Engine Availability... ", end="")
            engines_ok = True
            for engine_name, engine_info in service_info['engines'].items():
                if engine_name == 'pdf' and not engine_info.get('docling_available'):
                    engines_ok = False
                elif engine_name == 'docx' and not engine_info.get('python_docx_available'):
                    engines_ok = False
            
            if engines_ok:
                print("✅ OK")
            else:
                print("⚠️ Some engines unavailable")
            
            # Test 3: Directory structure
            print(f"3. Directory Structure... ", end="")
            dirs = self.config.get_data_dirs()
            dirs_ok = all(os.path.exists(path) for path in dirs.values())
            if dirs_ok:
                print("✅ OK")
            else:
                print("⚠️ Some directories missing")
                self.config.ensure_directories()
                print("   📁 Directories created")
            
            if not args.quick:
                # Test 4: Sample processing (if test files exist)
                print(f"4. Sample Processing... ", end="")
                test_files = list(Path("test-data").rglob("*.pdf"))[:1] if Path("test-data").exists() else []
                
                if test_files:
                    result = self.processor.process_document(str(test_files[0]))
                    if result.success:
                        print("✅ OK")
                    else:
                        print(f"❌ Failed: {result.error}")
                else:
                    print("⏭️ No test files available")
            
            print(f"\n🎉 Service test completed successfully!")
            return 0
            
        except Exception as e:
            print(f"❌ FAILED")
            print(f"💥 Test Error: {e}")
            logging.exception("Error in test command")
            return 1
    
    def cmd_case_extract(self, args) -> int:
        """Case extraction command handler"""
        case_folder = args.case_folder
        output_dir = args.output_dir or str(self.config.get_data_dirs()['output'])
        
        print(f"⚖️ Satori Tiger Legal Case Extraction")
        print(f"📁 Case Folder: {case_folder}")
        print(f"📤 Output: {output_dir}")
        print(f"📋 Generate Complaint JSON: {'Yes' if args.complaint_json else 'No'}")
        print()
        
        if not os.path.exists(case_folder):
            print(f"❌ Error: Case folder does not exist: {case_folder}")
            return 1
        
        if not os.path.isdir(case_folder):
            print(f"❌ Error: Path is not a directory: {case_folder}")
            return 1
        
        try:
            # Find all documents in the case folder
            case_path = Path(case_folder)
            document_files = []
            
            for pattern in ['*.pdf', '*.docx', '*.doc', '*.txt']:
                document_files.extend(case_path.glob(pattern))
            
            if not document_files:
                print(f"❌ Error: No legal documents found in case folder")
                print(f"   Supported formats: PDF, DOCX, DOC, TXT")
                return 1
            
            print(f"📄 Found {len(document_files)} documents:")
            for doc in document_files:
                print(f"   - {doc.name}")
            print()
            
            # Initialize case-based output manager
            from output.handlers import OutputManager
            from core.utils.case_name_generator import CaseNameGenerator
            
            output_manager = OutputManager(use_case_folders=True)
            if output_dir:
                output_manager.base_output_dir = Path(output_dir)
            case_name_generator = CaseNameGenerator()
            
            # Process each document with Tiger
            print("🔄 Processing documents...")
            extraction_results = []
            
            for doc_path in document_files:
                print(f"   Processing: {doc_path.name}...", end=" ")
                
                # Process document without saving to old structure
                result = self.processor.process_document(str(doc_path))
                extraction_results.append(result)
                
                if result.success:
                    quality_score = result.quality_metrics.get('quality_score', 0)
                    print(f"✅ {quality_score}/100")
                else:
                    print(f"❌ Failed: {result.error}")
            
            print()
            
            # Consolidate case information
            print("🔗 Consolidating case information...")
            consolidator = CaseConsolidator()
            consolidated_case = consolidator.consolidate_case_folder(case_folder, extraction_results)
            
            # Generate case name from consolidated case
            case_name = case_name_generator.generate_case_folder_name(consolidated_case=consolidated_case)
            print(f"📁 Case Name: {case_name}")
            
            # Save all documents using case-based structure
            print("💾 Saving case documents...")
            saved_files_list = []
            
            for result in extraction_results:
                if result.success:
                    saved_files = output_manager.save_case_processing_result(
                        result, 
                        case_name=case_name, 
                        consolidated_case=consolidated_case
                    )
                    saved_files_list.append(saved_files)
            
            # Save consolidated case information
            case_info_file = output_manager.save_case_info_json(case_name, consolidated_case)
            
            # Generate case summary
            case_summary_file = output_manager.generate_case_summary(
                case_name, 
                extraction_results, 
                consolidated_case
            )
            
            # Display consolidation results
            print(f"📊 Case Consolidation Results")
            print(f"{'='*35}")
            print(f"📋 Case ID: {consolidated_case.case_id}")
            print(f"📁 Case Folder: {case_name}")
            print(f"📊 Confidence: {consolidated_case.extraction_confidence:.1f}%")
            print(f"📄 Source Documents: {len(consolidated_case.source_documents)}")
            
            if consolidated_case.case_information.case_number:
                print(f"⚖️ Case Number: {consolidated_case.case_information.case_number}")
            if consolidated_case.case_information.court_district:
                print(f"🏛️ Court: {consolidated_case.case_information.court_district}")
            
            if consolidated_case.plaintiff:
                print(f"👤 Plaintiff: {consolidated_case.plaintiff.get('name', 'Unknown')}")
            
            if consolidated_case.defendants:
                print(f"🏢 Defendants: {len(consolidated_case.defendants)}")
                for defendant in consolidated_case.defendants[:3]:
                    print(f"   - {defendant.get('short_name', defendant.get('name', 'Unknown'))}")
            
            if consolidated_case.warnings:
                print(f"⚠️ Warnings: {len(consolidated_case.warnings)}")
                for warning in consolidated_case.warnings[:3]:
                    print(f"   - {warning}")
            
            print()
            
            # Generate complaint.json if requested
            if args.complaint_json:
                print("📝 Generating complaint.json...")
                complaint_json = consolidator.to_complaint_json(consolidated_case)
                
                # Save complaint.json in case folder
                complaint_file = output_manager.save_complaint_json(case_name, complaint_json)
                
                print(f"✅ Complaint JSON saved: {complaint_file}")
                print(f"📊 Readiness Score: {consolidated_case.extraction_confidence:.1f}%")
                
                # Quick validation
                required_fields = ['case_information', 'plaintiff', 'defendants']
                missing_fields = [field for field in required_fields if not complaint_json.get(field)]
                
                if missing_fields:
                    print(f"⚠️ Missing required fields: {', '.join(missing_fields)}")
                    print(f"   Manual review recommended before document generation")
                else:
                    print(f"✅ All required fields present - Ready for Beaver processing!")
            
            # Display saved files summary
            successful_docs = len([r for r in extraction_results if r.success])
            total_files = sum(len(files) for files in saved_files_list)
            
            print(f"💾 Saved Files Summary:")
            print(f"   📄 Documents Processed: {successful_docs}/{len(extraction_results)}")
            print(f"   📁 Output Files: {total_files}")
            print(f"   📋 Case Info: {case_info_file}")
            print(f"   📊 Case Summary: {case_summary_file}")
            
            print(f"\n🎉 Case extraction completed successfully!")
            return 0
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in case-extract command")
            return 1
    
    def cmd_hydrated_json(self, args) -> int:
        """Hydrated JSON command handler"""
        case_folder = args.case_folder
        output_dir = args.output_dir or str(self.config.get_data_dirs()['output'])
        case_name = args.case_name
        exclude_files = args.exclude or []
        dashboard_url = args.dashboard_url
        
        print(f"🏛️ Satori Tiger Hydrated JSON Consolidation")
        print(f"📁 Case Folder: {case_folder}")
        print(f"📤 Output Directory: {output_dir}")
        if case_name:
            print(f"📋 Case Name: {case_name}")
        if exclude_files:
            print(f"🚫 Excluding: {', '.join(exclude_files)}")
        if dashboard_url:
            print(f"📡 Dashboard URL: {dashboard_url}")
        print()
        
        if not os.path.exists(case_folder):
            print(f"❌ Error: Case folder does not exist: {case_folder}")
            return 1
        
        if not os.path.isdir(case_folder):
            print(f"❌ Error: Path is not a directory: {case_folder}")
            return 1
        
        try:
            # Import hydrated JSON consolidator
            from core.services.hydrated_json_consolidator import consolidate_case_to_hydrated_json, process_documents_for_case
            
            print("🔄 Processing case documents and generating hydrated JSON...")
            
            # Initialize event broadcaster if dashboard URL provided
            event_broadcaster = None
            if dashboard_url:
                event_broadcaster = ProcessingEventBroadcaster(dashboard_url)
                case_id = os.path.basename(case_folder)
                event_broadcaster.broadcast_case_start(case_id, len(os.listdir(case_folder)))
            
            # First, process all documents and save their raw text
            extraction_results = process_documents_for_case(case_folder, exclude_files, event_broadcaster)
            
            output_manager = OutputManager(self.config)
            if output_dir:
                output_manager.base_output_dir = Path(output_dir)

            for result in extraction_results:
                if result.success:
                    output_manager.save_case_processing_result(result)

            # Now, consolidate the results into a single hydrated JSON
            result = consolidate_case_to_hydrated_json(
                case_folder=case_folder,
                output_dir=output_dir,
                case_name=case_name,
                exclude_files=exclude_files,
                event_broadcaster=event_broadcaster
            )
            
            print(f"✅ Hydrated JSON consolidation completed!")
            print(f"📊 Results Summary")
            print(f"{'='*40}")
            print(f"📁 Case Name: {result.case_name}")
            print(f"📄 Source Documents: {len(result.source_files)}")
            print(f"📊 Quality Score: {result.quality_score:.1f}%")
            print(f"📈 Completeness Score: {result.completeness_score:.1f}%")
            
            # Display source files
            print(f"\n📄 Processed Documents:")
            for i, file_path in enumerate(result.source_files, 1):
                filename = os.path.basename(file_path)
                print(f"   {i}. {filename}")
            
            # Display warnings if any
            if result.warnings:
                print(f"\n⚠️ Warnings ({len(result.warnings)}):")
                for warning in result.warnings[:5]:  # Show first 5 warnings
                    print(f"   - {warning}")
                if len(result.warnings) > 5:
                    print(f"   ... and {len(result.warnings) - 5} more warnings")
            
            # Validate key sections
            hydrated_json = result.hydrated_json
            print(f"\n🔍 Content Validation:")
            print(f"   Case Information: {'✅' if hydrated_json.get('case_information') else '❌'}")
            print(f"   Plaintiff: {'✅' if hydrated_json.get('parties', {}).get('plaintiff') else '❌'}")
            print(f"   Defendants: {'✅' if hydrated_json.get('parties', {}).get('defendants') else '❌'}")
            print(f"   Causes of Action: {'✅' if hydrated_json.get('causes_of_action') else '❌'}")
            print(f"   Damages: {'✅' if hydrated_json.get('damages') else '❌'}")
            
            # Legal compliance check
            causes = hydrated_json.get('causes_of_action', [])
            ny_fcra_found = any('NY FCRA' in cause.get('title', '') for cause in causes)
            federal_fcra_found = any('15 U.S.C.' in cause.get('statutory_basis', '') for cause in causes)
            
            print(f"\n⚖️ Legal Compliance:")
            print(f"   Federal FCRA Claims: {'✅' if federal_fcra_found else '❌'}")
            print(f"   NY FCRA Claims: {'✅' if ny_fcra_found else '❌'}")
            
            # Check defendants classification
            defendants = hydrated_json.get('parties', {}).get('defendants', [])
            cra_count = sum(1 for d in defendants if 'reporting agency' in d.get('type', '').lower())
            furnisher_count = len(defendants) - cra_count
            
            print(f"   CRA Defendants: {cra_count}")
            print(f"   Furnisher Defendants: {furnisher_count}")
            
            # Display output file location
            hydrated_json_file = os.path.join(output_dir, f"hydrated_FCRA_{result.case_name}.json")
            print(f"\n💾 Output File:")
            print(f"   📄 Hydrated JSON: {hydrated_json_file}")
            
            # Readiness assessment
            if result.completeness_score >= 80 and result.quality_score >= 70:
                print(f"\n🎉 READY FOR BEAVER PROCESSING!")
                print(f"   The hydrated JSON meets quality thresholds for document generation")
            elif result.completeness_score >= 60:
                print(f"\n⚠️ REQUIRES REVIEW")
                print(f"   Manual review recommended before document generation")
            else:
                print(f"\n❌ NEEDS ADDITIONAL DATA")
                print(f"   Missing critical information - additional documents may be needed")
            
            # Quick Beaver compatibility note
            print(f"\n🦫 Next Steps:")
            print(f"   1. Review hydrated JSON for accuracy")
            print(f"   2. Test with Beaver: ./satori-beaver validate {hydrated_json_file}")
            print(f"   3. Generate documents: ./satori-beaver build-complaint {hydrated_json_file}")
            
            return 0
            
        except Exception as e:
            print(f"💥 Fatal Error: {e}")
            logging.exception("Fatal error in hydrated-json command")
            return 1

def main():
    """Main CLI entry point"""
    cli = SatoriCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())