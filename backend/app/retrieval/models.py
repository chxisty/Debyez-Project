"""
Hybrid Retrieval Data Models
Pydantic models for searchable chunks, scoring, rank fusion, and hybrid retrieval results.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RetrievalChunk(BaseModel):
    chunk_id: str
    text: str
    document_id: str
    filename: str
    page_number: int = 1
    section_name: Optional[str] = None
    cell_or_bbox: Optional[str] = None
    trust_tier: int = 2
    applicable_revision_start: Optional[str] = None
    applicable_revision_end: Optional[str] = None
    is_current: bool = True
    extraction_method: str = "pdf_native"
    verification_status: str = "VERIFIED"
    entity_references: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ScoredChunk(BaseModel):
    chunk: RetrievalChunk
    score: float
    rank: int
    channel: str  # 'exact_identifier', 'bm25', 'dense_semantic', 'structured_sql'

class FusedChunk(BaseModel):
    chunk: RetrievalChunk
    rrf_score: float
    channel_ranks: Dict[str, int] = Field(default_factory=dict)
    channel_scores: Dict[str, float] = Field(default_factory=dict)
    trust_multiplier: float = 1.0

class HybridRetrievalResult(BaseModel):
    query: str
    target_revision: Optional[str] = None
    identified_entities: List[str] = Field(default_factory=list)
    chunks: List[FusedChunk]
    structured_facts: List[Dict[str, Any]] = Field(default_factory=list)
    structured_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    structured_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    search_channels_used: List[str] = Field(default_factory=list)
    retrieval_notes: Optional[str] = None

