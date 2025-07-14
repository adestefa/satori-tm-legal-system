"""
Output Handlers for Satori Tiger service
Manages saving and organizing processed document outputs
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from .formatters import TextFormatter, JSONFormatter, MarkdownFormatter, HTMLFormatter
except ImportError:
    from formatters import TextFormatter, JSONFormatter, MarkdownFormatter, HTMLFormatter

try:
    from ..core.utils.case_name_generator import CaseNameGenerator
except ImportError:
    from app.core.utils.case_name_generator import CaseNameGenerator

logger = logging.getLogger(__name__)

class OutputManager:
    """Manages output saving and organization for processed documents"""
    
    def __init__(self, config=None, use_case_folders: bool = True):
        self.base_output_dir = Path("outputs") / "tiger"
        self.config = config
        self.use_case_folders = use_case_folders
        self.logger = logging.getLogger(__name__)
        
        # Initialize case name generator
        self.case_name_generator = CaseNameGenerator()
        
        # Initialize formatters
        self.formatters = {
            'txt': TextFormatter(),
            'json': JSONFormatter(),
            'md': MarkdownFormatter(),
            'html': HTMLFormatter()
        }
        
        # Ensure output directory exists
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories (legacy structure or global reports)
        if not self.use_case_folders:
            self.subdirs = {
                'processed': self.base_output_dir / 'processed',
                'failed': self.base_output_dir / 'failed',
                'reports': self.base_output_dir / 'reports',
                'metadata': self.base_output_dir / 'metadata',
                'raw_text': self.base_output_dir / 'raw_text'
            }
            
            for subdir in self.subdirs.values():
                subdir.mkdir(parents=True, exist_ok=True)
        else:
            # Create global directories for case-based structure
            self.subdirs = {
                'cases': self.base_output_dir / 'cases',
                'legacy': self.base_output_dir / 'legacy',
                'reports': self.base_output_dir / 'reports',
                'raw_text': self.base_output_dir / 'raw_text',
                'metadata': self.base_output_dir / 'metadata'
            }
            
            for subdir in self.subdirs.values():
                subdir.mkdir(parents=True, exist_ok=True)
    
    def create_case_directory_structure(self, case_name: str) -> Dict[str, Path]:
        """
        Create complete case directory structure
        
        Args:
            case_name: Name for the case folder
            
        Returns:
            Dictionary mapping subdirectory names to paths
        """
        case_dir = self.subdirs['cases'] / case_name
        
        case_subdirs = {
            'case_root': case_dir,
            'processed': case_dir / 'processed',
            'raw_text': case_dir / 'raw_text',
            'metadata': case_dir / 'metadata'
        }
        
        # Create all directories
        for subdir in case_subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Created case directory structure: {case_dir}")
        return case_subdirs
    
    def save_case_processing_result(self, result, case_name: str = None, 
                                   consolidated_case=None) -> Dict[str, str]:
        """
        Save processing result in case-based structure
        
        Args:
            result: Processing result to save
            case_name: Manual case name (optional)
            consolidated_case: ConsolidatedCase object (optional)
            
        Returns:
            Dictionary of saved file paths
        """
        if not self.use_case_folders:
            return self.save_processing_result(result)
        
        # Generate case name if not provided
        if not case_name:
            case_name = self.case_name_generator.generate_case_folder_name(
                consolidated_case=consolidated_case,
                legal_entities=getattr(result, 'legal_entities', None)
            )
        
        # Create case directory structure
        case_dirs = self.create_case_directory_structure(case_name)
        
        # Generate clean filename (no timestamp)
        base_name = self._generate_clean_filename(result.file_name)
        
        saved_files = {}
        
        # Get output formats from config or use defaults
        output_formats = ['txt', 'json', 'md']
        if self.config and hasattr(self.config.output, 'output_formats'):
            output_formats = self.config.output.output_formats
        
        # Determine output directory based on success
        if result.success:
            output_dir = case_dirs['processed']
        else:
            # Use legacy folder for failed processing
            output_dir = self.subdirs['legacy'] / 'failed'
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save in requested formats
        for format_name in output_formats:
            if format_name in self.formatters:
                try:
                    formatted_content = self.formatters[format_name].format(result.to_dict())
                    file_extension = self.formatters[format_name].get_extension()
                    
                    output_file = output_dir / f"{base_name}.{file_extension}"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                    
                    saved_files[format_name] = str(output_file)
                    self.logger.info(f"Saved {format_name.upper()} output: {output_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save {format_name} output: {e}")
        
        # Save raw text separately if successful
        if result.success and result.extracted_text:
            try:
                raw_text_file = case_dirs['raw_text'] / f"{base_name}_raw.txt"
                with open(raw_text_file, 'w', encoding='utf-8') as f:
                    f.write(result.extracted_text)
                saved_files['raw_text'] = str(raw_text_file)
                self.logger.info(f"Saved raw text: {raw_text_file}")
            except Exception as e:
                self.logger.error(f"Failed to save raw text: {e}")
        
        # Save metadata
        try:
            metadata_file = case_dirs['metadata'] / f"{base_name}_metadata.json"
            metadata = {
                'file_info': {
                    'original_path': result.file_path,
                    'file_name': result.file_name,
                    'processing_timestamp': result.timestamp
                },
                'processing_result': {
                    'success': result.success,
                    'engine_used': result.engine_used,
                    'processing_time': result.processing_time,
                    'error': result.error
                },
                'quality_metrics': result.quality_metrics,
                'extraction_metadata': result.metadata,
                'case_info': {
                    'case_name': case_name,
                    'case_folder': str(case_dirs['case_root'])
                },
                'output_files': saved_files
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            saved_files['metadata'] = str(metadata_file)
            self.logger.info(f"Saved metadata: {metadata_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
        
        return saved_files
    
    def save_case_info_json(self, case_name: str, consolidated_case) -> str:
        """
        Save consolidated case information to case_info.json
        
        Args:
            case_name: Case folder name
            consolidated_case: ConsolidatedCase object
            
        Returns:
            Path to saved case_info.json file
        """
        try:
            case_dir = self.subdirs['cases'] / case_name
            case_info_file = case_dir / 'case_info.json'
            
            # Convert consolidated case to dictionary
            case_info = {
                'case_id': consolidated_case.case_id,
                'case_information': {
                    'case_number': consolidated_case.case_information.case_number,
                    'court_type': consolidated_case.case_information.court_type,
                    'court_district': consolidated_case.case_information.court_district,
                    'jury_demand': consolidated_case.case_information.jury_demand
                },
                'plaintiff': consolidated_case.plaintiff,
                'plaintiff_counsel': consolidated_case.plaintiff_counsel,
                'defendants': consolidated_case.defendants,
                'factual_background': consolidated_case.factual_background,
                'damages': consolidated_case.damages,
                'source_documents': consolidated_case.source_documents,
                'extraction_confidence': consolidated_case.extraction_confidence,
                'consolidation_timestamp': consolidated_case.consolidation_timestamp,
                'warnings': consolidated_case.warnings
            }
            
            with open(case_info_file, 'w', encoding='utf-8') as f:
                json.dump(case_info, f, indent=2, default=str)
            
            self.logger.info(f"Saved case info: {case_info_file}")
            return str(case_info_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save case info: {e}")
            return ""
    
    def save_complaint_json(self, case_name: str, complaint_data: Dict[str, Any]) -> str:
        """
        Save complaint JSON to case folder
        
        Args:
            case_name: Case folder name
            complaint_data: Complaint JSON data
            
        Returns:
            Path to saved complaint.json file
        """
        try:
            case_dir = self.subdirs['cases'] / case_name
            complaint_file = case_dir / 'complaint.json'
            
            with open(complaint_file, 'w', encoding='utf-8') as f:
                json.dump(complaint_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved complaint JSON: {complaint_file}")
            return str(complaint_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save complaint JSON: {e}")
            return ""
    
    def generate_case_summary(self, case_name: str, results: List, 
                             consolidated_case=None) -> str:
        """
        Generate case-level summary report
        
        Args:
            case_name: Case folder name
            results: List of processing results
            consolidated_case: ConsolidatedCase object (optional)
            
        Returns:
            Path to saved case summary file
        """
        try:
            case_dir = self.subdirs['cases'] / case_name
            summary_file = case_dir / 'case_summary.md'
            
            # Generate summary content
            lines = [
                f"# Case Summary: {case_name}",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Case Overview"
            ]
            
            if consolidated_case:
                lines.extend([
                    f"- **Case Number**: {consolidated_case.case_information.case_number or 'N/A'}",
                    f"- **Court**: {consolidated_case.case_information.court_district or 'N/A'}",
                    f"- **Plaintiff**: {consolidated_case.plaintiff.get('name', 'N/A') if consolidated_case.plaintiff else 'N/A'}",
                    f"- **Defendants**: {len(consolidated_case.defendants)} entities",
                    f"- **Extraction Confidence**: {consolidated_case.extraction_confidence:.1f}%",
                    ""
                ])
            
            # Document processing summary
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]
            
            lines.extend([
                "## Document Processing Summary",
                f"- **Total Documents**: {len(results)}",
                f"- **Successfully Processed**: {len(successful_results)}",
                f"- **Failed Processing**: {len(failed_results)}",
                f"- **Success Rate**: {len(successful_results)/len(results)*100:.1f}%",
                ""
            ])
            
            # Quality analysis
            if successful_results:
                quality_scores = [r.quality_metrics.get('quality_score', 0) 
                                for r in successful_results if r.quality_metrics]
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    high_quality = len([s for s in quality_scores if s >= 80])
                    
                    lines.extend([
                        "## Quality Analysis",
                        f"- **Average Quality Score**: {avg_quality:.1f}/100",
                        f"- **High Quality Documents (≥80)**: {high_quality}/{len(quality_scores)}",
                        ""
                    ])
            
            # Document list
            lines.extend([
                "## Processed Documents",
                ""
            ])
            
            for result in results:
                status = "✅" if result.success else "❌"
                quality = result.quality_metrics.get('quality_score', 0) if result.quality_metrics else 0
                lines.append(f"- {status} **{result.file_name}** (Quality: {quality}/100)")
            
            lines.extend([
                "",
                "---",
                "*Generated by Satori Tiger Document Processing Service*"
            ])
            
            # Save summary
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            self.logger.info(f"Saved case summary: {summary_file}")
            return str(summary_file)
            
        except Exception as e:
            self.logger.error(f"Failed to generate case summary: {e}")
            return ""
    
    def _generate_clean_filename(self, original_filename: str) -> str:
        """
        Generate clean filename without timestamp for case-based organization
        
        Args:
            original_filename: Original filename from the document
            
        Returns:
            Clean filename suitable for case folder
        """
        # Remove extension and clean filename
        base_name = Path(original_filename).stem
        
        # Replace problematic characters but keep it readable
        safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Don't add timestamp for case-based organization
        return safe_name
    
    def save_processing_result(self, result) -> Dict[str, str]:
        """Save processing result in multiple formats"""
        saved_files = {}
        
        # Determine output directory based on structure and success
        if self.use_case_folders:
            # In case folder mode, use legacy directory for single documents
            output_dir = self.subdirs['legacy']
            # Create processed/failed subdirectories in legacy folder
            if result.success:
                output_dir = output_dir / 'processed'
            else:
                output_dir = output_dir / 'failed'
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            # In legacy mode, use the standard subdirectories
            if result.success:
                output_dir = self.subdirs['processed']
            else:
                output_dir = self.subdirs['failed']
        
        # Generate base filename
        base_name = self._generate_filename(result.file_name)
        
        # Get output formats from config or use defaults
        output_formats = ['txt', 'json', 'md']
        if self.config and hasattr(self.config.output, 'output_formats'):
            output_formats = self.config.output.output_formats
        
        # Save in requested formats
        for format_name in output_formats:
            if format_name in self.formatters:
                try:
                    formatted_content = self.formatters[format_name].format(result.to_dict())
                    file_extension = self.formatters[format_name].get_extension()
                    
                    output_file = output_dir / f"{base_name}.{file_extension}"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                    
                    saved_files[format_name] = str(output_file)
                    self.logger.info(f"Saved {format_name.upper()} output: {output_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save {format_name} output: {e}")
        
        # Save raw text separately if successful
        if result.success and result.extracted_text:
            try:
                raw_text_file = self.subdirs['raw_text'] / f"{base_name}_raw.txt"
                with open(raw_text_file, 'w', encoding='utf-8') as f:
                    f.write(result.extracted_text)
                saved_files['raw_text'] = str(raw_text_file)
            except Exception as e:
                self.logger.error(f"Failed to save raw text: {e}")
        
        # Save metadata
        try:
            metadata_file = self.subdirs['metadata'] / f"{base_name}_metadata.json"
            metadata = {
                'file_info': {
                    'original_path': result.file_path,
                    'file_name': result.file_name,
                    'processing_timestamp': result.timestamp
                },
                'processing_result': {
                    'success': result.success,
                    'engine_used': result.engine_used,
                    'processing_time': result.processing_time,
                    'error': result.error
                },
                'quality_metrics': result.quality_metrics,
                'extraction_metadata': result.metadata,
                'output_files': saved_files
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            saved_files['metadata'] = str(metadata_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
        
        return saved_files
    
    def save_batch_report(self, batch_result, report_name: str = None) -> str:
        """Save batch processing report"""
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"batch_report_{timestamp}"
        
        # Generate comprehensive batch report
        report_data = self._generate_batch_report_data(batch_result)
        
        # Save as markdown report
        try:
            markdown_content = self._format_batch_report_markdown(report_data)
            report_file = self.subdirs['reports'] / f"{report_name}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Batch report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save batch report: {e}")
            return ""
    
    def save_quality_summary(self, results: List[Dict[str, Any]], summary_name: str = None) -> str:
        """Save quality analysis summary"""
        if not summary_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_name = f"quality_summary_{timestamp}"
        
        try:
            # Analyze quality metrics across all results
            quality_analysis = self._analyze_quality_metrics(results)
            
            # Generate quality report
            report_content = self._format_quality_report(quality_analysis)
            
            report_file = self.subdirs['reports'] / f"{summary_name}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"Quality summary saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save quality summary: {e}")
            return ""
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate safe filename for outputs"""
        # Remove extension and clean filename
        base_name = Path(original_filename).stem
        
        # Replace problematic characters
        safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{safe_name}_{timestamp}"
    
    def _generate_batch_report_data(self, batch_result) -> Dict[str, Any]:
        """Generate comprehensive batch report data"""
        summary = batch_result.summary
        results = batch_result.results
        
        # Calculate additional statistics
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        quality_scores = [r.quality_metrics.get('quality_score', 0) 
                         for r in successful_results if r.quality_metrics]
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Engine usage statistics
        engine_usage = {}
        for result in results:
            engine = result.engine_used
            engine_usage[engine] = engine_usage.get(engine, 0) + 1
        
        # File type statistics
        file_types = {}
        for result in results:
            ext = Path(result.file_name).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'summary': summary,
            'statistics': {
                'avg_quality_score': avg_quality,
                'quality_score_range': [min(quality_scores), max(quality_scores)] if quality_scores else [0, 0],
                'engine_usage': engine_usage,
                'file_type_distribution': file_types,
                'avg_processing_time': summary.get('total_processing_time', 0) / max(summary.get('total_files', 1), 1)
            },
            'successful_results': successful_results,
            'failed_results': failed_results,
            'processing_errors': batch_result.processing_errors
        }
    
    def _format_batch_report_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format batch report as markdown"""
        lines = []
        
        # Header
        lines.extend([
            "# Satori Tiger Batch Processing Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary"
        ])
        
        summary = report_data['summary']
        stats = report_data['statistics']
        
        lines.extend([
            f"- **Total Files Processed:** {summary.get('total_files', 0)}",
            f"- **Successful Extractions:** {summary.get('successful', 0)}",
            f"- **Failed Extractions:** {summary.get('failed', 0)}",
            f"- **Success Rate:** {summary.get('success_rate', 0):.1f}%",
            f"- **Average Quality Score:** {stats['avg_quality_score']:.1f}/100",
            f"- **Total Processing Time:** {summary.get('total_processing_time', 0):.2f} seconds",
            ""
        ])
        
        # Engine performance
        if stats['engine_usage']:
            lines.extend([
                "## Engine Performance",
                ""
            ])
            for engine, count in stats['engine_usage'].items():
                lines.append(f"- **{engine}:** {count} documents")
            lines.append("")
        
        # File type breakdown
        if stats['file_type_distribution']:
            lines.extend([
                "## File Type Distribution",
                ""
            ])
            for file_type, count in stats['file_type_distribution'].items():
                lines.append(f"- **{file_type.upper()}:** {count} files")
            lines.append("")
        
        # Quality analysis
        successful_results = report_data['successful_results']
        if successful_results:
            high_quality = len([r for r in successful_results 
                               if r.quality_metrics.get('quality_score', 0) >= 80])
            medium_quality = len([r for r in successful_results 
                                 if 50 <= r.quality_metrics.get('quality_score', 0) < 80])
            low_quality = len([r for r in successful_results 
                              if r.quality_metrics.get('quality_score', 0) < 50])
            
            lines.extend([
                "## Quality Distribution",
                "",
                f"- **High Quality (≥80):** {high_quality} documents",
                f"- **Medium Quality (50-79):** {medium_quality} documents", 
                f"- **Low Quality (<50):** {low_quality} documents",
                ""
            ])
        
        # Errors and issues
        failed_results = report_data['failed_results']
        if failed_results:
            lines.extend([
                "## Processing Failures",
                ""
            ])
            for result in failed_results[:5]:  # Show first 5 failures
                lines.append(f"- **{result.file_name}:** {result.error}")
            
            if len(failed_results) > 5:
                lines.append(f"- *...and {len(failed_results) - 5} more failures*")
            lines.append("")
        
        # Processing errors
        if report_data['processing_errors']:
            lines.extend([
                "## Processing Errors",
                ""
            ])
            for error in report_data['processing_errors'][:3]:  # Show first 3 errors
                lines.append(f"- {error}")
            lines.append("")
        
        lines.extend([
            "---",
            "*Generated by Satori Tiger Document Processing Service*"
        ])
        
        return '\n'.join(lines)
    
    def _analyze_quality_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality metrics across results"""
        # Extract quality metrics
        quality_data = []
        for result in results:
            if result.get('quality_metrics'):
                quality_data.append(result['quality_metrics'])
        
        if not quality_data:
            return {'error': 'No quality metrics to analyze'}
        
        # Calculate statistics
        scores = [q.get('quality_score', 0) for q in quality_data]
        compression_ratios = [q.get('compression_ratio', 0) for q in quality_data]
        text_lengths = [q.get('text_length', 0) for q in quality_data]
        
        return {
            'total_documents': len(quality_data),
            'score_statistics': {
                'average': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'high_quality_count': len([s for s in scores if s >= 80]),
                'medium_quality_count': len([s for s in scores if 50 <= s < 80]),
                'low_quality_count': len([s for s in scores if s < 50])
            },
            'compression_statistics': {
                'average': sum(compression_ratios) / len(compression_ratios),
                'min': min(compression_ratios),
                'max': max(compression_ratios),
                'optimal_count': len([r for r in compression_ratios if 0.002 <= r <= 0.05])
            },
            'text_length_statistics': {
                'average': sum(text_lengths) / len(text_lengths),
                'min': min(text_lengths),
                'max': max(text_lengths),
                'total_characters': sum(text_lengths)
            }
        }
    
    def _format_quality_report(self, analysis: Dict[str, Any]) -> str:
        """Format quality analysis as markdown report"""
        if 'error' in analysis:
            return f"# Quality Analysis Report\n\nError: {analysis['error']}"
        
        lines = [
            "# Satori Tiger Quality Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"**Documents Analyzed:** {analysis['total_documents']}",
            ""
        ]
        
        # Score analysis
        score_stats = analysis['score_statistics']
        lines.extend([
            "## Quality Score Analysis",
            "",
            f"- **Average Score:** {score_stats['average']:.1f}/100",
            f"- **Score Range:** {score_stats['min']:.1f} - {score_stats['max']:.1f}",
            f"- **High Quality (≥80):** {score_stats['high_quality_count']} documents",
            f"- **Medium Quality (50-79):** {score_stats['medium_quality_count']} documents",
            f"- **Low Quality (<50):** {score_stats['low_quality_count']} documents",
            ""
        ])
        
        # Compression analysis
        comp_stats = analysis['compression_statistics']
        lines.extend([
            "## Compression Ratio Analysis",
            "",
            f"- **Average Ratio:** {comp_stats['average']:.4f}",
            f"- **Range:** {comp_stats['min']:.4f} - {comp_stats['max']:.4f}",
            f"- **Optimal Range (0.002-0.05):** {comp_stats['optimal_count']} documents",
            ""
        ])
        
        # Text length analysis
        text_stats = analysis['text_length_statistics']
        lines.extend([
            "## Text Extraction Analysis",
            "",
            f"- **Average Length:** {text_stats['average']:.0f} characters",
            f"- **Range:** {text_stats['min']:,} - {text_stats['max']:,} characters",
            f"- **Total Extracted:** {text_stats['total_characters']:,} characters",
            ""
        ])
        
        lines.extend([
            "---",
            "*Generated by Satori Tiger Document Processing Service*"
        ])
        
        return '\n'.join(lines)
    
    def get_output_summary(self) -> Dict[str, Any]:
        """Get summary of saved outputs"""
        summary = {
            'base_directory': str(self.base_output_dir),
            'subdirectories': {k: str(v) for k, v in self.subdirs.items()},
            'file_counts': {}
        }
        
        # Count files in each subdirectory
        for name, path in self.subdirs.items():
            if path.exists():
                summary['file_counts'][name] = len(list(path.iterdir()))
            else:
                summary['file_counts'][name] = 0
        
        return summary