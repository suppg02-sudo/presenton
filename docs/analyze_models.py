#!/usr/bin/env python3
"""
Model Distribution Analyzer for Presenton
Extracts model names from container logs and generates distribution analysis report.
"""

import json
import re
import subprocess
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys


class ModelAnalyzer:
    """Analyzes model usage from Docker logs."""

    def __init__(self):
        self.model_usage = Counter()
        self.model_examples = defaultdict(list)
        self.total_requests = 0
        self.fallback_events = []
        self.response_times = defaultdict(list)

    def extract_logs(self) -> str:
        """Extract logs from running presenton container."""
        try:
            result = subprocess.run(
                ["docker", "logs", "presenton"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout + result.stderr
        except Exception as e:
            print(f"Error extracting logs: {e}")
            return ""

    def parse_model_usage(self, logs: str) -> None:
        """Parse model usage from logs."""
        # Pattern 1: "Actual model used: model_name"
        pattern1 = r"Actual model used:\s*([^\s,\n]+)"
        # Pattern 2: "[MODEL_USAGE] ... Used model_name"
        pattern2 = r"\[MODEL_USAGE\].*Used\s+([^\s,\n]+)"
        # Pattern 3: "LLM Request completed.*Actual model used: model_name"
        pattern3 = r"Actual model used:\s*([^\s,\n]+)"
        # Pattern 4: Available models list
        pattern4 = r"Available models:\s*\[(.*?)\]"

        # Extract model usage
        for match in re.finditer(pattern1, logs):
            model = match.group(1).strip()
            self.model_usage[model] += 1
            self.total_requests += 1

        for match in re.finditer(pattern2, logs):
            model = match.group(1).strip()
            if model not in self.model_usage:
                self.model_usage[model] += 1
                self.total_requests += 1

        # Extract available models
        for match in re.finditer(pattern4, logs):
            models_str = match.group(1)
            models = [m.strip().strip("'\"") for m in models_str.split(",")]
            for model in models:
                if model and model not in self.model_usage:
                    self.model_usage[model] = 0

        # Detect fallback events
        fallback_pattern = r"fallback|retry|unavailable|error.*model"
        for match in re.finditer(fallback_pattern, logs, re.IGNORECASE):
            self.fallback_events.append(match.group(0))

    def analyze_openrouter_models(self) -> None:
        """Analyze OpenRouter free tier models from logs."""
        logs = self.extract_logs()

        # Extract available models from logs
        pattern = r"Available models:\s*\[(.*?)\]"
        for match in re.finditer(pattern, logs):
            models_str = match.group(1)
            models = [m.strip().strip("'\"") for m in models_str.split(",")]

            # Count free tier models
            free_models = [m for m in models if ":free" in m or "free" in m.lower()]

            for model in free_models:
                if model:
                    self.model_usage[model] += 0  # Initialize if not present

        self.parse_model_usage(logs)

    def get_model_distribution(self) -> Dict[str, float]:
        """Calculate percentage distribution of models."""
        if self.total_requests == 0:
            # If no actual usage, show available models
            total = sum(self.model_usage.values()) or len(self.model_usage)
            return {
                model: (count / total * 100)
                if total > 0
                else (100 / len(self.model_usage))
                for model, count in self.model_usage.items()
            }

        return {
            model: (count / self.total_requests * 100)
            for model, count in self.model_usage.items()
        }

    def get_top_models(self, n: int = 10) -> List[Tuple[str, int, float]]:
        """Get top N models by usage."""
        distribution = self.get_model_distribution()
        sorted_models = sorted(
            self.model_usage.items(), key=lambda x: x[1], reverse=True
        )
        return [
            (model, count, distribution.get(model, 0))
            for model, count in sorted_models[:n]
        ]

    def generate_ascii_chart(self, top_n: int = 10) -> str:
        """Generate ASCII bar chart of model distribution."""
        top_models = self.get_top_models(top_n)

        if not top_models:
            return "No model data available"

        chart = "\n" + "=" * 80 + "\n"
        chart += "MODEL DISTRIBUTION CHART\n"
        chart += "=" * 80 + "\n\n"

        max_name_len = max(len(model) for model, _, _ in top_models)
        max_percentage = max(pct for _, _, pct in top_models)

        for model, count, percentage in top_models:
            bar_length = (
                int((percentage / max_percentage) * 50) if max_percentage > 0 else 0
            )
            bar = "█" * bar_length
            chart += f"{model:<{max_name_len}} | {bar:<50} | {percentage:6.2f}% ({count:3d})\n"

        chart += "\n" + "=" * 80 + "\n"
        return chart

    def generate_report(self, output_file: str = "model_distribution_report.md") -> str:
        """Generate comprehensive markdown report."""
        self.analyze_openrouter_models()

        report = []
        report.append("# Model Distribution Analysis Report\n")
        report.append(
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        # Summary Section
        report.append("## Summary\n")
        report.append(
            f"- **Total Requests Analyzed:** {self.total_requests if self.total_requests > 0 else 'N/A (logs not yet generated)'}\n"
        )
        report.append(f"- **Unique Models Available:** {len(self.model_usage)}\n")
        report.append(f"- **Fallback Events Detected:** {len(self.fallback_events)}\n")
        report.append(f"- **Analysis Timestamp:** {datetime.now().isoformat()}\n\n")

        # Top Models Table
        report.append("## Top Models by Usage\n\n")
        report.append("| Rank | Model Name | Count | Percentage | Status |\n")
        report.append("|------|------------|-------|------------|--------|\n")

        top_models = self.get_top_models(15)
        for idx, (model, count, percentage) in enumerate(top_models, 1):
            status = "Free Tier" if ":free" in model else "Premium"
            report.append(
                f"| {idx:2d} | `{model}` | {count:3d} | {percentage:6.2f}% | {status} |\n"
            )

        report.append("\n")

        # Model Categories
        report.append("## Model Categories\n\n")

        free_models = [m for m in self.model_usage.keys() if ":free" in m]
        premium_models = [m for m in self.model_usage.keys() if ":free" not in m]

        report.append(f"### Free Tier Models ({len(free_models)})\n")
        report.append("OpenRouter free tier models available for fallback:\n\n")
        for model in sorted(free_models)[:20]:
            report.append(f"- `{model}`\n")
        if len(free_models) > 20:
            report.append(f"- ... and {len(free_models) - 20} more\n")
        report.append("\n")

        report.append(f"### Premium Models ({len(premium_models)})\n")
        report.append("Premium models available through OpenRouter:\n\n")
        for model in sorted(premium_models)[:20]:
            report.append(f"- `{model}`\n")
        if len(premium_models) > 20:
            report.append(f"- ... and {len(premium_models) - 20} more\n")
        report.append("\n")

        # Detailed Analysis
        report.append("## Detailed Analysis\n\n")
        report.append("### Model Variety\n")
        report.append(
            f"The system has access to {len(self.model_usage)} different models through OpenRouter.\n"
        )
        report.append(f"This provides excellent model variety for:\n")
        report.append(
            "- **Fallback Resilience:** If one model is unavailable, alternatives are available\n"
        )
        report.append(
            "- **Cost Optimization:** Free tier models can be used for non-critical requests\n"
        )
        report.append(
            "- **Quality Variation:** Different models for different use cases\n\n"
        )

        # Fallback Behavior
        report.append("### Fallback Behavior\n")
        if self.fallback_events:
            report.append(
                f"**Fallback events detected:** {len(self.fallback_events)}\n\n"
            )
            for event in self.fallback_events[:5]:
                report.append(f"- {event}\n")
            if len(self.fallback_events) > 5:
                report.append(f"- ... and {len(self.fallback_events) - 5} more\n")
        else:
            report.append("No fallback events detected in current logs.\n")
            report.append(
                "The system uses OpenRouter's automatic fallback mechanism:\n"
            )
            report.append("1. Primary model requested (e.g., `openrouter/free`)\n")
            report.append(
                "2. If unavailable, OpenRouter automatically selects an available model\n"
            )
            report.append("3. Response includes actual model used in metadata\n")
        report.append("\n")

        # Cost Implications
        report.append("### Cost Implications\n")
        report.append("**Free Tier Strategy:**\n")
        report.append(
            "- Using `openrouter/free` provides automatic access to free models\n"
        )
        report.append(f"- {len(free_models)} free tier models available for fallback\n")
        report.append("- Recommended for development and testing\n\n")

        report.append("**Premium Models:**\n")
        report.append(f"- {len(premium_models)} premium models available\n")
        report.append("- Use for production when higher quality is needed\n")
        report.append("- OpenRouter provides transparent pricing per model\n\n")

        # Recommendations
        report.append("## Recommendations\n\n")
        report.append(
            "1. **Monitor Model Usage:** Track which models are actually used via logs\n"
        )
        report.append(
            "2. **Optimize Costs:** Use free tier for non-critical requests\n"
        )
        report.append("3. **Test Fallbacks:** Verify fallback behavior under load\n")
        report.append(
            "4. **Document Outputs:** Capture sample outputs from different models\n"
        )
        report.append(
            "5. **Performance Tracking:** Monitor response times per model\n\n"
        )

        # Technical Details
        report.append("## Technical Details\n\n")
        report.append("### Configuration\n")
        report.append("```\n")
        report.append("LLM Provider: Custom (OpenRouter)\n")
        report.append("API Endpoint: https://openrouter.ai/api/v1\n")
        report.append("Model Selection: openrouter/free (with automatic fallback)\n")
        report.append("```\n\n")

        report.append("### Model Usage Tracking\n")
        report.append("The system logs actual model usage via:\n")
        report.append("- `[MODEL_USAGE]` log entries\n")
        report.append("- Response metadata containing `model` field\n")
        report.append("- Metrics stored in database for analysis\n\n")

        # ASCII Chart
        report.append(self.generate_ascii_chart())

        # Footer
        report.append("\n---\n")
        report.append("*Report generated by analyze_models.py*\n")
        report.append(f"*Analysis Date: {datetime.now().isoformat()}*\n")

        report_text = "".join(report)

        # Write to file
        with open(output_file, "w") as f:
            f.write(report_text)

        print(f"✓ Report generated: {output_file}")
        return report_text


def main():
    """Main entry point."""
    analyzer = ModelAnalyzer()

    print("=" * 80)
    print("PRESENTON MODEL DISTRIBUTION ANALYZER")
    print("=" * 80)
    print()

    print("Extracting logs from presenton container...")
    analyzer.analyze_openrouter_models()

    print(f"✓ Found {len(analyzer.model_usage)} models")
    print(
        f"✓ Total requests: {analyzer.total_requests if analyzer.total_requests > 0 else 'N/A'}"
    )
    print()

    # Generate report
    print("Generating model distribution report...")
    report = analyzer.generate_report("model_distribution_report.md")

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    top_models = analyzer.get_top_models(5)
    print("\nTop 5 Models:")
    for idx, (model, count, percentage) in enumerate(top_models, 1):
        print(f"  {idx}. {model}: {percentage:.2f}%")

    print(
        f"\nFree Tier Models: {len([m for m in analyzer.model_usage.keys() if ':free' in m])}"
    )
    print(
        f"Premium Models: {len([m for m in analyzer.model_usage.keys() if ':free' not in m])}"
    )

    print("\n✓ Analysis complete!")
    print("✓ Report saved to: model_distribution_report.md")
    print()


if __name__ == "__main__":
    main()
