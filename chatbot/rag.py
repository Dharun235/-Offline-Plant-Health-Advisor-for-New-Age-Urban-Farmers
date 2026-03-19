"""
Simple local retrieval for agriculture guidance.

This module intentionally avoids heavy dependencies and works fully offline.
Corpus format: JSONL with at least a `text` field.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
import math
from pathlib import Path
import re
from typing import Any

from config import RAG_CORPUS_PATH

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class LocalBM25Retriever:
    def __init__(self, corpus_path: str) -> None:
        self.corpus_path = Path(corpus_path).expanduser().resolve()
        self.docs: list[dict[str, Any]] = []
        self.term_freqs: list[Counter[str]] = []
        self.doc_lens: list[int] = []
        self.doc_freq: Counter[str] = Counter()
        self.avgdl = 1.0

        self._load()

    def _load(self) -> None:
        if not self.corpus_path.exists():
            return

        for line in self.corpus_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = str(row.get("text", "")).strip()
            if not text:
                continue

            title = str(row.get("title", "")).strip()
            source = str(row.get("source", "")).strip()
            content = f"{title}\n{text}".strip()
            tokens = _tokenize(content)
            if not tokens:
                continue

            tf = Counter(tokens)
            self.docs.append({
                "title": title,
                "text": text,
                "source": source,
            })
            self.term_freqs.append(tf)
            self.doc_lens.append(len(tokens))
            for term in tf.keys():
                self.doc_freq[term] += 1

        if self.doc_lens:
            self.avgdl = sum(self.doc_lens) / len(self.doc_lens)

    def available(self) -> bool:
        return bool(self.docs)

    def _score(self, query_tokens: list[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        tf = self.term_freqs[doc_idx]
        dl = self.doc_lens[doc_idx]
        n_docs = len(self.docs)

        score = 0.0
        for term in query_tokens:
            freq = tf.get(term, 0)
            if freq == 0:
                continue
            df = self.doc_freq.get(term, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            denom = freq + k1 * (1 - b + b * (dl / self.avgdl))
            score += idf * (freq * (k1 + 1) / denom)
        return score

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if not self.docs:
            return []

        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        scored: list[tuple[float, int]] = []
        for i in range(len(self.docs)):
            s = self._score(q_tokens, i)
            if s > 0:
                scored.append((s, i))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [self.docs[i] for _, i in scored[:max(1, top_k)]]


@lru_cache(maxsize=1)
def _get_retriever() -> LocalBM25Retriever:
    return LocalBM25Retriever(RAG_CORPUS_PATH)


def get_rag_context(query: str, top_k: int = 3, max_chars: int = 1600) -> str:
    retriever = _get_retriever()
    if not retriever.available():
        return ""

    docs = retriever.retrieve(query=query, top_k=top_k)
    if not docs:
        return ""

    parts: list[str] = []
    total = 0
    for idx, d in enumerate(docs, start=1):
        title = d.get("title") or f"Reference {idx}"
        source = d.get("source") or "local"
        text = str(d.get("text", "")).strip()
        if not text:
            continue
        block = f"[{idx}] {title} ({source})\n{text}"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)

    return "\n\n".join(parts)
