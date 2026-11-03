"""
Answer Generation Engine
Top-level coordinator combining Hybrid Retrieval, Grounded Answer Generation,
Citation Validation, and Deterministic Offline Fallback.
"""
from typing import Optional

from backend.app.retrieval.hybrid_router import HybridRouter
from backend.app.retrieval.models import HybridRetrievalResult
from backend.app.answer_generation.schema import GroundedAnswer
from backend.app.answer_generation.deterministic_generator import DeterministicGenerator
from backend.app.answer_generation.llm_adapters import LLMAdapter
from backend.app.answer_generation.citation_validator import CitationValidator

class AnswerEngine:
    def __init__(self, router: Optional[HybridRouter] = None):
        self.router = router or HybridRouter()

    def answer_question(
        self,
        query: str,
        target_revision: Optional[str] = None,
        force_offline: bool = False
    ) -> GroundedAnswer:
        """
        Executes hybrid retrieval, attempts LLM synthesis with citation audit,
        and falls back to deterministic offline generation if needed.
        """
        # 1. Execute Hybrid Retrieval
        retrieval: HybridRetrievalResult = self.router.search(
            query=query,
            target_revision=target_revision,
            top_k=25
        )

        answer: Optional[GroundedAnswer] = None

        # 2. Attempt LLM generation if allowed and configured
        if not force_offline and LLMAdapter.can_run():
            try:
                answer = LLMAdapter.generate_with_llm(retrieval)
            except Exception:
                answer = None

        # 3. Fallback to deterministic offline generator
        if answer is None:
            answer = DeterministicGenerator.generate(retrieval)

        # 4. Final Citation Audit Validation
        is_valid, valid_cits, rejections = CitationValidator.validate_answer_citations(answer, retrieval)
        answer.citations = valid_cits
        if rejections:
            answer.limitations_and_conflicts.extend(rejections)

        return answer

