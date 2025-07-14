"""
Performance and load testing for Tiger legal extraction system.
Tests processing speed, memory usage, and scalability limits.
"""

import unittest
import time
import psutil
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from app.core.extractors.legal_entity_extractor import LegalEntityExtractor
from app.core.processors.case_consolidator import CaseConsolidator
from app.engines.base_engine import ExtractionResult


class TestPerformance(unittest.TestCase):
    """Performance tests for legal extraction components."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
        self.process = psutil.Process(os.getpid())
    
    def measure_performance(self, func, *args, **kwargs) -> Dict[str, Any]:
        """Measure execution time and memory usage of a function."""
        # Get initial memory
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Measure execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Get peak memory
        peak_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'initial_memory_mb': initial_memory,
            'peak_memory_mb': peak_memory,
            'memory_increase_mb': peak_memory - initial_memory
        }
    
    def generate_large_document(self, size_kb: int = 100) -> str:
        """Generate a large legal document for testing."""
        base_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES
        
        TO THE HONORABLE JUDGES OF THIS COURT:
        
        Plaintiff brings this action against Defendants and alleges:
        
        1. This action arises under the Fair Credit Reporting Act.
        2. Plaintiff is a consumer within the meaning of the FCRA.
        3. Defendants violated their duties under the FCRA.
        """
        
        # Repeat text to reach desired size
        target_bytes = size_kb * 1024
        current_size = len(base_text.encode('utf-8'))
        repetitions = target_bytes // current_size + 1
        
        large_text = base_text * repetitions
        return large_text[:target_bytes]
    
    def test_extraction_performance_small_document(self):
        """Test extraction performance on small documents (< 10KB)."""
        text = self.generate_large_document(5)  # 5KB
        
        metrics = self.measure_performance(
            self.extractor.extract_case_information, text
        )
        
        # Performance expectations for small documents
        self.assertLess(metrics['execution_time'], 1.0, "Small document extraction should take < 1s")
        self.assertLess(metrics['memory_increase_mb'], 10, "Memory increase should be < 10MB")
        
        print(f"Small doc (5KB): {metrics['execution_time']:.3f}s, +{metrics['memory_increase_mb']:.1f}MB")
    
    def test_extraction_performance_medium_document(self):
        """Test extraction performance on medium documents (50-100KB)."""
        text = self.generate_large_document(75)  # 75KB
        
        metrics = self.measure_performance(
            self.extractor.extract_case_information, text
        )
        
        # Performance expectations for medium documents
        self.assertLess(metrics['execution_time'], 3.0, "Medium document extraction should take < 3s")
        self.assertLess(metrics['memory_increase_mb'], 25, "Memory increase should be < 25MB")
        
        print(f"Medium doc (75KB): {metrics['execution_time']:.3f}s, +{metrics['memory_increase_mb']:.1f}MB")
    
    def test_extraction_performance_large_document(self):
        """Test extraction performance on large documents (500KB+)."""
        text = self.generate_large_document(500)  # 500KB
        
        metrics = self.measure_performance(
            self.extractor.extract_case_information, text
        )
        
        # Performance expectations for large documents
        self.assertLess(metrics['execution_time'], 10.0, "Large document extraction should take < 10s")
        self.assertLess(metrics['memory_increase_mb'], 100, "Memory increase should be < 100MB")
        
        print(f"Large doc (500KB): {metrics['execution_time']:.3f}s, +{metrics['memory_increase_mb']:.1f}MB")
    
    def test_batch_processing_performance(self):
        """Test performance of processing multiple documents in batch."""
        # Create batch of documents
        documents = [self.generate_large_document(20) for _ in range(10)]  # 10 x 20KB docs
        
        def process_batch():
            results = []
            for i, text in enumerate(documents):
                case_info = self.extractor.extract_case_information(text)
                legal_entities = self.extractor.extract_legal_entities(text)
                
                result = ExtractionResult(success=True, text=text)
                result.extracted_text = text
                result.file_path = f"batch_doc_{i}.txt"
                results.append(result)
            return results
        
        metrics = self.measure_performance(process_batch)
        
        # Performance expectations for batch processing
        docs_per_second = 10 / metrics['execution_time']
        self.assertGreater(docs_per_second, 2, "Should process at least 2 docs/second")
        self.assertLess(metrics['memory_increase_mb'], 50, "Batch memory increase should be < 50MB")
        
        print(f"Batch (10x20KB): {metrics['execution_time']:.3f}s, {docs_per_second:.1f} docs/s, +{metrics['memory_increase_mb']:.1f}MB")
    
    def test_consolidation_performance(self):
        """Test performance of case consolidation with multiple documents."""
        # Create multiple extraction results
        results = []
        for i in range(20):  # 20 documents
            text = self.generate_large_document(10)  # 10KB each
            result = ExtractionResult(success=True, text=text)
            result.extracted_text = text
            result.file_path = f"test_doc_{i}.txt"
            results.append(result)
        
        def consolidate_case():
            with tempfile.TemporaryDirectory() as temp_dir:
                return self.consolidator.consolidate_case_folder(temp_dir, results)
        
        metrics = self.measure_performance(consolidate_case)
        
        # Performance expectations for consolidation
        self.assertLess(metrics['execution_time'], 5.0, "Consolidation should take < 5s")
        self.assertLess(metrics['memory_increase_mb'], 30, "Consolidation memory increase should be < 30MB")
        
        print(f"Consolidation (20 docs): {metrics['execution_time']:.3f}s, +{metrics['memory_increase_mb']:.1f}MB")
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated processing."""
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        # Process documents repeatedly
        for i in range(50):
            text = self.generate_large_document(10)
            self.extractor.extract_case_information(text)
            
            # Check memory every 10 iterations
            if i % 10 == 0:
                current_memory = self.process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable (< 100MB total)
                self.assertLess(memory_growth, 100, 
                               f"Excessive memory growth detected: {memory_growth:.1f}MB after {i+1} iterations")
        
        final_memory = self.process.memory_info().rss / 1024 / 1024
        total_growth = final_memory - initial_memory
        
        print(f"Memory leak test: {total_growth:.1f}MB growth over 50 iterations")
        
        # Final check - total growth should be reasonable
        self.assertLess(total_growth, 150, "Total memory growth suggests potential leak")
    
    def test_regex_performance(self):
        """Test performance of regex patterns used in legal extraction."""
        # Create text with many potential matches
        text_with_many_case_numbers = ""
        for i in range(1000):
            text_with_many_case_numbers += f"Case No. 1:25-cv-{i:05d}\n"
        
        metrics = self.measure_performance(
            self.extractor._extract_case_number, text_with_many_case_numbers
        )
        
        # Regex should be fast even with many matches
        self.assertLess(metrics['execution_time'], 0.5, "Regex matching should be < 0.5s for 1000 patterns")
        
        print(f"Regex performance (1000 matches): {metrics['execution_time']:.3f}s")
    
    def test_concurrent_processing_simulation(self):
        """Simulate concurrent processing load."""
        import threading
        import queue
        
        # Create work queue
        work_queue = queue.Queue()
        results_queue = queue.Queue()
        
        # Add work items
        for i in range(20):
            text = self.generate_large_document(15)
            work_queue.put(text)
        
        def worker():
            """Worker function to process documents."""
            while True:
                try:
                    text = work_queue.get(timeout=1)
                    start_time = time.time()
                    
                    case_info = self.extractor.extract_case_information(text)
                    legal_entities = self.extractor.extract_legal_entities(text)
                    
                    processing_time = time.time() - start_time
                    results_queue.put(processing_time)
                    work_queue.task_done()
                    
                except queue.Empty:
                    break
        
        # Start worker threads
        num_workers = 4
        start_time = time.time()
        
        threads = []
        for _ in range(num_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # Wait for completion
        work_queue.join()
        total_time = time.time() - start_time
        
        # Collect results
        processing_times = []
        while not results_queue.empty():
            processing_times.append(results_queue.get())
        
        # Calculate statistics
        avg_processing_time = sum(processing_times) / len(processing_times)
        throughput = len(processing_times) / total_time
        
        print(f"Concurrent processing: {len(processing_times)} docs in {total_time:.2f}s")
        print(f"Throughput: {throughput:.1f} docs/s, Avg: {avg_processing_time:.3f}s/doc")
        
        # Performance expectations
        self.assertGreater(throughput, 3, "Concurrent throughput should be > 3 docs/s")
        self.assertLess(avg_processing_time, 2, "Average processing time should be < 2s")


class TestScalabilityLimits(unittest.TestCase):
    """Test system behavior at scale limits."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_maximum_document_size(self):
        """Test processing of very large documents (5MB+)."""
        # Generate a 5MB document
        large_text = "A" * (5 * 1024 * 1024)  # 5MB of text
        
        start_time = time.time()
        try:
            result = self.extractor.extract_case_information(large_text)
            processing_time = time.time() - start_time
            
            print(f"5MB document processed in {processing_time:.2f}s")
            
            # Should complete within reasonable time
            self.assertLess(processing_time, 30, "5MB document should process within 30s")
            
        except Exception as e:
            self.fail(f"Failed to process 5MB document: {e}")
    
    def test_maximum_case_folder_size(self):
        """Test consolidation with many documents (100+)."""
        # Create 100 small extraction results
        results = []
        for i in range(100):
            text = f"Document {i}: Case No. 1:25-cv-{i:05d}"
            result = ExtractionResult(success=True, text=text)
            result.extracted_text = text
            result.file_path = f"test_doc_{i}.txt"
            results.append(result)
        
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
                processing_time = time.time() - start_time
                
                print(f"100 documents consolidated in {processing_time:.2f}s")
                
                # Should complete within reasonable time
                self.assertLess(processing_time, 10, "100 documents should consolidate within 10s")
                self.assertIsNotNone(consolidated)
                
            except Exception as e:
                self.fail(f"Failed to consolidate 100 documents: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("TIGER LEGAL EXTRACTION PERFORMANCE TESTS")
    print("=" * 60)
    
    # Run performance tests
    unittest.main(verbosity=2, buffer=False)