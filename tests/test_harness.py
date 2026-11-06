"""
Tests for the evaluation harness CLI contract.

These verify the harness:
- Accepts --input and --output arguments
- Runs without crashing on real data
- Produces valid JSON output

These tests PASS immediately — the harness stub is fully wired from day one.
"""
import json
import os
import subprocess
import sys
import tempfile

import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(PROJECT_ROOT, "evaluation", "harness.py")
VALIDATION_TICKETS = os.path.join(PROJECT_ROOT, "data", "validation_tickets.json")


class TestHarnessCLI:
    """Tests that the harness CLI contract is correct from day one."""

    def test_harness_script_exists(self):
        """The harness script must exist at evaluation/harness.py."""
        assert os.path.exists(HARNESS), f"harness.py not found at {HARNESS}"

    def test_validation_tickets_exist(self):
        """The validation dataset must be present in data/."""
        assert os.path.exists(VALIDATION_TICKETS), (
            f"validation_tickets.json not found at {VALIDATION_TICKETS}"
        )

    def test_harness_fails_without_input_arg(self):
        """Harness should exit non-zero if --input is missing."""
        result = subprocess.run(
            [sys.executable, HARNESS, "--output", "/tmp/test_no_input.json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode != 0, (
            "Harness should fail when --input argument is not provided"
        )

    def test_harness_fails_without_output_arg(self):
        """Harness should exit non-zero if --output is missing."""
        result = subprocess.run(
            [sys.executable, HARNESS, "--input", VALIDATION_TICKETS],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode != 0, (
            "Harness should fail when --output argument is not provided"
        )

    def test_harness_runs_on_validation_set(self):
        """Harness must run on validation_tickets.json without crashing."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, dir="/tmp"
        ) as f:
            output_path = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable, HARNESS,
                    "--input", VALIDATION_TICKETS,
                    "--output", output_path,
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=120,
            )
            # No unhandled exception
            assert "Traceback" not in result.stderr, (
                f"Harness crashed with unhandled exception:\n{result.stderr}"
            )
            # Output file must be created
            assert os.path.exists(output_path), "Output file was not created"
            # Output must be valid JSON
            with open(output_path) as f:
                output = json.load(f)
            assert "metrics" in output, "Output JSON missing 'metrics' key"
            assert "results" in output, "Output JSON missing 'results' key"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_harness_output_has_required_structure(self):
        """Output JSON must contain metrics with total_tickets and results list."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, dir="/tmp"
        ) as f:
            output_path = f.name

        try:
            subprocess.run(
                [
                    sys.executable, HARNESS,
                    "--input", VALIDATION_TICKETS,
                    "--output", output_path,
                    "--max-tickets", "5",
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=60,
            )
            with open(output_path) as f:
                output = json.load(f)

            assert "metrics" in output
            assert "results" in output
            assert "total_tickets" in output["metrics"]
            assert isinstance(output["results"], list)
            # With --max-tickets 5, should have 5 results
            assert len(output["results"]) == 5
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_harness_processes_all_tickets_without_stopping(self):
        """Harness must process all tickets even when individual ones fail."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, dir="/tmp"
        ) as f:
            output_path = f.name

        try:
            subprocess.run(
                [
                    sys.executable, HARNESS,
                    "--input", VALIDATION_TICKETS,
                    "--output", output_path,
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=120,
            )
            with open(output_path) as f:
                output = json.load(f)

            # All 80 validation tickets should be in results (not stopped early)
            assert len(output["results"]) == output["metrics"]["total_tickets"]
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_each_result_has_ticket_id(self):
        """Each result in the output must have a ticket_id field."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, dir="/tmp"
        ) as f:
            output_path = f.name

        try:
            subprocess.run(
                [
                    sys.executable, HARNESS,
                    "--input", VALIDATION_TICKETS,
                    "--output", output_path,
                    "--max-tickets", "10",
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=60,
            )
            with open(output_path) as f:
                output = json.load(f)

            for result in output["results"]:
                assert "ticket_id" in result, (
                    f"Result missing ticket_id: {result}"
                )
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
