"""
Quality Report Generator for Tiger Engine
Enhanced reporting for legal document processing with comprehensive analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class TigerQualityReporter:
    """Generate comprehensive quality reports for Tiger document processing"""
    
    def __init__(self, results_data: Dict):
        self.results = results_data
        self.summary = results_data.get('summary', {})
        self.document_results = results_data.get('results', [])
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary report for legal teams"""
        report = []
        
        report.append("# TIGER ENGINE QUALITY REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Engine: Satori Tiger Document Processing Service\n")
        
        # Overall Statistics
        report.append("## PROCESSING SUMMARY")
        total = self.summary.get('total', 0)
        successful = self.summary.get('successful', 0)
        failed = self.summary.get('failed', 0)
        warnings = self.summary.get('warnings', 0)
        
        report.append(f"- **Total Documents Processed:** {total}")
        report.append(f"- **Successfully Processed:** {successful}")
        report.append(f"- **Failed Extractions:** {failed}")
        report.append(f"- **Documents with Warnings:** {warnings}")
        
        success_rate = (successful / max(total, 1)) * 100
        report.append(f"- **Success Rate:** {success_rate:.1f}%")
        
        # Quality scoring
        if self.document_results:
            avg_quality = sum(doc.get('quality_metrics', {}).get('quality_score', 0) 
                            for doc in self.document_results) / len(self.document_results)
            report.append(f"- **Average Quality Score:** {avg_quality:.1f}/100\n")
        
        return "\n".join(report)
    
    def generate_legal_analysis(self) -> str:
        """Generate legal document specific analysis"""
        report = []
        
        report.append("## LEGAL DOCUMENT ANALYSIS")
        report.append("-" * 40)
        
        # Document type classification
        doc_types = {}
        legal_indicators_summary = {
            'court_documents': 0,
            'case_numbers_found': 0,
            'summons_detected': 0,
            'complaints_detected': 0,
            'addresses_extracted': 0,
            'phone_numbers_extracted': 0,
            'emails_extracted': 0
        }
        
        for doc in self.document_results:
            doc_type = self.classify_legal_document(doc.get('quality_metrics', {}).get('legal_indicators', {}))
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Count legal indicators
            legal_indicators = doc.get('quality_metrics', {}).get('legal_indicators', {})
            if legal_indicators.get('court_document'):
                legal_indicators_summary['court_documents'] += 1
            if legal_indicators.get('case_number'):
                legal_indicators_summary['case_numbers_found'] += 1
            if legal_indicators.get('summons'):
                legal_indicators_summary['summons_detected'] += 1
            if legal_indicators.get('complaint'):
                legal_indicators_summary['complaints_detected'] += 1
            
            legal_indicators_summary['addresses_extracted'] += legal_indicators.get('addresses', {}).get('count', 0)
            legal_indicators_summary['phone_numbers_extracted'] += legal_indicators.get('phone_numbers', {}).get('count', 0)
            legal_indicators_summary['emails_extracted'] += legal_indicators.get('emails', {}).get('count', 0)
        
        # Document type distribution
        report.append("### Document Type Distribution")
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{doc_type}:** {count} documents")
        
        # Legal indicators summary
        report.append("\n### Legal Information Extraction")
        report.append(f"- **Court Documents Identified:** {legal_indicators_summary['court_documents']}")
        report.append(f"- **Case Numbers Found:** {legal_indicators_summary['case_numbers_found']}")
        report.append(f"- **Summons Documents:** {legal_indicators_summary['summons_detected']}")
        report.append(f"- **Complaint Documents:** {legal_indicators_summary['complaints_detected']}")
        report.append(f"- **Total Addresses Extracted:** {legal_indicators_summary['addresses_extracted']}")
        report.append(f"- **Total Phone Numbers Extracted:** {legal_indicators_summary['phone_numbers_extracted']}")
        report.append(f"- **Total Email Addresses Extracted:** {legal_indicators_summary['emails_extracted']}")
        
        return "\n".join(report)
    
    def classify_legal_document(self, legal_indicators: Dict) -> str:
        """Classify legal document type based on indicators"""
        if legal_indicators.get('summons'):
            return "Court Summons"
        elif legal_indicators.get('complaint'):
            return "Legal Complaint"
        elif legal_indicators.get('court_document'):
            return "Court Document"
        elif any(word in str(legal_indicators).lower() for word in ['credit', 'denial', 'adverse']):
            return "Credit/Financial Document"
        elif any(word in str(legal_indicators).lower() for word in ['attorney', 'legal', 'counsel']):
            return "Attorney Notes/Correspondence"
        else:
            return "General Document"
    
    def generate_quality_breakdown(self) -> str:
        """Generate detailed quality score breakdown"""
        report = []
        
        report.append("## QUALITY SCORE BREAKDOWN")
        report.append("-" * 35)
        
        if not self.document_results:
            report.append("No documents to analyze.")
            return "\n".join(report)
        
        # Quality distribution
        quality_scores = [doc.get('quality_metrics', {}).get('quality_score', 0) 
                         for doc in self.document_results]
        
        high_quality = sum(1 for s in quality_scores if s >= 80)
        medium_quality = sum(1 for s in quality_scores if 50 <= s < 80)
        low_quality = sum(1 for s in quality_scores if s < 50)
        
        total_docs = len(quality_scores)
        report.append(f"### Quality Distribution (Total: {total_docs} documents)")
        report.append(f"- **High Quality (≥80):** {high_quality} documents ({high_quality/total_docs*100:.1f}%)")
        report.append(f"- **Medium Quality (50-79):** {medium_quality} documents ({medium_quality/total_docs*100:.1f}%)")
        report.append(f"- **Low Quality (<50):** {low_quality} documents ({low_quality/total_docs*100:.1f}%)")
        
        # Top performing documents
        top_docs = sorted(self.document_results, 
                         key=lambda x: x.get('quality_metrics', {}).get('quality_score', 0), 
                         reverse=True)[:3]
        
        if top_docs:
            report.append("\n### Top Performing Documents")
            for i, doc in enumerate(top_docs, 1):
                quality = doc.get('quality_metrics', {})
                score = quality.get('quality_score', 0)
                engine = doc.get('engine_used', 'Unknown')
                report.append(f"{i}. **{doc.get('file_name')}** - {score}/100 (Engine: {engine})")
        
        return "\n".join(report)
    
    def generate_recommendations(self) -> str:
        """Generate actionable recommendations for improving quality"""
        report = []
        
        report.append("## ACTIONABLE RECOMMENDATIONS")
        report.append("-" * 35)
        
        # Analyze issues
        low_quality_docs = [doc for doc in self.document_results 
                           if doc.get('quality_metrics', {}).get('quality_score', 0) < 50]
        
        failed_threshold_docs = [doc for doc in self.document_results 
                               if not doc.get('quality_metrics', {}).get('passes_threshold', True)]
        
        high_compression_docs = [doc for doc in self.document_results 
                               if doc.get('quality_metrics', {}).get('compression_ratio', 0) > 0.1]
        
        recommendations = []
        
        if low_quality_docs:
            recommendations.append(f"🔍 **Manual Review Required:** {len(low_quality_docs)} documents scored below 50")
            recommendations.append("   - Consider re-scanning at higher resolution")
            recommendations.append("   - Verify document orientation and lighting")
            
        if failed_threshold_docs:
            recommendations.append(f"⚠️ **Quality Threshold Failures:** {len(failed_threshold_docs)} documents failed validation")
            recommendations.append("   - Re-process with enhanced OCR settings")
            recommendations.append("   - Check for damaged or corrupted source files")
            
        if high_compression_docs:
            recommendations.append(f"📊 **High Compression Ratio:** {len(high_compression_docs)} documents may have OCR errors")
            recommendations.append("   - Validate extracted text for accuracy")
            recommendations.append("   - Consider alternative OCR engines for problematic files")
        
        # Success patterns
        high_quality_docs = [doc for doc in self.document_results 
                           if doc.get('quality_metrics', {}).get('quality_score', 0) >= 80]
        
        if high_quality_docs:
            engine_performance = {}
            for doc in high_quality_docs:
                engine = doc.get('engine_used', 'Unknown')
                engine_performance[engine] = engine_performance.get(engine, 0) + 1
            
            best_engine = max(engine_performance.items(), key=lambda x: x[1])
            recommendations.append(f"✅ **Best Performing Engine:** {best_engine[0]} ({best_engine[1]} high-quality extractions)")
            recommendations.append("   - Prioritize this engine for similar document types")
        
        if not recommendations:
            recommendations.append("✅ **Excellent Performance:** All documents processed successfully with high quality scores!")
        
        for rec in recommendations:
            report.append(rec)
        
        return "\n".join(report)
    
    def generate_case_readiness_report(self) -> str:
        """Generate legal case readiness assessment"""
        report = []
        
        report.append("## LEGAL CASE READINESS ASSESSMENT")
        report.append("-" * 40)
        
        # Check for required legal document components
        case_elements = {
            'case_numbers': 0,
            'court_documents': 0,
            'summons_documents': 0,
            'defendant_addresses': 0,
            'plaintiff_info': 0,
            'attorney_info': 0
        }
        
        for doc in self.document_results:
            legal_indicators = doc.get('quality_metrics', {}).get('legal_indicators', {})
            
            if legal_indicators.get('case_number'):
                case_elements['case_numbers'] += 1
            if legal_indicators.get('court_document'):
                case_elements['court_documents'] += 1
            if legal_indicators.get('summons'):
                case_elements['summons_documents'] += 1
            if legal_indicators.get('addresses', {}).get('count', 0) > 0:
                case_elements['defendant_addresses'] += 1
        
        total_docs = len(self.document_results)
        report.append("### Required Elements Detection")
        report.append(f"- **Case Numbers:** {case_elements['case_numbers']}/{total_docs} documents")
        report.append(f"- **Court Documents:** {case_elements['court_documents']}/{total_docs} documents")
        report.append(f"- **Summons Documents:** {case_elements['summons_documents']}/{total_docs} documents")
        report.append(f"- **Address Information:** {case_elements['defendant_addresses']}/{total_docs} documents")
        
        # Case readiness score
        completeness_score = sum(1 for count in case_elements.values() if count > 0) / len(case_elements) * 100
        report.append(f"\n**Case Completeness Score:** {completeness_score:.1f}%")
        
        if completeness_score >= 80:
            report.append("🟢 **Status: READY FOR LEGAL PROCESSING**")
        elif completeness_score >= 60:
            report.append("🟡 **Status: MOSTLY READY - Minor gaps identified**")
        else:
            report.append("🔴 **Status: INCOMPLETE - Significant missing elements**")
        
        return "\n".join(report)
    
    def generate_full_report(self) -> str:
        """Generate complete Tiger quality report"""
        sections = [
            self.generate_executive_summary(),
            self.generate_legal_analysis(),
            self.generate_quality_breakdown(),
            self.generate_case_readiness_report(),
            self.generate_recommendations()
        ]
        
        footer = [
            "\n" + "=" * 50,
            "Generated by Satori Tiger Document Processing Service",
            "Designed for Consumer Protection Legal Practice",
            "=" * 50
        ]
        
        return "\n\n".join(sections) + "\n".join(footer)

def generate_tiger_quality_report(results_data: Dict, output_path: Optional[str] = None) -> str:
    """
    Generate a comprehensive quality report from Tiger processing results
    
    Args:
        results_data: Tiger batch processing results
        output_path: Optional path to save the report file
    
    Returns:
        Generated report as string
    """
    reporter = TigerQualityReporter(results_data)
    full_report = reporter.generate_full_report()
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(full_report)
    
    return full_report