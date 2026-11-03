"""
Dense Semantic Retriever
Real embedding generation and vector similarity search using BAAI/bge-small-en-v1.5 (384-dim ONNX).
"""
import numpy as np
from pathlib import Path
from typing import List, Optional
from fastembed import TextEmbedding

from backend.app.config import KNOWLEDGE_DIR
from backend.app.retrieval.models import RetrievalChunk, ScoredChunk

class DenseSemanticRetriever:
    def __init__(self, chunks: List[RetrievalChunk], model_name: str = "BAAI/bge-small-en-v1.5"):
        self.chunks = chunks
        self.model_name = model_name
        self.model = TextEmbedding(model_name)
        self.embeddings: Optional[np.ndarray] = None
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Generates or loads cached L2-normalized embeddings for all chunks."""
        cache_file = KNOWLEDGE_DIR / "chunk_embeddings.npy"
        
        # Check if cache exists and length matches
        if cache_file.exists():
            try:
                cached = np.load(cache_file)
                if cached.shape[0] == len(self.chunks):
                    self.embeddings = cached
                    return
            except Exception:
                pass

        # Compute embeddings using FastEmbed ONNX
        texts = [c.text for c in self.chunks]
        if not texts:
            self.embeddings = np.zeros((0, 384), dtype=np.float32)
            return

        raw_embeds = list(self.model.embed(texts))
        matrix = np.array(raw_embeds, dtype=np.float32)
        
        # L2-normalize vectors for exact cosine similarity via matrix dot product
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        self.embeddings = matrix / norms

        # Save to disk cache
        try:
            np.save(cache_file, self.embeddings)
        except Exception:
            pass

    def search(self, query: str, top_k: int = 15) -> List[ScoredChunk]:
        """Encodes query and computes cosine similarity ranking against corpus embeddings."""
        if self.embeddings is None or len(self.chunks) == 0 or not query.strip():
            return []

        # Generate and normalize query embedding
        q_embed = list(self.model.embed([query]))[0]
        q_vec = np.array(q_embed, dtype=np.float32)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec /= norm

        # Cosine similarity is dot product of normalized vectors
        scores = np.dot(self.embeddings, q_vec)
        ranked_indices = np.argsort(scores)[::-1][:top_k]

        results: List[ScoredChunk] = []
        rank = 1
        for idx in ranked_indices:
            score = float(scores[idx])
            results.append(ScoredChunk(
                chunk=self.chunks[idx],
                score=score,
                rank=rank,
                channel="dense_semantic"
            ))
            rank += 1

        return results

