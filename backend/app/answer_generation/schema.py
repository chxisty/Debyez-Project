"""
Answer Generation Schema
Structured Pydantic models for evidence citations, abstention taxonomy, and grounded answers.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class AbstentionCategory(str, Enum):
    NONE = "NONE"
    GENUINELY_ABSENT = "GENUINELY_ABSENT"
    FALSE_PREMISE = "FALSE_PREMISE"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    OMITTED_COMPANION_DOCUMENT = "OMITTED_COMPANION_DOCUMENT"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    INSUFFICIENT_RETRIEVAL_EVIDENCE = "INSUFFICIENT_RETRIEVAL_EVIDENCE"

class EvidenceCitation(BaseModel):
    chunk_id: str
    source_document: str
    page_number: int = 1
    section_or_cell: Optional[str] = None
    quoted_evidence: str
    applicable_revision: Optional[str] = None
    trust_tier: int = 2
    verification_status: str = "VERIFIED"

class GroundedAnswer(BaseModel):
    question_id: Optional[str] = None
    question: str
    direct_answer: str
    supporting_claims: List[str] = Field(default_factory=list)
    citations: List[EvidenceCitation] = Field(default_factory=list)
    applicable_revision: str = "Current (SW >= 3.2)"
    verification_status: str = "VERIFIED"  # 'VERIFIED', 'PARTIALLY VERIFIED', 'NOT FOUND', 'CONFLICTING'
    abstention_category: AbstentionCategory = AbstentionCategory.NONE
    abstention_explanation: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_justification: str
    limitations_and_conflicts: List[str] = Field(default_factory=list)
    generation_method: str = "deterministic_offline"  # 'deterministic_offline', 'groq_llm', 'openai_llm'

