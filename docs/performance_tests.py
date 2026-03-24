#!/usr/bin/env python3
"""
Performance & Load Testing Suite for Presenton
Tests 18-20: Baseline Normal-Load, Concurrent Load, and Streaming Performance

This script establishes performance baselines and tests concurrent load scenarios,
then creates a comprehensive performance report with metrics and recommendations.
"""

import asyncio
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from statistics import mean, stdev
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:5001/api/v1/ppt"
PRESENTATION_CREATE_ENDPOINT = f"{API_BASE_URL}/presentation/create"

# Test Configuration
TEST_TIMEOUT = 120  # seconds
REQUEST_TIMEOUT = 120  # seconds


class PerformanceMetrics:
    """Container for performance metrics."""

    def __init__(
        self,
        test_name: str,
        timestamp: str,
        total_requests: int,
        successful_requests: int,
        failed_requests: int,
        response_times: List[float],
        total_time: float,
        avg_response_time: float,
        min_response_time: float,
        max_response_time: float,
        std_dev_response_time: float,
        throughput: float,
        success_rate: float,
    ):
        self.test_name = test_name
        self.timestamp = timestamp
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.failed_requests = failed_requests
        self.response_times = response_times
        self.total_time = total_time
        self.avg_response_time = avg_response_time
        self.min_response_time = min_response_time
        self.max_response_time = max_response_time
        self.std_dev_response_time = std_dev_response_time
        self.throughput = throughput
        self.success_rate = success_rate
        # Optional streaming metrics
        self.avg_ttfb: Optional[float] = None
        self.min_ttfb: Optional[float] = None
        self.max_ttfb: Optional[float] = None
        self.avg_chunk_rate: Optional[float] = None
        self.min_chunk_rate: Optional[float] = None
        self.max_chunk_rate: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding response_times list."""
        d = {
            "test_name": self.test_name,
            "timestamp": self.timestamp,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_time": self.total_time,
            "avg_response_time": self.avg_response_time,
            "min_response_time": self.min_response_time,
            "max_response_time": self.max_response_time,
            "std_dev_response_time": self.std_dev_response_time,
            "throughput": self.throughput,
            "success_rate": self.success_rate,
        }
        # Add optional streaming metrics if present
        if self.avg_ttfb is not None:
            d["avg_ttfb"] = self.avg_ttfb
            d["min_ttfb"] = self.min_ttfb
            d["max_ttfb"] = self.max_ttfb
        if self.avg_chunk_rate is not None:
            d["avg_chunk_rate"] = self.avg_chunk_rate
            d["min_chunk_rate"] = self.min_chunk_rate
            d["max_chunk_rate"] = self.max_chunk_rate
        return d


class PerformanceTestRunner:
    """Manages performance testing for Presenton API."""

    def __init__(self, api_base_url: str = API_BASE_URL):
        """Initialize the test runner."""
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.metrics: List[PerformanceMetrics] = []

    def _create_test_payload(self, test_id: int) -> Dict:
        """Create a test payload for presentation creation."""
        test_configs = [
            {
                "content": "Introduction to machine learning and artificial intelligence fundamentals",
                "n_slides": 5,
                "language": "English",
                "topic": "ML Basics",
            },
            {
                "content": "Advanced cloud computing architectures and microservices patterns",
                "n_slides": 5,
                "language": "English",
                "topic": "Cloud Architecture",
            },
            {
                "content": "Web development best practices and modern frameworks",
                "n_slides": 5,
                "language": "English",
                "topic": "Web Dev",
            },
            {
                "content": "Data science and analytics for business intelligence",
                "n_slides": 5,
                "language": "English",
                "topic": "Data Science",
            },
            {
                "content": "DevOps practices and continuous integration/deployment",
                "n_slides": 5,
                "language": "English",
                "topic": "DevOps",
            },
        ]

        config = test_configs[test_id % len(test_configs)]

        return {
            "content": config["content"],
            "n_slides": config["n_slides"],
            "language": config["language"],
            "tone": "default",
            "verbosity": "standard",
            "include_table_of_contents": False,
            "include_title_slide": True,
            "web_search": False,
            "file_paths": None,
        }

    def _make_request(self, test_id: int) -> Tuple[float, bool, Optional[str]]:
        """
        Make a single API request and measure response time.

        Returns:
            Tuple of (response_time, success, error_message)
        """
        payload = self._create_test_payload(test_id)

        try:
            start_time = time.time()
            response = self.session.post(
                PRESENTATION_CREATE_ENDPOINT,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                return response_time, True, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                return response_time, False, error_msg

        except requests.Timeout:
            return REQUEST_TIMEOUT, False, "Request timeout"
        except Exception as e:
            return 0, False, str(e)

    def test_baseline_normal_load(
        self, num_presentations: int = 5
    ) -> PerformanceMetrics:
        """
        Test 18: Baseline Normal-Load Performance
        Create presentations sequentially and measure response times.

        Args:
            num_presentations: Number of presentations to create sequentially

        Returns:
            PerformanceMetrics object with baseline measurements
        """
        logger.info("=" * 80)
        logger.info("TEST 18: BASELINE NORMAL-LOAD PERFORMANCE")
        logger.info("=" * 80)
        logger.info(f"Creating {num_presentations} presentations sequentially...")

        response_times = []
        successful = 0
        failed = 0

        start_time = time.time()

        for i in range(num_presentations):
            logger.info(f"  [{i + 1}/{num_presentations}] Creating presentation...")
            response_time, success, error = self._make_request(i)

            if success:
                response_times.append(response_time)
                successful += 1
                logger.info(f"    ✓ Success - Response time: {response_time:.2f}s")
            else:
                failed += 1
                logger.warning(f"    ✗ Failed - {error}")

            # Small delay between requests
            time.sleep(0.5)

        total_time = time.time() - start_time

        # Calculate statistics
        metrics = self._calculate_metrics(
            test_name="Baseline Normal-Load (Sequential)",
            response_times=response_times,
            total_requests=num_presentations,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
        )

        self.metrics.append(metrics)
        self._log_metrics(metrics)

        return metrics

    def test_concurrent_load(
        self, num_presentations: int = 5, max_workers: int = 3
    ) -> PerformanceMetrics:
        """
        Test 19: Concurrent Presentation Creation
        Create presentations simultaneously and measure performance.

        Args:
            num_presentations: Number of presentations to create concurrently
            max_workers: Maximum number of concurrent workers

        Returns:
            PerformanceMetrics object with concurrent load measurements
        """
        logger.info("=" * 80)
        logger.info("TEST 19: CONCURRENT PRESENTATION CREATION")
        logger.info("=" * 80)
        logger.info(
            f"Creating {num_presentations} presentations concurrently (max {max_workers} workers)..."
        )

        response_times = []
        successful = 0
        failed = 0

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._make_request, i): i
                for i in range(num_presentations)
            }

            for future in as_completed(futures):
                test_id = futures[future]
                try:
                    response_time, success, error = future.result()

                    if success:
                        response_times.append(response_time)
                        successful += 1
                        logger.info(
                            f"  [Test {test_id}] ✓ Success - Response time: {response_time:.2f}s"
                        )
                    else:
                        failed += 1
                        logger.warning(f"  [Test {test_id}] ✗ Failed - {error}")

                except Exception as e:
                    failed += 1
                    logger.error(f"  [Test {test_id}] ✗ Exception - {str(e)}")

        total_time = time.time() - start_time

        # Calculate statistics
        metrics = self._calculate_metrics(
            test_name=f"Concurrent Load ({max_workers} workers)",
            response_times=response_times,
            total_requests=num_presentations,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
        )

        self.metrics.append(metrics)
        self._log_metrics(metrics)

        return metrics

    def test_streaming_performance(self, num_samples: int = 3) -> PerformanceMetrics:
        """
        Test 20: Streaming Performance & Compile Report
        Measure streaming response characteristics.

        Args:
            num_samples: Number of streaming requests to sample

        Returns:
            PerformanceMetrics object with streaming measurements
        """
        logger.info("=" * 80)
        logger.info("TEST 20: STREAMING PERFORMANCE ANALYSIS")
        logger.info("=" * 80)
        logger.info(f"Measuring streaming performance ({num_samples} samples)...")

        response_times = []
        successful = 0
        failed = 0
        ttfb_times = []  # Time To First Byte
        chunk_rates = []  # Chunks per second

        start_time = time.time()

        for i in range(num_samples):
            logger.info(f"  [{i + 1}/{num_samples}] Measuring streaming response...")

            payload = self._create_test_payload(i)

            try:
                request_start = time.time()
                response = self.session.post(
                    PRESENTATION_CREATE_ENDPOINT,
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                    stream=True,
                )

                if response.status_code == 200:
                    # Measure time to first byte
                    ttfb = time.time() - request_start
                    ttfb_times.append(ttfb)

                    # Measure chunk delivery
                    chunk_count = 0
                    chunk_start = time.time()

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunk_count += 1

                    chunk_duration = time.time() - chunk_start
                    chunk_rate = (
                        chunk_count / chunk_duration if chunk_duration > 0 else 0
                    )
                    chunk_rates.append(chunk_rate)

                    total_response_time = time.time() - request_start
                    response_times.append(total_response_time)
                    successful += 1

                    logger.info(
                        f"    ✓ TTFB: {ttfb:.3f}s | Chunks: {chunk_count} | Rate: {chunk_rate:.1f} chunks/s"
                    )
                else:
                    failed += 1
                    logger.warning(f"    ✗ HTTP {response.status_code}")

            except Exception as e:
                failed += 1
                logger.error(f"    ✗ Error - {str(e)}")

            time.sleep(0.5)

        total_time = time.time() - start_time

        # Calculate statistics
        metrics = self._calculate_metrics(
            test_name="Streaming Performance",
            response_times=response_times,
            total_requests=num_samples,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
        )

        # Add streaming-specific metrics
        if ttfb_times:
            metrics.avg_ttfb = mean(ttfb_times)
            metrics.min_ttfb = min(ttfb_times)
            metrics.max_ttfb = max(ttfb_times)

        if chunk_rates:
            metrics.avg_chunk_rate = mean(chunk_rates)
            metrics.min_chunk_rate = min(chunk_rates)
            metrics.max_chunk_rate = max(chunk_rates)

        self.metrics.append(metrics)
        self._log_metrics(metrics)

        return metrics

    def _calculate_metrics(
        self,
        test_name: str,
        response_times: List[float],
        total_requests: int,
        successful_requests: int,
        failed_requests: int,
        total_time: float,
    ) -> PerformanceMetrics:
        """Calculate performance metrics from raw data."""

        avg_response_time = mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        std_dev = stdev(response_times) if len(response_times) > 1 else 0

        # Throughput: presentations per minute
        throughput = (successful_requests / total_time * 60) if total_time > 0 else 0

        # Success rate: percentage
        success_rate = (
            (successful_requests / total_requests * 100) if total_requests > 0 else 0
        )

        return PerformanceMetrics(
            test_name=test_name,
            timestamp=datetime.now().isoformat(),
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            total_time=total_time,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            std_dev_response_time=std_dev,
            throughput=throughput,
            success_rate=success_rate,
        )

    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log metrics in a readable format."""
        logger.info("-" * 80)
        logger.info(f"Test: {metrics.test_name}")
        logger.info(f"Total Requests: {metrics.total_requests}")
        logger.info(
            f"Successful: {metrics.successful_requests} | Failed: {metrics.failed_requests}"
        )
        logger.info(f"Success Rate: {metrics.success_rate:.1f}%")
        logger.info(f"Total Time: {metrics.total_time:.2f}s")
        logger.info(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
        logger.info(
            f"Min/Max Response Time: {metrics.min_response_time:.2f}s / {metrics.max_response_time:.2f}s"
        )
        logger.info(f"Std Dev: {metrics.std_dev_response_time:.2f}s")
        logger.info(f"Throughput: {metrics.throughput:.2f} presentations/minute")
        logger.info("-" * 80)

    def generate_report(self) -> str:
        """
        Generate comprehensive performance report with metrics and recommendations.

        Returns:
            Formatted report string
        """
        report_lines = [
            "# Presenton Performance Baseline Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            "This report establishes performance baselines for the Presenton presentation generation system.",
            "Three comprehensive tests were conducted to measure normal-load, concurrent, and streaming performance.",
            "",
        ]

        # Summary metrics table
        report_lines.extend(self._generate_summary_table())

        # Detailed test results
        report_lines.extend(self._generate_detailed_results())

        # Performance graphs
        report_lines.extend(self._generate_performance_graphs())

        # Comparative analysis
        report_lines.extend(self._generate_comparative_analysis())

        # Streaming analysis
        report_lines.extend(self._generate_streaming_analysis())

        # Recommendations
        report_lines.extend(self._generate_recommendations())

        # Baseline reference
        report_lines.extend(self._generate_baseline_reference())

        return "\n".join(report_lines)

    def _generate_summary_table(self) -> List[str]:
        """Generate summary metrics table."""
        lines = [
            "## Summary Metrics Table",
            "",
            "| Metric | Baseline | Concurrent | Streaming |",
            "|--------|----------|-----------|-----------|",
        ]

        # Ensure we have all three test results
        baseline = next((m for m in self.metrics if "Sequential" in m.test_name), None)
        concurrent = next(
            (m for m in self.metrics if "Concurrent" in m.test_name), None
        )
        streaming = next((m for m in self.metrics if "Streaming" in m.test_name), None)

        if baseline:
            lines.append(f"| Total Time | {baseline.total_time:.2f}s | - | - |")
            lines.append(
                f"| Avg Response Time | {baseline.avg_response_time:.2f}s | - | - |"
            )
            lines.append(
                f"| Min/Max Response | {baseline.min_response_time:.2f}s / {baseline.max_response_time:.2f}s | - | - |"
            )
            lines.append(f"| Std Dev | {baseline.std_dev_response_time:.2f}s | - | - |")
            lines.append(f"| Throughput | {baseline.throughput:.2f} pres/min | - | - |")
            lines.append(f"| Success Rate | {baseline.success_rate:.1f}% | - | - |")

        if concurrent:
            lines.append(f"| Concurrent Time | - | {concurrent.total_time:.2f}s | - |")
            lines.append(
                f"| Concurrent Avg Response | - | {concurrent.avg_response_time:.2f}s | - |"
            )
            lines.append(
                f"| Concurrent Throughput | - | {concurrent.throughput:.2f} pres/min | - |"
            )
            lines.append(
                f"| Concurrent Success Rate | - | {concurrent.success_rate:.1f}% | - |"
            )

        if streaming:
            lines.append(
                f"| Streaming Avg Response | - | - | {streaming.avg_response_time:.2f}s |"
            )
            lines.append(
                f"| Streaming Success Rate | - | - | {streaming.success_rate:.1f}% |"
            )

        lines.append("")
        return lines

    def _generate_detailed_results(self) -> List[str]:
        """Generate detailed test results."""
        lines = [
            "## Detailed Test Results",
            "",
        ]

        for metrics in self.metrics:
            lines.extend(
                [
                    f"### {metrics.test_name}",
                    "",
                    f"- **Test Timestamp**: {metrics.timestamp}",
                    f"- **Total Requests**: {metrics.total_requests}",
                    f"- **Successful**: {metrics.successful_requests}",
                    f"- **Failed**: {metrics.failed_requests}",
                    f"- **Success Rate**: {metrics.success_rate:.1f}%",
                    f"- **Total Execution Time**: {metrics.total_time:.2f} seconds",
                    "",
                    "#### Response Time Statistics",
                    "",
                    f"- **Average**: {metrics.avg_response_time:.2f}s",
                    f"- **Minimum**: {metrics.min_response_time:.2f}s",
                    f"- **Maximum**: {metrics.max_response_time:.2f}s",
                    f"- **Standard Deviation**: {metrics.std_dev_response_time:.2f}s",
                    f"- **Throughput**: {metrics.throughput:.2f} presentations/minute",
                    "",
                ]
            )

        return lines

    def _generate_performance_graphs(self) -> List[str]:
        """Generate ASCII performance graphs."""
        lines = [
            "## Performance Graphs",
            "",
            "### Response Time Comparison (ASCII Chart)",
            "",
        ]

        # Create ASCII bar chart for response times
        baseline = next((m for m in self.metrics if "Sequential" in m.test_name), None)
        concurrent = next(
            (m for m in self.metrics if "Concurrent" in m.test_name), None
        )
        streaming = next((m for m in self.metrics if "Streaming" in m.test_name), None)

        if baseline and concurrent and streaming:
            max_time = max(
                baseline.avg_response_time,
                concurrent.avg_response_time,
                streaming.avg_response_time,
            )

            lines.append("```")
            lines.append("Average Response Time (seconds)")
            lines.append("")

            # Baseline
            bar_length = (
                int((baseline.avg_response_time / max_time) * 40) if max_time > 0 else 0
            )
            lines.append(
                f"Baseline:   {'█' * bar_length} {baseline.avg_response_time:.2f}s"
            )

            # Concurrent
            bar_length = (
                int((concurrent.avg_response_time / max_time) * 40)
                if max_time > 0
                else 0
            )
            lines.append(
                f"Concurrent: {'█' * bar_length} {concurrent.avg_response_time:.2f}s"
            )

            # Streaming
            bar_length = (
                int((streaming.avg_response_time / max_time) * 40)
                if max_time > 0
                else 0
            )
            lines.append(
                f"Streaming:  {'█' * bar_length} {streaming.avg_response_time:.2f}s"
            )

            lines.append("```")
            lines.append("")

        # Throughput comparison
        lines.append("### Throughput Comparison (presentations/minute)")
        lines.append("")
        lines.append("```")

        if baseline and concurrent:
            max_throughput = max(baseline.throughput, concurrent.throughput)

            bar_length = (
                int((baseline.throughput / max_throughput) * 40)
                if max_throughput > 0
                else 0
            )
            lines.append(
                f"Baseline:   {'█' * bar_length} {baseline.throughput:.2f} pres/min"
            )

            bar_length = (
                int((concurrent.throughput / max_throughput) * 40)
                if max_throughput > 0
                else 0
            )
            lines.append(
                f"Concurrent: {'█' * bar_length} {concurrent.throughput:.2f} pres/min"
            )

        lines.append("```")
        lines.append("")

        return lines

    def _generate_comparative_analysis(self) -> List[str]:
        """Generate comparative analysis between sequential and concurrent."""
        lines = [
            "## Comparative Analysis: Sequential vs Concurrent",
            "",
        ]

        baseline = next((m for m in self.metrics if "Sequential" in m.test_name), None)
        concurrent = next(
            (m for m in self.metrics if "Concurrent" in m.test_name), None
        )

        if baseline and concurrent:
            time_savings = baseline.total_time - concurrent.total_time
            time_savings_pct = (
                (time_savings / baseline.total_time * 100)
                if baseline.total_time > 0
                else 0
            )

            throughput_improvement = concurrent.throughput - baseline.throughput
            throughput_improvement_pct = (
                (throughput_improvement / baseline.throughput * 100)
                if baseline.throughput > 0
                else 0
            )

            lines.extend(
                [
                    f"### Time Comparison",
                    "",
                    f"- **Sequential Total Time**: {baseline.total_time:.2f}s",
                    f"- **Concurrent Total Time**: {concurrent.total_time:.2f}s",
                    f"- **Time Savings**: {time_savings:.2f}s ({time_savings_pct:.1f}%)",
                    "",
                    f"### Throughput Comparison",
                    "",
                    f"- **Sequential Throughput**: {baseline.throughput:.2f} presentations/minute",
                    f"- **Concurrent Throughput**: {concurrent.throughput:.2f} presentations/minute",
                    f"- **Improvement**: {throughput_improvement:.2f} presentations/minute ({throughput_improvement_pct:.1f}%)",
                    "",
                    f"### Success Rate Comparison",
                    "",
                    f"- **Sequential Success Rate**: {baseline.success_rate:.1f}%",
                    f"- **Concurrent Success Rate**: {concurrent.success_rate:.1f}%",
                    "",
                ]
            )

        return lines

    def _generate_streaming_analysis(self) -> List[str]:
        """Generate streaming performance analysis."""
        lines = [
            "## Streaming Performance Analysis",
            "",
        ]

        streaming = next((m for m in self.metrics if "Streaming" in m.test_name), None)

        if streaming:
            lines.extend(
                [
                    f"### Streaming Metrics",
                    "",
                    f"- **Average Response Time**: {streaming.avg_response_time:.2f}s",
                    f"- **Min/Max Response Time**: {streaming.min_response_time:.2f}s / {streaming.max_response_time:.2f}s",
                    f"- **Success Rate**: {streaming.success_rate:.1f}%",
                    "",
                    f"### Chunk Delivery Performance",
                    "",
                    f"- **Samples Measured**: {streaming.total_requests}",
                    f"- **Successful Samples**: {streaming.successful_requests}",
                    "",
                ]
            )

            # Add TTFB and chunk rate if available
            if hasattr(streaming, "avg_ttfb"):
                lines.extend(
                    [
                        f"### Time To First Byte (TTFB)",
                        "",
                        f"- **Average TTFB**: {streaming.avg_ttfb:.3f}s",
                        f"- **Min TTFB**: {streaming.min_ttfb:.3f}s",
                        f"- **Max TTFB**: {streaming.max_ttfb:.3f}s",
                        "",
                    ]
                )

            if hasattr(streaming, "avg_chunk_rate"):
                lines.extend(
                    [
                        f"### Chunk Delivery Rate",
                        "",
                        f"- **Average Rate**: {streaming.avg_chunk_rate:.1f} chunks/second",
                        f"- **Min Rate**: {streaming.min_chunk_rate:.1f} chunks/second",
                        f"- **Max Rate**: {streaming.max_chunk_rate:.1f} chunks/second",
                        "",
                    ]
                )

        return lines

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        lines = [
            "## Recommendations for Optimization",
            "",
        ]

        baseline = next((m for m in self.metrics if "Sequential" in m.test_name), None)
        concurrent = next(
            (m for m in self.metrics if "Concurrent" in m.test_name), None
        )

        recommendations = []

        if baseline:
            if baseline.avg_response_time > 10:
                recommendations.append(
                    "- **High Response Time**: Average response time exceeds 10 seconds. "
                    "Consider optimizing LLM calls, database queries, or implementing caching."
                )

            if baseline.std_dev_response_time > baseline.avg_response_time * 0.5:
                recommendations.append(
                    "- **High Variability**: Response time standard deviation is high. "
                    "Investigate inconsistent performance patterns and resource contention."
                )

        if concurrent:
            if concurrent.success_rate < 100:
                recommendations.append(
                    "- **Concurrent Failures**: Some requests failed under concurrent load. "
                    "Review error logs and consider implementing request queuing or rate limiting."
                )

            if baseline and concurrent.throughput < baseline.throughput * 1.5:
                recommendations.append(
                    "- **Limited Concurrency Benefit**: Concurrent throughput improvement is modest. "
                    "Consider increasing worker pool size or optimizing I/O operations."
                )

        if not recommendations:
            recommendations.append(
                "- **Performance Baseline Established**: System is performing well. "
                "Continue monitoring and re-run tests periodically to track performance trends."
            )

        lines.extend(recommendations)
        lines.append("")

        return lines

    def _generate_baseline_reference(self) -> List[str]:
        """Generate baseline reference for future comparisons."""
        lines = [
            "## Baseline Reference for Future Comparisons",
            "",
            "This baseline should be used as a reference point for future performance testing.",
            "Re-run this test suite periodically to track performance trends and identify regressions.",
            "",
            "### How to Use This Baseline",
            "",
            "1. **Track Trends**: Compare future test results against these baselines",
            "2. **Identify Regressions**: Alert if performance degrades by >10%",
            "3. **Validate Optimizations**: Measure improvement from optimization efforts",
            "4. **Capacity Planning**: Use throughput metrics for capacity planning",
            "",
            "### Baseline Snapshot",
            "",
        ]

        for metrics in self.metrics:
            lines.append(f"**{metrics.test_name}**:")
            lines.append(f"- Avg Response Time: {metrics.avg_response_time:.2f}s")
            lines.append(f"- Throughput: {metrics.throughput:.2f} presentations/minute")
            lines.append(f"- Success Rate: {metrics.success_rate:.1f}%")
            lines.append("")

        return lines

    def save_report(self, filename: str = "performance_baseline_report.md"):
        """Save report to file."""
        report = self.generate_report()

        with open(filename, "w") as f:
            f.write(report)

        logger.info(f"Report saved to {filename}")

        # Also save metrics as JSON
        json_filename = filename.replace(".md", ".json")
        metrics_data = [m.to_dict() for m in self.metrics]

        with open(json_filename, "w") as f:
            json.dump(metrics_data, f, indent=2)

        logger.info(f"Metrics saved to {json_filename}")

    def close(self):
        """Close the session."""
        self.session.close()


def main():
    """Main entry point."""
    runner = None
    try:
        runner = PerformanceTestRunner()

        logger.info("Starting Presenton Performance Test Suite")
        logger.info("=" * 80)

        # Test 18: Baseline Normal-Load Performance
        baseline_metrics = runner.test_baseline_normal_load(num_presentations=5)

        # Small delay between test suites
        time.sleep(2)

        # Test 19: Concurrent Presentation Creation
        concurrent_metrics = runner.test_concurrent_load(
            num_presentations=5, max_workers=3
        )

        # Small delay between test suites
        time.sleep(2)

        # Test 20: Streaming Performance
        streaming_metrics = runner.test_streaming_performance(num_samples=3)

        # Generate and save comprehensive report
        logger.info("=" * 80)
        logger.info("Generating comprehensive performance report...")
        runner.save_report()

        # Print summary
        print("\n" + "=" * 80)
        print("PERFORMANCE TEST SUITE COMPLETED")
        print("=" * 80)
        print(runner.generate_report())

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1
    finally:
        if runner:
            runner.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
