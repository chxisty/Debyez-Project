"""
Hybrid Retrieval Router & Reciprocal Rank Fusion (RRF) Engine
Combines exact identifier matching, structured SQL, BM25 keyword search, and dense semantic embeddings.
Applies source-trust weighting and revision-aware temporal filtering.
"""
import re
from typing import List, Optional, Dict, Tuple
from collections import defaultdict

from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.retrieval.models import RetrievalChunk, ScoredChunk, FusedChunk, HybridRetrievalResult
from backend.app.retrieval.chunk_indexer import ChunkIndexer
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseSemanticRetriever
from backend.app.retrieval.structured_retriever import StructuredRetriever
from backend.app.conflict_detection.revision_engine import RevisionEngine

class HybridRouter:
    # Source Trust Tier Weight Multipliers (Preserves lower-tier relevance while maintaining hierarchy)
    TRUST_WEIGHTS = {
        1: 1.00,  # Tier 1 Master / ECN
        2: 0.98,  # Tier 2 Official Manuals & Drawings
        3: 0.95,  # Tier 3 Operational HMI & Training
        4: 0.90,  # Tier 4 Legacy Manuals
        5: 0.85,  # Tier 5 Informal Field Notes
        6: 0.40   # Tier 6 Noise (MSDS)
    }

    # Channel weights for RRF (structured facts for identified entities receive strong weighting)
    CHANNEL_WEIGHTS = {
        "structured_sql": 2.50,
        "dense_semantic": 1.00,
        "bm25": 1.00
    }

    def __init__(self, db: Optional[KnowledgeDatabase] = None):
        self.db = db or KnowledgeDatabase()
        self.chunks = ChunkIndexer.load_chunks()
        self.bm25 = BM25Retriever(self.chunks)
        self.dense = DenseSemanticRetriever(self.chunks)
        self.structured = StructuredRetriever(self.db)

    def detect_revision_context(self, query: str) -> Optional[str]:
        """Infers requested software revision from query phrasing."""
        q_lower = query.lower()
        if "before" in q_lower and ("3.2" in q_lower or "sw 3.2" in q_lower or "rev 3.2" in q_lower):
            return "3.0"
        if "prior to" in q_lower and "3.2" in q_lower:
            return "3.0"
        if "historical" in q_lower and ("pressure" in q_lower or "threshold" in q_lower):
            return "3.0"
        if "3.0" in q_lower:
            return "3.0"
        if "3.1" in q_lower:
            return "3.1"
        if "3.2.1" in q_lower:
            return "3.2.1"
        if "3.2" in q_lower or "current" in q_lower or "present" in q_lower:
            return "3.2"
        return None

    def search(
        self,
        query: str,
        target_revision: Optional[str] = None,
        top_k: int = 10
    ) -> HybridRetrievalResult:
        """
        Executes multi-channel retrieval, applies Reciprocal Rank Fusion,
        and enforces source trust and revision constraints.
        """
        if target_revision is None:
            target_revision = self.detect_revision_context(query)

        # 1. Detect mentioned entities
        entities = self.structured.search_entities(query)

        # 2. Channel 1: Structured SQL retrieval
        structured_chunks = self.structured.search_as_chunks(entities, target_revision, query=query)
        structured_raw = self.structured.retrieve_structured_data(entities, target_revision)

        # 3. Channel 2: BM25 Sparse Keyword Retrieval
        bm25_chunks = self.bm25.search(query, top_k=25)

        # 4. Channel 3: Dense Semantic Retrieval (BAAI/bge-small-en-v1.5)
        dense_chunks = self.dense.search(query, top_k=25)

        # 5. False-Friend Protection Filtering:
        # If query specifically mentions PS-40, remove PS-04 and PS-04A chunks unless query also mentions them.
        if "PS-40" in entities and "PS-04" not in entities and "PS-04A" not in entities:
            bm25_chunks = [c for c in bm25_chunks if "PS-04" not in c.chunk.entity_references]
            dense_chunks = [c for c in dense_chunks if "PS-04" not in c.chunk.entity_references]

        # 6. Reciprocal Rank Fusion (RRF) with Trust Weighting
        fused_map: Dict[str, FusedChunk] = {}
        all_channel_chunks = [
            ("structured_sql", structured_chunks),
            ("bm25", bm25_chunks),
            ("dense_semantic", dense_chunks)
        ]

        k_rrf = 60  # Standard RRF smoothing constant

        for channel_name, scored_list in all_channel_chunks:
            w_channel = self.CHANNEL_WEIGHTS.get(channel_name, 1.0)
            for item in scored_list:
                cid = item.chunk.chunk_id
                t_weight = self.TRUST_WEIGHTS.get(item.chunk.trust_tier, 0.5)

                if cid not in fused_map:
                    fused_map[cid] = FusedChunk(
                        chunk=item.chunk,
                        rrf_score=0.0,
                        channel_ranks={},
                        channel_scores={},
                        trust_multiplier=t_weight
                    )

                fused = fused_map[cid]
                fused.channel_ranks[channel_name] = item.rank
                fused.channel_scores[channel_name] = item.score

                # RRF addition formula: w_channel * (1 / (k + rank)) * trust_multiplier
                fused.rrf_score += (w_channel * (1.0 / (k_rrf + item.rank))) * t_weight

        # 7. Revision-aware post-filtering:
        # If target revision is specified, filter out chunks that strictly belong to non-applicable revisions.
        final_chunks: List[FusedChunk] = []
        for fused in fused_map.values():
            chk = fused.chunk
            if target_revision and (chk.applicable_revision_start or chk.applicable_revision_end):
                # Verify applicability
                from backend.app.knowledge.schema import FactEntity, ProvenanceRecord
                dummy_fact = FactEntity(
                    fact_id="TMP",
                    subject="TMP",
                    predicate="TMP",
                    object_value="TMP",
                    applicable_revision_start=chk.applicable_revision_start,
                    applicable_revision_end=chk.applicable_revision_end,
                    is_current=chk.is_current,
                    provenance=ProvenanceRecord(source_document=chk.filename)
                )
                if not RevisionEngine.is_fact_applicable(dummy_fact, target_revision):
                    continue

            final_chunks.append(fused)

        # Sort by RRF score descending
        final_chunks.sort(key=lambda x: x.rrf_score, reverse=True)

        return HybridRetrievalResult(
            query=query,
            target_revision=target_revision,
            identified_entities=entities,
            chunks=final_chunks[:top_k],
            structured_facts=[f.model_dump() for f in structured_raw["facts"]],
            structured_relationships=[r.model_dump() for r in structured_raw["relationships"]],
            structured_conflicts=[c.model_dump() for c in structured_raw["conflicts"]],
            search_channels_used=["structured_sql", "bm25", "dense_semantic"],
            retrieval_notes=f"Identified entities: {entities}; Target revision: {target_revision or 'Current/Unspecified'}"
        )

