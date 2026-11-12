"""
Retrieval over the 29 knowledge-base articles (Chroma + all-MiniLM-L6-v2). Satisfies A4.

- Articles are split by '## ' section so a query matches the relevant section, not a whole article.
- One passage per document is returned (best chunk), each carrying a real doc_id.
- Returning an empty list is valid: results below RETRIEVAL_MIN_SCORE are dropped.
"""
import json
import os
import re
from typing import Optional

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")  # chromadb telemetry is noisy and unneeded

import logging

import chromadb
from chromadb.config import Settings

logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
from chromadb.utils import embedding_functions

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.join(ROOT, "storage", "chroma"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
MIN_SCORE = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.30"))  # chosen from evaluation/eval_retrieval.py
DOC_COLLECTION = "kb_articles"
DEFAULT_DOCS = os.path.join(ROOT, "data", "documentation.json")

_cache = {"client": None, "ef": None, "docs": None}


def _articles() -> dict:
    """doc_id -> full article text (used so the model sees the whole article, not one section)."""
    if _cache["docs"] is None:
        with open(DEFAULT_DOCS, "r", encoding="utf-8") as f:
            _cache["docs"] = {d["doc_id"]: d["content"] for d in json.load(f)}
    return _cache["docs"]


def _ef():
    if _cache["ef"] is None:
        _cache["ef"] = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _cache["ef"]


def get_client():
    if _cache["client"] is None:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        _cache["client"] = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
    return _cache["client"]


def chunk_document(doc: dict) -> list:
    """Split one article into section chunks, each prefixed with the article title."""
    content = doc.get("content", "")
    parts = re.split(r"\n(?=## )", content)
    chunks = []
    for part in parts:
        part = part.strip()
        if len(part) < 60:
            continue
        chunks.append(f"{doc['title']}\n{part}")
    return chunks or [f"{doc['title']}\n{content}"]


def embed_corpus(documentation_path: Optional[str] = None) -> int:
    """(Re)build the vector store from documentation.json. Idempotent. Returns chunk count."""
    path = documentation_path or DEFAULT_DOCS
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    client = get_client()
    try:
        client.delete_collection(DOC_COLLECTION)
    except Exception:
        pass
    col = client.create_collection(DOC_COLLECTION, embedding_function=_ef(), metadata={"hnsw:space": "cosine"})

    ids, texts, metas = [], [], []
    for doc in docs:
        for i, chunk in enumerate(chunk_document(doc)):
            ids.append(f"{doc['doc_id']}::{i}")
            texts.append(chunk)
            try:
                age = int(doc.get("last_reviewed_days_ago", 0))
            except (TypeError, ValueError):
                age = 0
            metas.append({"doc_id": doc["doc_id"], "title": doc["title"], "category": doc.get("category", ""),
                          "last_reviewed_days_ago": age})
    col.add(ids=ids, documents=texts, metadatas=metas)
    return len(ids)


def ensure_corpus() -> None:
    """Build the store on first use so a clean checkout needs no manual step."""
    client = get_client()
    try:
        col = client.get_collection(DOC_COLLECTION, embedding_function=_ef())
        if col.count() > 0:
            return
    except Exception:
        pass
    embed_corpus()


def retrieve_passages(query: str, top_k: int = DEFAULT_TOP_K, min_score: Optional[float] = None) -> list:
    """
    Return up to top_k passages: [{doc_id, title, passage, score, category}], best first.
    Returns [] when nothing clears the relevance floor (this is a valid, often correct, result).
    """
    if not query or not query.strip():
        return []
    ensure_corpus()
    floor = MIN_SCORE if min_score is None else min_score
    col = get_client().get_collection(DOC_COLLECTION, embedding_function=_ef())
    res = col.query(query_texts=[query], n_results=min(top_k * 4, max(col.count(), 1)))

    best = {}
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        score = round(1.0 - float(dist), 4)
        did = meta["doc_id"]
        if did not in best or score > best[did]["score"]:
            best[did] = {"doc_id": did, "title": meta["title"], "passage": text, "score": score,
                         "full_text": _articles().get(did, text),
                         "category": meta.get("category", ""),
                         "last_reviewed_days_ago": meta.get("last_reviewed_days_ago", 0)}
    ranked = sorted(best.values(), key=lambda p: -p["score"])
    return [p for p in ranked if p["score"] >= floor][:top_k]
