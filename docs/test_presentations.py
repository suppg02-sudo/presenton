#!/usr/bin/env python3
"""
Test Presentations Generator for Presenton Enhancement-11
Generates 10 test presentations with varying parameters to test system functionality.
"""

import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

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

# Test Matrix Definition
TEST_MATRIX = [
    {
        "test_id": 1,
        "language": "English",
        "n_slides": 3,
        "topic": "Simple topic",
        "content": "Introduction to basic concepts and fundamentals",
        "include_images": False,
    },
    {
        "test_id": 2,
        "language": "Spanish",
        "n_slides": 5,
        "topic": "Business topic",
        "content": "Estrategias empresariales y gestión de proyectos",
        "include_images": False,
    },
    {
        "test_id": 3,
        "language": "French",
        "n_slides": 5,
        "topic": "Technology topic",
        "content": "Les dernières avancées technologiques et l'innovation",
        "include_images": False,
    },
    {
        "test_id": 4,
        "language": "English",
        "n_slides": 10,
        "topic": "Educational topic",
        "content": "Comprehensive learning materials and educational frameworks",
        "include_images": False,
    },
    {
        "test_id": 5,
        "language": "German",
        "n_slides": 3,
        "topic": "Creative topic",
        "content": "Kreative Ideen und künstlerische Ausdrucksformen",
        "include_images": False,
    },
    {
        "test_id": 6,
        "language": "English",
        "n_slides": 5,
        "topic": "Marketing topic",
        "content": "Digital marketing strategies and customer engagement",
        "include_images": False,
    },
    {
        "test_id": 7,
        "language": "Spanish",
        "n_slides": 10,
        "topic": "Science topic",
        "content": "Descubrimientos científicos y avances en investigación",
        "include_images": False,
    },
    {
        "test_id": 8,
        "language": "English",
        "n_slides": 3,
        "topic": "Mixed topic",
        "content": "Combination of various subjects and interdisciplinary approaches",
        "include_images": False,
    },
    {
        "test_id": 9,
        "language": "French",
        "n_slides": 5,
        "topic": "Professional topic",
        "content": "Développement professionnel et compétences en milieu de travail",
        "include_images": False,
    },
    {
        "test_id": 10,
        "language": "Italian",
        "n_slides": 5,
        "topic": "Cultural topic",
        "content": "Patrimonio culturale e tradizioni storiche",
        "include_images": False,
    },
]


class PresentationTestRunner:
    """Manages test presentation creation and logging."""

    def __init__(self, api_base_url: str = API_BASE_URL):
        """Initialize the test runner."""
        self.api_base_url = api_base_url
        self.results: List[Dict] = []
        self.session = requests.Session()

    def create_presentation(self, test_config: Dict) -> Dict:
        """
        Create a single test presentation.

        Args:
            test_config: Test configuration dictionary

        Returns:
            Result dictionary with status and presentation ID
        """
        test_id = test_config["test_id"]
        language = test_config["language"]
        n_slides = test_config["n_slides"]
        topic = test_config["topic"]
        content = test_config["content"]

        # Prepare request payload
        payload = {
            "content": content,
            "n_slides": n_slides,
            "language": language,
            "tone": "default",
            "verbosity": "standard",
            "include_table_of_contents": False,
            "include_title_slide": True,
            "web_search": False,
            "file_paths": None,
        }

        result = {
            "test_id": test_id,
            "topic": topic,
            "language": language,
            "n_slides": n_slides,
            "include_images": test_config["include_images"],
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "presentation_id": None,
            "error": None,
        }

        try:
            logger.info(
                f"Test {test_id}: Creating presentation - {topic} ({language}, {n_slides} slides)"
            )

            response = self.session.post(
                PRESENTATION_CREATE_ENDPOINT,
                json=payload,
                timeout=60,
            )

            if response.status_code == 200:
                response_data = response.json()
                presentation_id = response_data.get("id")
                result["presentation_id"] = presentation_id
                result["status"] = "success"
                logger.info(
                    f"Test {test_id}: ✓ Created successfully - ID: {presentation_id}"
                )
            else:
                result["status"] = "failed"
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Test {test_id}: ✗ Failed - {result['error']}")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Test {test_id}: ✗ Error - {str(e)}")

        self.results.append(result)
        return result

    def run_all_tests(self) -> List[Dict]:
        """
        Run all test presentations sequentially.

        Returns:
            List of result dictionaries
        """
        logger.info("=" * 80)
        logger.info("PRESENTON TEST PRESENTATIONS - ENHANCEMENT-11")
        logger.info("=" * 80)
        logger.info(f"Starting test run at {datetime.now().isoformat()}")
        logger.info(f"Total tests to run: {len(TEST_MATRIX)}")
        logger.info("=" * 80)

        for test_config in TEST_MATRIX:
            self.create_presentation(test_config)
            # Small delay between requests to avoid overwhelming the server
            time.sleep(0.5)

        return self.results

    def generate_report(self) -> str:
        """
        Generate a formatted test report.

        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 100,
            "PRESENTON TEST PRESENTATIONS - RESULTS REPORT",
            "=" * 100,
            f"Report Generated: {datetime.now().isoformat()}",
            f"Total Tests: {len(self.results)}",
            f"Successful: {sum(1 for r in self.results if r['status'] == 'success')}",
            f"Failed: {sum(1 for r in self.results if r['status'] in ['failed', 'error'])}",
            "=" * 100,
            "",
            "DETAILED RESULTS:",
            "-" * 100,
        ]

        for result in self.results:
            report_lines.append(
                f"Test #{result['test_id']:02d} | "
                f"Topic: {result['topic']:<25} | "
                f"Language: {result['language']:<10} | "
                f"Slides: {result['n_slides']:<2} | "
                f"Images: {'Yes' if result['include_images'] else 'No':<3} | "
                f"Status: {result['status']:<8}"
            )

            if result["presentation_id"]:
                report_lines.append(
                    f"         Presentation ID: {result['presentation_id']}"
                )

            if result["error"]:
                report_lines.append(f"         Error: {result['error']}")

            report_lines.append(f"         Timestamp: {result['timestamp']}")
            report_lines.append("")

        report_lines.extend(
            [
                "-" * 100,
                "SUMMARY BY LANGUAGE:",
                "-" * 100,
            ]
        )

        # Group by language
        languages = {}
        for result in self.results:
            lang = result["language"]
            if lang not in languages:
                languages[lang] = {"total": 0, "success": 0}
            languages[lang]["total"] += 1
            if result["status"] == "success":
                languages[lang]["success"] += 1

        for lang, stats in sorted(languages.items()):
            report_lines.append(
                f"{lang:<15} - Total: {stats['total']}, Successful: {stats['success']}"
            )

        report_lines.extend(
            [
                "",
                "-" * 100,
                "SUMMARY BY SLIDE COUNT:",
                "-" * 100,
            ]
        )

        # Group by slide count
        slide_counts = {}
        for result in self.results:
            slides = result["n_slides"]
            if slides not in slide_counts:
                slide_counts[slides] = {"total": 0, "success": 0}
            slide_counts[slides]["total"] += 1
            if result["status"] == "success":
                slide_counts[slides]["success"] += 1

        for slides in sorted(slide_counts.keys()):
            stats = slide_counts[slides]
            report_lines.append(
                f"{slides} slides - Total: {stats['total']}, Successful: {stats['success']}"
            )

        report_lines.extend(
            [
                "",
                "=" * 100,
            ]
        )

        return "\n".join(report_lines)

    def save_results(self, filename: str = "test_results_presentations.txt"):
        """
        Save test results to a file.

        Args:
            filename: Output filename
        """
        report = self.generate_report()

        with open(filename, "w") as f:
            f.write(report)

        logger.info(f"Results saved to {filename}")

        # Also save JSON results for programmatic access
        json_filename = filename.replace(".txt", ".json")
        with open(json_filename, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"JSON results saved to {json_filename}")

    def close(self):
        """Close the session."""
        self.session.close()


def main():
    """Main entry point."""
    runner = None
    try:
        runner = PresentationTestRunner()

        # Run all tests
        results = runner.run_all_tests()

        # Generate and save report
        runner.save_results()

        # Print summary
        print("\n" + runner.generate_report())

        # Return exit code based on results
        failed_count = sum(1 for r in results if r["status"] in ["failed", "error"])
        return 0 if failed_count == 0 else 1

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1
    finally:
        if runner:
            runner.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
