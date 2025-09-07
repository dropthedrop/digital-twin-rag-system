#!/usr/bin/env python3
"""
Digital Twin RAG System Testing Script
=====================================

Comprehensive testing suite for the Digital Twin RAG (Retrieval-Augmented Generation) system.
Tests vector search functionality, retrieval quality, and performance benchmarks.

Features:
- Semantic search testing with professional queries
- Retrieval quality assessment and relevance scoring
- Metadata filtering validation
- Performance benchmarking and latency measurements
- Concurrent search operation testing
- Search result ranking and accuracy validation

Author: Digital Twin RAG Testing Syst                logger.info(f"   {test['name']}: {'[PASS]' if filter_success else '[FAIL]'}")m
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from upstash_vector import Index

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_testing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SearchTestCase:
    """Represents a search test case"""
    query: str
    expected_content_types: List[str]
    expected_keywords: List[str]
    min_relevance_score: float
    description: str
    category: str

@dataclass
class SearchResult:
    """Represents a search result with metadata"""
    content: str
    score: float
    metadata: Dict[str, Any]
    chunk_id: str
    content_type: str

@dataclass
class TestResults:
    """Aggregated test results"""
    test_name: str
    query: str
    results: List[SearchResult]
    execution_time: float
    relevance_scores: List[float]
    passed: bool
    error: Optional[str] = None
    expected_types_found: List[str] = None
    keywords_matched: List[str] = None

@dataclass
class PerformanceMetrics:
    """Performance benchmarking metrics"""
    total_queries: int = 0
    total_time: float = 0.0
    avg_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    queries_per_second: float = 0.0
    concurrent_queries: int = 0
    concurrent_time: float = 0.0
    errors: int = 0

class DigitalTwinRAGTester:
    """Main RAG testing class"""
    
    def __init__(self):
        """Initialize the RAG tester"""
        self.postgres_conn = None
        self.vector_index = None
        self.performance_metrics = PerformanceMetrics()
        
        # Configuration
        self.postgres_url = os.getenv('POSTGRES_CONNECTION_STRING') or "postgresql://neondb_owner:npg_BAWzXMoQ69yn@ep-rapid-silence-a93kwvl5-pooler.gwc.azure.neon.tech/neondb?channel_binding=require&sslmode=require"
        self.vector_url = os.getenv('UPSTASH_VECTOR_REST_URL')
        self.vector_token = os.getenv('UPSTASH_VECTOR_REST_TOKEN')
        
        if not self.vector_url or not self.vector_token:
            raise ValueError("Missing Upstash Vector configuration")
        
        # Define comprehensive test cases
        self.test_cases = self._create_test_cases()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect_databases()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connections()
    
    def connect_databases(self):
        """Establish database connections"""
        try:
            logger.info("Connecting to databases...")
            
            # PostgreSQL connection
            self.postgres_conn = psycopg2.connect(
                self.postgres_url,
                cursor_factory=RealDictCursor
            )
            
            # Upstash Vector connection
            self.vector_index = Index(
                url=self.vector_url,
                token=self.vector_token
            )
            
            # Verify connections
            info = self.vector_index.info()
            logger.info(f"[OK] Connected to databases")
            logger.info(f"   PostgreSQL: Connected")
            logger.info(f"   Upstash Vector: {info.vector_count} vectors, {info.dimension}D")
            
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {str(e)}")
            raise
    
    def close_connections(self):
        """Close database connections"""
        if self.postgres_conn:
            self.postgres_conn.close()
    
    def _create_test_cases(self) -> List[SearchTestCase]:
        """Create comprehensive test cases for RAG evaluation"""
        return [
            # Professional Experience Queries
            SearchTestCase(
                query="What experience do you have with AI and machine learning?",
                expected_content_types=["experience", "skills", "project"],
                expected_keywords=["ai", "machine learning", "artificial intelligence"],
                min_relevance_score=0.7,
                description="AI and ML experience inquiry",
                category="experience"
            ),
            
            SearchTestCase(
                query="Tell me about your most challenging project",
                expected_content_types=["project", "experience"],
                expected_keywords=["project", "challenge", "achievement"],
                min_relevance_score=0.6,
                description="Project complexity and achievements",
                category="projects"
            ),
            
            SearchTestCase(
                query="What are your technical skills in web development?",
                expected_content_types=["skills", "experience"],
                expected_keywords=["web", "development", "programming"],
                min_relevance_score=0.7,
                description="Web development technical skills",
                category="skills"
            ),
            
            SearchTestCase(
                query="Describe your leadership experience and team management",
                expected_content_types=["experience", "project"],
                expected_keywords=["leadership", "team", "management"],
                min_relevance_score=0.6,
                description="Leadership and management capabilities",
                category="leadership"
            ),
            
            # Technical Skills Queries
            SearchTestCase(
                query="What programming languages and frameworks do you know?",
                expected_content_types=["skills", "experience"],
                expected_keywords=["programming", "languages", "frameworks"],
                min_relevance_score=0.7,
                description="Programming languages and frameworks",
                category="technical"
            ),
            
            SearchTestCase(
                query="Do you have experience with cloud platforms and DevOps?",
                expected_content_types=["skills", "experience"],
                expected_keywords=["cloud", "devops", "aws", "azure"],
                min_relevance_score=0.7,
                description="Cloud and DevOps expertise",
                category="technical"
            ),
            
            SearchTestCase(
                query="What database technologies have you worked with?",
                expected_content_types=["skills", "experience"],
                expected_keywords=["database", "sql", "nosql"],
                min_relevance_score=0.6,
                description="Database technology experience",
                category="technical"
            ),
            
            # Project Portfolio Queries
            SearchTestCase(
                query="Show me examples of full-stack applications you've built",
                expected_content_types=["project"],
                expected_keywords=["full-stack", "application", "web"],
                min_relevance_score=0.6,
                description="Full-stack development projects",
                category="projects"
            ),
            
            SearchTestCase(
                query="What blockchain or cryptocurrency projects have you worked on?",
                expected_content_types=["project", "experience"],
                expected_keywords=["blockchain", "cryptocurrency", "crypto"],
                min_relevance_score=0.7,
                description="Blockchain and crypto projects",
                category="projects"
            ),
            
            # Educational Background
            SearchTestCase(
                query="What is your educational background and qualifications?",
                expected_content_types=["education"],
                expected_keywords=["education", "degree", "university"],
                min_relevance_score=0.7,
                description="Educational qualifications",
                category="education"
            ),
            
            # Career Progression
            SearchTestCase(
                query="How has your career progressed over the years?",
                expected_content_types=["experience"],
                expected_keywords=["career", "progression", "growth"],
                min_relevance_score=0.6,
                description="Career development and progression",
                category="career"
            ),
            
            # Specific Achievement Details
            SearchTestCase(
                query="What are your most significant professional achievements?",
                expected_content_types=["experience", "project"],
                expected_keywords=["achievement", "success", "accomplishment"],
                min_relevance_score=0.6,
                description="Professional achievements and successes",
                category="achievements"
            ),
            
            # Problem-Solving and Innovation
            SearchTestCase(
                query="How do you approach problem-solving and innovation?",
                expected_content_types=["experience", "project"],
                expected_keywords=["problem", "solving", "innovation"],
                min_relevance_score=0.5,
                description="Problem-solving methodology",
                category="methodology"
            ),
            
            # Industry Knowledge
            SearchTestCase(
                query="What do you know about software engineering best practices?",
                expected_content_types=["experience", "skills"],
                expected_keywords=["software", "engineering", "practices"],
                min_relevance_score=0.6,
                description="Software engineering best practices",
                category="methodology"
            ),
            
            # Collaboration and Communication
            SearchTestCase(
                query="How do you work in collaborative environments?",
                expected_content_types=["experience"],
                expected_keywords=["collaboration", "team", "communication"],
                min_relevance_score=0.5,
                description="Collaboration and teamwork",
                category="soft_skills"
            )
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all RAG tests and return comprehensive results"""
        logger.info("[START] Starting Comprehensive RAG System Testing")
        logger.info("="*60)
        
        start_time = time.time()
        all_results = []
        category_results = {}
        
        try:
            # Run individual test cases
            for i, test_case in enumerate(self.test_cases, 1):
                logger.info(f"Running Test {i}/{len(self.test_cases)}: {test_case.description}")
                
                result = self.run_single_test(test_case)
                all_results.append(result)
                
                # Group by category
                category = test_case.category
                if category not in category_results:
                    category_results[category] = []
                category_results[category].append(result)
                
                logger.info(f"   {'[PASS]' if result.passed else '[FAIL]'} - {result.query[:50]}...")
                if result.error:
                    logger.warning(f"   Error: {result.error}")
            
            # Run performance benchmarks
            logger.info("\n[BENCH] Running Performance Benchmarks...")
            self.run_performance_tests()
            
            # Run metadata filtering tests
            logger.info("\n[FILTER] Running Metadata Filtering Tests...")
            filtering_results = self.run_metadata_filtering_tests()
            
            # Run concurrent search tests
            logger.info("\n⚡ Running Concurrent Search Tests...")
            concurrent_results = self.run_concurrent_search_tests()
            
            # Compile final results
            total_time = time.time() - start_time
            summary = self.generate_test_summary(all_results, category_results, total_time)
            
            # Save detailed results
            self.save_test_results({
                'summary': summary,
                'individual_tests': [self._serialize_test_result(r) for r in all_results],
                'category_breakdown': {k: [self._serialize_test_result(r) for r in v] for k, v in category_results.items()},
                'performance_metrics': self._serialize_performance_metrics(),
                'filtering_tests': filtering_results,
                'concurrent_tests': concurrent_results,
                'timestamp': datetime.now().isoformat()
            })
            
            return summary
            
        except Exception as e:
            logger.error(f"[ERROR] RAG testing failed: {str(e)}")
            raise
    
    def run_single_test(self, test_case: SearchTestCase) -> TestResults:
        """Run a single search test case"""
        start_time = time.time()
        
        try:
            # Perform vector search
            search_results = self.vector_index.query(
                data=test_case.query,
                top_k=5,
                include_metadata=True
            )
            
            execution_time = time.time() - start_time
            self.performance_metrics.total_queries += 1
            self.performance_metrics.total_time += execution_time
            
            # Process results
            processed_results = []
            relevance_scores = []
            content_types_found = set()
            keywords_matched = set()
            
            if search_results:
                for result in search_results:
                    # Extract content and metadata
                    if hasattr(result, 'metadata') and result.metadata:
                        metadata = result.metadata
                        if hasattr(metadata, 'get'):
                            content_type = metadata.get('content_type', 'unknown')
                            
                            # Fix chunk_id mapping: vector DB uses upstash- prefix
                            vector_id = str(result.id)
                            if vector_id.startswith('upstash-'):
                                chunk_id = vector_id[8:]  # Remove 'upstash-' prefix
                            else:
                                chunk_id = metadata.get('chunk_id', 'unknown')
                        else:
                            content_type = getattr(metadata, 'content_type', 'unknown')
                            
                            # Fix chunk_id mapping: vector DB uses upstash- prefix
                            vector_id = str(result.id)
                            if vector_id.startswith('upstash-'):
                                chunk_id = vector_id[8:]  # Remove 'upstash-' prefix
                            else:
                                chunk_id = getattr(metadata, 'chunk_id', 'unknown')
                    else:
                        metadata = {}
                        content_type = 'unknown'
                        chunk_id = 'unknown'
                    
                    # Get content from PostgreSQL if needed
                    content = self.get_chunk_content(chunk_id) if chunk_id != 'unknown' else "Content not found"
                    
                    search_result = SearchResult(
                        content=content,
                        score=getattr(result, 'score', 0.0),
                        metadata=metadata,
                        chunk_id=str(chunk_id),
                        content_type=content_type
                    )
                    
                    processed_results.append(search_result)
                    relevance_scores.append(search_result.score)
                    content_types_found.add(content_type)
                    
                    # Check for keyword matches
                    content_lower = content.lower()
                    for keyword in test_case.expected_keywords:
                        if keyword.lower() in content_lower:
                            keywords_matched.add(keyword)
            
            # Evaluate test success
            passed = self.evaluate_test_success(
                test_case, processed_results, relevance_scores, 
                content_types_found, keywords_matched
            )
            
            return TestResults(
                test_name=test_case.description,
                query=test_case.query,
                results=processed_results,
                execution_time=execution_time,
                relevance_scores=relevance_scores,
                passed=passed,
                expected_types_found=list(content_types_found),
                keywords_matched=list(keywords_matched)
            )
            
        except Exception as e:
            self.performance_metrics.errors += 1
            return TestResults(
                test_name=test_case.description,
                query=test_case.query,
                results=[],
                execution_time=time.time() - start_time,
                relevance_scores=[],
                passed=False,
                error=str(e)
            )
    
    def get_chunk_content(self, chunk_id: str) -> str:
        """Retrieve chunk content from PostgreSQL"""
        try:
            with self.postgres_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT content FROM content_chunks WHERE chunk_id = %s",
                    (chunk_id,)
                )
                result = cursor.fetchone()
                if result:
                    # Handle both tuple and dict-like results
                    if isinstance(result, (list, tuple)):
                        return result[0]
                    else:
                        return result.get('content', str(result))
                else:
                    logger.warning(f"No content found for chunk_id: {chunk_id}")
                    return "Content not found"
        except Exception as e:
            logger.warning(f"Could not retrieve content for chunk {chunk_id}: {type(e).__name__}: {str(e)}")
            return "Content retrieval error"
    
    def evaluate_test_success(
        self, 
        test_case: SearchTestCase, 
        results: List[SearchResult], 
        scores: List[float],
        content_types_found: set,
        keywords_matched: set
    ) -> bool:
        """Evaluate if a test case passed based on multiple criteria"""
        
        # Check if we got any results
        if not results:
            return False
        
        # Check minimum relevance score
        if scores and max(scores) < test_case.min_relevance_score:
            return False
        
        # Check if expected content types are present
        expected_types_set = set(test_case.expected_content_types)
        if not expected_types_set.intersection(content_types_found):
            return False
        
        # Check if at least some keywords matched
        expected_keywords_set = set(keyword.lower() for keyword in test_case.expected_keywords)
        matched_keywords_set = set(keyword.lower() for keyword in keywords_matched)
        if not expected_keywords_set.intersection(matched_keywords_set):
            return False
        
        return True
    
    def run_performance_tests(self):
        """Run performance benchmarking tests"""
        try:
            # Test various query types for latency
            performance_queries = [
                "experience with software development",
                "technical skills in programming",
                "education and qualifications",
                "project portfolio examples",
                "leadership and management experience"
            ]
            
            latencies = []
            
            for query in performance_queries:
                start_time = time.time()
                
                try:
                    self.vector_index.query(
                        data=query,
                        top_k=3,
                        include_metadata=True
                    )
                    latency = time.time() - start_time
                    latencies.append(latency)
                    
                    self.performance_metrics.min_latency = min(self.performance_metrics.min_latency, latency)
                    self.performance_metrics.max_latency = max(self.performance_metrics.max_latency, latency)
                    
                except Exception as e:
                    logger.warning(f"Performance test query failed: {str(e)}")
                    self.performance_metrics.errors += 1
            
            if latencies:
                self.performance_metrics.avg_latency = statistics.mean(latencies)
                self.performance_metrics.queries_per_second = 1 / self.performance_metrics.avg_latency
                
                logger.info(f"   Average Latency: {self.performance_metrics.avg_latency:.3f}s")
                logger.info(f"   Queries/Second: {self.performance_metrics.queries_per_second:.1f}")
                logger.info(f"   Latency Range: {self.performance_metrics.min_latency:.3f}s - {self.performance_metrics.max_latency:.3f}s")
            
        except Exception as e:
            logger.error(f"Performance testing failed: {str(e)}")
    
    def run_metadata_filtering_tests(self) -> List[Dict[str, Any]]:
        """Test metadata filtering capabilities"""
        filtering_tests = []
        
        filter_test_cases = [
            {
                "name": "Filter by Experience Content",
                "filter": "content_type = 'experience'",
                "query": "software development experience",
                "expected_type": "experience"
            },
            {
                "name": "Filter by Skills Content", 
                "filter": "content_type = 'skills'",
                "query": "programming languages",
                "expected_type": "skills"
            },
            {
                "name": "Filter by Project Content",
                "filter": "content_type = 'project'",
                "query": "web application development",
                "expected_type": "project"
            },
            {
                "name": "Filter by High Importance",
                "filter": "importance = 'high'",
                "query": "professional expertise",
                "expected_importance": "high"
            }
        ]
        
        for test in filter_test_cases:
            try:
                start_time = time.time()
                
                results = self.vector_index.query(
                    data=test["query"],
                    top_k=3,
                    include_metadata=True,
                    filter=test["filter"]
                )
                
                execution_time = time.time() - start_time
                
                # Validate filter worked
                filter_success = True
                result_types = []
                
                if results:
                    for result in results:
                        if hasattr(result, 'metadata') and result.metadata:
                            metadata = result.metadata
                            if hasattr(metadata, 'get'):
                                content_type = metadata.get('content_type')
                                importance = metadata.get('importance')
                            else:
                                content_type = getattr(metadata, 'content_type', None)
                                importance = getattr(metadata, 'importance', None)
                                
                            result_types.append(content_type)
                            
                            # Check filter criteria
                            if 'expected_type' in test and content_type != test['expected_type']:
                                filter_success = False
                            if 'expected_importance' in test and importance != test['expected_importance']:
                                filter_success = False
                
                filtering_tests.append({
                    "test_name": test["name"],
                    "filter": test["filter"],
                    "query": test["query"],
                    "execution_time": execution_time,
                    "results_count": len(results) if results else 0,
                    "filter_success": filter_success,
                    "result_types": result_types,
                    "passed": filter_success and (len(results) if results else 0) > 0
                })
                
                logger.info(f"   {test['name']}: {'[PASS]' if filter_success else '[FAIL]'}")
                
            except Exception as e:
                filtering_tests.append({
                    "test_name": test["name"],
                    "filter": test["filter"],
                    "query": test["query"],
                    "execution_time": 0,
                    "results_count": 0,
                    "filter_success": False,
                    "result_types": [],
                    "passed": False,
                    "error": str(e)
                })
                logger.warning(f"   {test['name']}: [FAIL] - {str(e)}")
        
        return filtering_tests
    
    def run_concurrent_search_tests(self) -> Dict[str, Any]:
        """Test concurrent search operations"""
        try:
            concurrent_queries = [
                "experience with AI and machine learning",
                "web development skills and expertise", 
                "project management and leadership",
                "database and backend development",
                "cloud platforms and DevOps experience"
            ]
            
            num_concurrent = len(concurrent_queries)
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = {
                    executor.submit(
                        self.vector_index.query,
                        data=query,
                        top_k=3,
                        include_metadata=True
                    ): query for query in concurrent_queries
                }
                
                results = {}
                errors = []
                
                for future in as_completed(futures):
                    query = futures[future]
                    try:
                        result = future.result()
                        results[query] = {
                            "success": True,
                            "results_count": len(result) if result else 0
                        }
                    except Exception as e:
                        results[query] = {
                            "success": False,
                            "error": str(e)
                        }
                        errors.append(str(e))
            
            total_time = time.time() - start_time
            
            self.performance_metrics.concurrent_queries = num_concurrent
            self.performance_metrics.concurrent_time = total_time
            
            concurrent_results = {
                "total_queries": num_concurrent,
                "total_time": total_time,
                "queries_per_second": num_concurrent / total_time,
                "success_rate": sum(1 for r in results.values() if r["success"]) / num_concurrent,
                "errors": errors,
                "individual_results": results
            }
            
            logger.info(f"   Concurrent Queries: {num_concurrent}")
            logger.info(f"   Total Time: {total_time:.3f}s")
            logger.info(f"   Success Rate: {concurrent_results['success_rate']:.1%}")
            
            return concurrent_results
            
        except Exception as e:
            logger.error(f"Concurrent testing failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_test_summary(
        self, 
        all_results: List[TestResults], 
        category_results: Dict[str, List[TestResults]], 
        total_time: float
    ) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        passed_tests = [r for r in all_results if r.passed]
        failed_tests = [r for r in all_results if not r.passed]
        
        # Calculate performance metrics
        if self.performance_metrics.total_queries > 0:
            self.performance_metrics.avg_latency = self.performance_metrics.total_time / self.performance_metrics.total_queries
            self.performance_metrics.queries_per_second = self.performance_metrics.total_queries / self.performance_metrics.total_time
        
        # Category breakdown
        category_summary = {}
        for category, results in category_results.items():
            category_passed = sum(1 for r in results if r.passed)
            category_summary[category] = {
                "total": len(results),
                "passed": category_passed,
                "success_rate": category_passed / len(results) if results else 0,
                "avg_relevance": statistics.mean([
                    max(r.relevance_scores) if r.relevance_scores else 0 
                    for r in results
                ]) if results else 0
            }
        
        summary = {
            "total_tests": len(all_results),
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "success_rate": len(passed_tests) / len(all_results) if all_results else 0,
            "total_execution_time": total_time,
            "average_query_time": statistics.mean([r.execution_time for r in all_results]) if all_results else 0,
            "category_breakdown": category_summary,
            "performance_metrics": {
                "avg_latency": self.performance_metrics.avg_latency,
                "queries_per_second": self.performance_metrics.queries_per_second,
                "min_latency": self.performance_metrics.min_latency if self.performance_metrics.min_latency != float('inf') else 0,
                "max_latency": self.performance_metrics.max_latency,
                "concurrent_performance": {
                    "queries": self.performance_metrics.concurrent_queries,
                    "time": self.performance_metrics.concurrent_time
                }
            },
            "errors": self.performance_metrics.errors,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def _serialize_test_result(self, result: TestResults) -> Dict[str, Any]:
        """Serialize test result for JSON output"""
        return {
            "test_name": result.test_name,
            "query": result.query,
            "passed": result.passed,
            "execution_time": result.execution_time,
            "results_count": len(result.results),
            "avg_relevance_score": statistics.mean(result.relevance_scores) if result.relevance_scores else 0,
            "max_relevance_score": max(result.relevance_scores) if result.relevance_scores else 0,
            "content_types_found": result.expected_types_found or [],
            "keywords_matched": result.keywords_matched or [],
            "error": result.error
        }
    
    def _serialize_performance_metrics(self) -> Dict[str, Any]:
        """Serialize performance metrics"""
        return {
            "total_queries": self.performance_metrics.total_queries,
            "total_time": self.performance_metrics.total_time,
            "avg_latency": self.performance_metrics.avg_latency,
            "min_latency": self.performance_metrics.min_latency if self.performance_metrics.min_latency != float('inf') else 0,
            "max_latency": self.performance_metrics.max_latency,
            "queries_per_second": self.performance_metrics.queries_per_second,
            "concurrent_queries": self.performance_metrics.concurrent_queries,
            "concurrent_time": self.performance_metrics.concurrent_time,
            "errors": self.performance_metrics.errors
        }
    
    def save_test_results(self, results: Dict[str, Any]):
        """Save test results to JSON file"""
        try:
            output_file = f"rag_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📄 Test results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save test results: {str(e)}")
    
    def log_summary(self, summary: Dict[str, Any]):
        """Log final test summary"""
        logger.info("="*60)
        logger.info("[SUMMARY] RAG SYSTEM TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"🧪 Total Tests: {summary['total_tests']}")
        logger.info(f"[PASS] Passed: {summary['passed']}")
        logger.info(f"[FAIL] Failed: {summary['failed']}")
        logger.info(f"📈 Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")
        logger.info(f"[TIME] Avg Query Time: {summary['average_query_time']:.3f}s")
        
        logger.info("\n📂 Category Breakdown:")
        for category, stats in summary['category_breakdown'].items():
            logger.info(f"   {category.title()}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1%})")
        
        logger.info("\n⚡ Performance Metrics:")
        perf = summary['performance_metrics']
        logger.info(f"   Average Latency: {perf['avg_latency']:.3f}s")
        logger.info(f"   Queries/Second: {perf['queries_per_second']:.1f}")
        logger.info(f"   Latency Range: {perf['min_latency']:.3f}s - {perf['max_latency']:.3f}s")
        
        if summary['errors'] > 0:
            logger.warning(f"[WARN] {summary['errors']} errors encountered during testing")
        
        overall_status = "[EXCELLENT]" if summary['success_rate'] > 0.9 else \
                        "[GOOD]" if summary['success_rate'] > 0.7 else \
                        "[NEEDS IMPROVEMENT]" if summary['success_rate'] > 0.5 else \
                        "[POOR]"
        
        logger.info(f"\n[STATUS] Overall RAG System Status: {overall_status}")
        logger.info("="*60)

def main():
    """Main testing execution"""
    logger.info("[START] Starting Digital Twin RAG System Testing")
    
    try:
        with DigitalTwinRAGTester() as tester:
            summary = tester.run_all_tests()
            tester.log_summary(summary)
            
            # Exit with appropriate code
            if summary['success_rate'] >= 0.8:
                logger.info("[SUCCESS] RAG system testing completed successfully!")
                sys.exit(0)
            else:
                logger.warning("[WARN] RAG system has issues that need attention")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"[ERROR] RAG testing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()