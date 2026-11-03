"""
BM25 Keyword Retriever
Sparse lexical search engine using Rank-BM25 over indexed technical documentation and IKR chunks.
"""
import re
from typing import List
from rank_bm25 import BM25Okapi

from backend.app.retrieval.models import RetrievalChunk, ScoredChunk

class BM25Retriever:
    def __init__(self, chunks: List[RetrievalChunk]):
        self.chunks = chunks
        self.corpus_tokens = [self.tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Punctuation-preserving tokenizer for technical industrial text."""
        if not text:
            return []
        # Keep hyphenated codes like PS-04A, IV-21, PLC-03 intact while splitting punctuation
        tokens = re.findall(r"[A-Za-z0-9]+(?:[\-_][A-Za-z0-9]+)*", text.lower())
        return tokens

    def search(self, query: str, top_k: int = 15) -> List[ScoredChunk]:
        """Performs BM25 search and returns top-k scored chunks."""
        if not self.bm25 or not query.strip():
            return []

        q_tokens = self.tokenize(query)
        if not q_tokens:
            return []

        scores = self.bm25.get_scores(q_tokens)
        scored_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results: List[ScoredChunk] = []
        rank = 1
        for idx in scored_indices[:top_k]:
            score = float(scores[idx])
            if score <= 0.0:
                continue
            results.append(ScoredChunk(
                chunk=self.chunks[idx],
                score=score,
                rank=rank,
                channel="bm25"
            ))
            rank += 1

        return results

