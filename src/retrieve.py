"""
Retrieval module — embeds documentation corpus into Chroma and retrieves relevant passages.
Satisfies acceptance criteria: A4 (retrieval runs against documentation corpus,
returned sources resolve to real passages)

IMPORTANT: Returning an empty list is valid and often correct when no article is
relevant. Never return plausible-but-irrelevant passages to avoid having empty results.
Returning nothing and escalating is better than returning irrelevant context.
"""
import os
from typing import Optional

CHROMA_PATH = os.getenv("CHROMA_PATH", "./storage/chroma")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))


def embed_corpus(documentation_path: str = "data/documentation.json") -> None:
    """
    Load documentation.json and embed all 29 articles into the Chroma vector store.
    Must be idempotent — safe to run multiple times without creating duplicates.

    Args:
        documentation_path: Path to documentation.json

    Raises:
        FileNotFoundError: If documentation_path does not exist
        NotImplementedError: Until implemented in Week 2 Day 2
    """
    raise NotImplementedError("TODO: implement embed_corpus() - Week 2 Day 2")


def retrieve_passages(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Search the Chroma vector store for passages relevant to the query.

    Args:
        query: The search query (typically the ticket body or subject)
        top_k: Maximum number of passages to return

    Returns:
        List of passage dicts, each containing:
        - doc_id (str): ID of source document (e.g. 'DOC-AUTH-001')
        - title (str): Document title
        - passage (str): Relevant text excerpt
        - score (float): Similarity score 0.0-1.0
        - category (str): Document category

        Returns empty list [] if no relevant passages found. This IS valid behaviour.
        The caller (route.py) handles the empty case by escalating.

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 2
    """
    raise NotImplementedError("TODO: implement retrieve_passages() - Week 2 Day 2")
