"""
Retrieval over the 29 knowledge-base articles (Chroma + all-MiniLM-L6-v2). Satisfies A4.

- Articles are split by '## ' section so a query matches the relevant section, not a whole article.
- One passage per document is returned (best chunk), each carrying a real doc_id.
- Returning an empty list is valid: results below RETRIEVAL_MIN_SCORE are dropped.
"""
import json
import math
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
# Risk R-05 (stale documentation): an article not reviewed within this many days is never quoted to a customer;
# the ticket escalates instead. 0 disables the guard. The shipped corpus is a fresh snapshot (every article 0 days).
DOC_MAX_AGE_DAYS = int(os.getenv("DOC_MAX_AGE_DAYS", "180"))
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


# --------------------------------------------------------------------------- hybrid search
# The brief's low-level design calls for hybrid search: dense embeddings catch paraphrase, BM25 catches exact terms
# (error codes, flag names, product words). Both rank the same section chunks and are fused by reciprocal rank.
HYBRID = os.getenv("RETRIEVAL_HYBRID", "1") == "1"
RRF_K = 60
BM25_WEIGHT = float(os.getenv("RETRIEVAL_BM25_WEIGHT", "0.15"))   # keyword evidence relative to dense; chosen on development tickets only
_bm = {"ready": False, "ids": [], "tf": [], "dl": [], "df": {}, "avgdl": 1.0}
_STOP = set("a an and are as at be by for from has have i in is it its my of on or our that the this to was we with you your not but if so do does did can could would should will".split())


def _tok(text: str) -> list:
    return [w for w in re.findall(r"[a-z0-9_]+", (text or "").lower()) if w not in _STOP and len(w) > 1]


def _build_bm25(col) -> None:
    got = col.get(include=["documents"])
    _bm.update(ids=list(got["ids"]), tf=[], dl=[], df={})
    for doc in got["documents"]:
        toks = _tok(doc)
        tf = {}
        for w in toks:
            tf[w] = tf.get(w, 0) + 1
        _bm["tf"].append(tf)
        _bm["dl"].append(len(toks))
        for w in tf:
            _bm["df"][w] = _bm["df"].get(w, 0) + 1
    _bm["avgdl"] = (sum(_bm["dl"]) / len(_bm["dl"])) if _bm["dl"] else 1.0
    _bm["ready"] = True


def _bm25_scores(col, query: str, k1: float = 1.5, b: float = 0.75) -> dict:
    """BM25 score per chunk id (Robertson-Sparck Jones idf with +1 so it is never negative)."""
    if not _bm["ready"]:
        _build_bm25(col)
    n = len(_bm["ids"])
    out = {}
    q = set(_tok(query))
    for cid, tf, dl in zip(_bm["ids"], _bm["tf"], _bm["dl"]):
        sc = 0.0
        for w in q:
            f = tf.get(w)
            if not f:
                continue
            df = _bm["df"][w]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            sc += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / _bm["avgdl"]))
        out[cid] = sc
    return out


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
    total = max(col.count(), 1)
    res = col.query(query_texts=[query], n_results=total if HYBRID else min(top_k * 4, total))
    ids, docs, metas, dists = res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
    fused = {}
    if HYBRID:
        bm = _bm25_scores(col, query)
        dense_rank = {cid: i for i, cid in enumerate(ids)}                      # already best-first by cosine
        bm_order = sorted(bm, key=lambda c: -bm[c])
        bm_rank = {cid: i for i, cid in enumerate(bm_order) if bm[cid] > 0}
        for cid in ids:
            fused[cid] = 1.0 / (RRF_K + dense_rank[cid]) + BM25_WEIGHT * (1.0 / (RRF_K + bm_rank[cid]) if cid in bm_rank else 0.0)
    best = {}
    for cid, text, meta, dist in zip(ids, docs, metas, dists):
        score = round(1.0 - float(dist), 4)
        did = meta["doc_id"]
        key = fused.get(cid, score)                                              # hybrid rank score, else cosine
        if did not in best or key > best[did]["_key"]:
            best[did] = {"doc_id": did, "title": meta["title"], "passage": text, "score": score, "_key": key,
                         "full_text": _articles().get(did, text),
                         "category": meta.get("category", ""),
                         "last_reviewed_days_ago": meta.get("last_reviewed_days_ago", 0)}
    ranked = sorted(best.values(), key=lambda p: -p["_key"])
    for p in ranked:
        p.pop("_key", None)
    max_age = DOC_MAX_AGE_DAYS
    fresh = [p for p in ranked if not max_age or int(p.get("last_reviewed_days_ago") or 0) <= max_age]
    return [p for p in fresh if p["score"] >= floor][:top_k]
