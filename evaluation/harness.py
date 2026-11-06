#!/usr/bin/env python3
"""
Evaluation harness — processes a full ticket set unattended and outputs a metrics report.
Satisfies acceptance criteria: A9 (processes full evaluation set in single unattended run)
                               A10 (produces metrics report automatically)

CRITICAL: This harness MUST accept --input and --output path arguments.
It will be pointed at a hidden 120-ticket evaluation set you have never seen.
Hardcoded file paths = A9 failure.

Usage:
    python evaluation/harness.py \\
        --input data/validation_tickets.json \\
        --output evaluation/results/run_001.json

    python evaluation/harness.py \\
        --input data/development_tickets.json \\
        --output evaluation/results/dev_run.json \\
        --max-tickets 50 --verbose
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

# Add project root to path so src imports work from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CloudServe Support System — Evaluation Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluation/harness.py --input data/validation_tickets.json --output evaluation/results/run_001.json
  python evaluation/harness.py --input data/development_tickets.json --output evaluation/results/dev_run.json
        """,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input tickets JSON file (required)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output results JSON file (required)",
    )
    parser.add_argument(
        "--max-tickets",
        type=int,
        default=None,
        help="Maximum number of tickets to process (default: all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-ticket progress",
    )
    return parser.parse_args()


def load_tickets(input_path: str) -> list:
    """
    Load tickets from a JSON file.

    Raises:
        FileNotFoundError: If the path does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, "r") as f:
        tickets = json.load(f)
    print(f"Loaded {len(tickets)} tickets from {input_path}")
    return tickets


def process_ticket(ticket: dict) -> dict:
    """
    Process a single ticket through the full pipeline.

    Returns a result dict. NEVER raises — catches all exceptions and records them.
    This ensures A9: the harness processes ALL tickets even if individual ones fail.

    TODO: Wire up the real pipeline in Week 2 Day 5.
          Replace the stub below with:
            normalized     = ingest.normalize_ticket(ticket, ticket['channel'])
            classification = classify.classify_ticket(normalized)
            passages       = retrieve.retrieve_passages(normalized['body'])
            routing        = route.route_ticket(normalized, classification, passages)
            if routing['decision'] == 'auto_respond':
                response       = generate.generate_response(normalized, passages, classification)
                guardrail_result = guardrails.run_guardrails(response, normalized, passages, routing)
            logging_store.log_decision({...})
    """
    result = {
        "ticket_id": ticket.get("ticket_id", "unknown"),
        "channel": ticket.get("channel", "unknown"),
        # Will be 'success', 'escalated', or 'error' once pipeline is implemented
        "status": "stub",
        "decision": None,
        "intent_predicted": None,
        "confidence": None,
        "response_text": None,
        "citations": [],
        "decision_id": None,
        "processing_time_ms": 0,
        "error": "Pipeline not yet implemented — complete in Week 2 Day 5",
        # Ground truth fields for evaluation scoring
        "intent_actual": ticket.get("labels", {}).get("intent"),
        "expected_route": ticket.get("labels", {}).get("expected_route"),
        "answerable_from_docs": ticket.get("labels", {}).get("answerable_from_docs"),
    }
    return result


def compute_metrics(results: list) -> dict:
    """
    Compute all evaluation metrics from the results list.

    TODO: Implement full metrics in Week 2 Day 5.

    Required metrics (with targets):
    - Intent classification precision per class          target: ≥85%
    - Routing accuracy (auto_respond vs escalate)        target: measured
    - Hallucination rate (50+ responses, 2 assessors)   target: ≤5%
    - Citation accuracy                                  target: ≥95%
    - 95th-percentile response latency                   target: <3s
    - Confidence calibration per band                    target: within 5pp
    - Business outcomes: FCR, escalation rate, CSAT proxy
    """
    total = len(results)
    errors = sum(1 for r in results if r.get("status") == "error")
    stubs = sum(1 for r in results if r.get("status") == "stub")

    return {
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "total_tickets": total,
        "processed_successfully": total - errors,
        "errors": errors,
        "stubs_not_yet_implemented": stubs,
        "metrics": {
            "_note": "Full metrics not yet implemented — complete in Week 2 Day 5",
            "intent_classification_precision": None,   # target: ≥85%
            "routing_accuracy": None,
            "hallucination_rate": None,                # target: ≤5%
            "citation_accuracy": None,                 # target: ≥95%
            "latency_p95_ms": None,                    # target: <3000
            "confidence_calibration": {
                "_note": "Group predictions by confidence band, check accuracy per band",
                "0.5_0.6": None,
                "0.6_0.7": None,
                "0.7_0.8": None,
                "0.8_0.9": None,
                "0.9_1.0": None,
            },
        },
        "business_outcomes": {
            "_note": "Compute after pipeline is implemented",
            "first_contact_resolution_rate": None,     # baseline 42%, target ≥60%
            "escalation_rate": None,                   # baseline 58%, target ≤30%
            "auto_respond_rate": None,
        },
        "governance": {
            "pii_violations": None,                    # target: 0
            "guardrail_activations": None,
            "decisions_logged": None,
            "decisions_reconciled": None,              # should equal total_tickets
        },
    }


def save_results(results: list, metrics: dict, output_path: str) -> None:
    """Save results and metrics to the output JSON file."""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    output = {
        "metrics": metrics,
        "results": results,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"Results saved to {output_path}")


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("CloudServe Support System — Evaluation Harness")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print("=" * 60)

    # Load tickets
    tickets = load_tickets(args.input)
    if args.max_tickets:
        tickets = tickets[: args.max_tickets]
        print(f"Processing first {len(tickets)} tickets (--max-tickets)")

    # Process all tickets — A9 requires no intervention, no skipping
    results = []
    start_time = time.time()

    for i, ticket in enumerate(tickets):
        ticket_start = time.time()
        try:
            result = process_ticket(ticket)
        except Exception as e:
            # A9: never let an individual ticket crash the harness
            result = {
                "ticket_id": ticket.get("ticket_id", f"unknown_{i}"),
                "status": "error",
                "error": str(e),
                "decision": None,
                "intent_predicted": None,
                "confidence": None,
                "citations": [],
            }

        result["processing_time_ms"] = int((time.time() - ticket_start) * 1000)
        results.append(result)

        if args.verbose or (i + 1) % 10 == 0:
            status = result.get("status", "unknown")
            print(f"  [{i+1:3d}/{len(tickets)}] {result['ticket_id']} → {status}")

    total_time = time.time() - start_time
    print(f"\nProcessed {len(results)} tickets in {total_time:.1f}s")

    # Compute and print metrics
    metrics = compute_metrics(results)
    metrics["total_processing_time_seconds"] = round(total_time, 2)

    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)
    print(f"Total tickets:  {metrics['total_tickets']}")
    print(f"Successful:     {metrics['processed_successfully']}")
    print(f"Errors:         {metrics['errors']}")
    print(f"Total time:     {total_time:.1f}s")
    print("=" * 60)

    # Save results
    save_results(results, metrics, args.output)

    # Exit 0 if no errors, 1 if any tickets errored
    sys.exit(1 if metrics["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
