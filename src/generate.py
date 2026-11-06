"""
Generation module — drafts grounded answers with citations using LangChain/LangGraph.
Satisfies acceptance criteria: A6 (generated answers carry citations that resolve
to actually-retrieved passages)

CRITICAL: Citations must map to passages actually returned by the retrieval layer.
Never generate plausible-looking references to documents that were not retrieved.
If passages is empty, raise ValueError — do not attempt generation without grounding.
"""
import os
from typing import Optional

MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")


def generate_response(
    ticket: dict,
    passages: list[dict],
    classification: dict,
    prompt_version: str = "PR-GN-01 v1.0",
) -> dict:
    """
    Generate a grounded response to a ticket using retrieved passages.

    Args:
        ticket: Normalised ticket dict
        passages: Retrieved passages from retrieve.retrieve_passages() — MUST be non-empty
        classification: Classification result (for context and tone)
        prompt_version: Version of the generation prompt used

    Returns:
        Response dict with keys:
        - answer (str): The drafted response text
        - citations (list): List of {doc_id, passage_excerpt} dicts.
                            Each citation MUST map to a passage in the passages arg.
        - model_used (str): Model name used
        - prompt_version (str): Prompt version used
        - token_count (int): Approximate token usage (for cost monitoring in logs)

    Raises:
        ValueError: If passages is empty. Cannot generate a grounded response
                    without retrieved context. Caller should escalate instead.
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    if not passages:
        raise ValueError(
            "Cannot generate response without retrieved passages. "
            "Route to escalate instead of calling generate_response with empty passages."
        )
    raise NotImplementedError("TODO: implement generate_response() - Week 2 Day 4")
