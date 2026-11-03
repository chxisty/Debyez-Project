"""
Automated Test Suite for Phase 4 & Phase 5
Hybrid Retrieval Pipeline, Dense Semantic Search, Reciprocal Rank Fusion,
Evidence-Grounded Answer Generation, Citation Validation, and Epistemic Abstention.
"""
import pytest
from typing import List

from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.retrieval.models import RetrievalChunk, ScoredChunk, HybridRetrievalResult
from backend.app.retrieval.chunk_indexer import ChunkIndexer
from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.dense_retriever import DenseSemanticRetriever
from backend.app.retrieval.structured_retriever import StructuredRetriever
from backend.app.retrieval.hybrid_router import HybridRouter
from backend.app.answer_generation.schema import GroundedAnswer, EvidenceCitation, AbstentionCategory
from backend.app.answer_generation.citation_validator import CitationValidator
from backend.app.answer_generation.deterministic_generator import DeterministicGenerator
from backend.app.answer_generation.engine import AnswerEngine

@pytest.fixture(scope="module")
def hybrid_router():
    """Initializes and returns shared HybridRouter instance."""
    db = KnowledgeDatabase()
    return HybridRouter(db)

@pytest.fixture(scope="module")
def answer_engine(hybrid_router):
    """Initializes and returns shared AnswerEngine instance."""
    return AnswerEngine(hybrid_router)

# 1. EXACT IDENTIFIER RETRIEVAL
def test_exact_identifier_retrieval(hybrid_router):
    # PS-04A
    res_ps04a = hybrid_router.search("What is sensor PS-04A and what does it report?")
    assert "PS-04A" in res_ps04a.identified_entities
    assert any("PS-04A" in fc.chunk.text for fc in res_ps04a.chunks)

    # IV-21
    res_iv21 = hybrid_router.search("What is the location of IV-21?")
    assert "IV-21" in res_iv21.identified_entities
    assert any("Hydraulic Module" in fc.chunk.text for fc in res_iv21.chunks)

    # A17
    res_a17 = hybrid_router.search("What is alarm A17 threshold?")
    assert "A17" in res_a17.identified_entities
    assert any("150 bar" in fc.chunk.text for fc in res_a17.chunks)

    # PLC-03
    res_plc = hybrid_router.search("What does controller PLC-03 do?")
    assert "PLC-03" in res_plc.identified_entities
    assert any("HCS Controller" in fc.chunk.text or "PLC-03" in fc.chunk.text for fc in res_plc.chunks)

# 2. ALIAS RETRIEVAL & FALSE-FRIEND PROTECTION
def test_alias_retrieval_and_false_friend_protection(hybrid_router):
    # Alias P.S.04-A resolves to PS-04A
    res_alias = hybrid_router.search("Diagnostics tag P.S.04-A reading")
    assert "PS-04A" in res_alias.identified_entities

    # Multi-word alias "Hydraulic Power Pack" resolves to HPU
    res_pack = hybrid_router.search("Hydraulic Power Pack startup")
    assert "HPU" in res_pack.identified_entities

    # False-Friend Protection: Query for PS-40 must NOT return PS-04 or PS-04A
    res_ps40 = hybrid_router.search("What circuit is sensor PS-40 installed on?")
    assert "PS-40" in res_ps40.identified_entities
    # Ensure PS-04 is not in identified entities
    assert "PS-04" not in res_ps40.identified_entities
    assert "PS-04A" not in res_ps40.identified_entities
    # Verify top chunk identifies PS-40 / Coolant Loop
    assert "Coolant Loop" in res_ps40.chunks[0].chunk.text or "PS-40" in res_ps40.chunks[0].chunk.text
    # Verify no false-friend intrusion from PS-04 or PS-04A
    for fc in res_ps40.chunks:
        assert "PS-04" not in fc.chunk.entity_references
        assert "PS-04A" not in fc.chunk.entity_references

    # Unknown aliases must NOT be automatically mapped to known components
    res_unknown = hybrid_router.search("Status of sensor XYZ-999")
    assert "XYZ-999" not in res_unknown.identified_entities
    assert len(res_unknown.identified_entities) == 0

# 3. BM25 KEYWORD RETRIEVAL
def test_bm25_retrieval():
    chunks = ChunkIndexer.load_chunks()
    bm25 = BM25Retriever(chunks)
    
    # Specific industrial phrases
    results = bm25.search("Shutdown Procedure 4.7 persistent 10 seconds", top_k=5)
    assert len(results) > 0
    top_text = results[0].chunk.text
    assert "Shutdown" in top_text or "4.7" in top_text
    assert results[0].channel == "bm25"
    assert results[0].score > 0.0

# 4. DENSE SEMANTIC RETRIEVAL (BAAI/bge-small-en-v1.5)
def test_dense_semantic_retrieval():
    chunks = ChunkIndexer.load_chunks()
    dense = DenseSemanticRetriever(chunks)
    assert dense.embeddings.shape[1] == 384

    # Paraphrased conceptual query with zero exact keyword match to "sight glass"
    results = dense.search("fluid level inspection safeguards before starting power unit", top_k=5)
    assert len(results) > 0
    top = results[0]
    assert top.channel == "dense_semantic"
    assert 0.0 <= top.score <= 1.0
    # Top results must relate to startup interlocks / fluid level
    combined = " ".join([r.chunk.text.lower() for r in results[:3]])
    assert "fluid" in combined or "startup" in combined or "interlock" in combined

# 5. STRUCTURED SQL RETRIEVAL
def test_structured_sql_retrieval():
    retriever = StructuredRetriever()
    structured = retriever.retrieve_structured_data(["PLC-03"])
    
    # Check relationships
    rels = structured["relationships"]
    assert len(rels) >= 2
    targets = [r.target_component for r in rels if r.source_component == "PLC-03"]
    assert "PS-04A" in targets
    assert "IV-21" in targets

    # Convert to chunks
    chunks = retriever.search_as_chunks(["PLC-03"])
    assert len(chunks) >= 2
    assert chunks[0].channel == "structured_sql"

# 6. HYBRID RANKING & RECIPROCAL RANK FUSION (RRF)
def test_hybrid_ranking_and_rrf(hybrid_router):
    res = hybrid_router.search("What is normal operating pressure for HPU?")
    assert len(res.chunks) > 0
    
    # Verify fused RRF score ordering
    scores = [fc.rrf_score for fc in res.chunks]
    assert scores == sorted(scores, reverse=True)
    
    # Top chunk must have multi-channel presence or high tier trust
    top_chunk = res.chunks[0]
    assert top_chunk.rrf_score > 0.0
    assert top_chunk.trust_multiplier >= 0.85
    assert "200" in top_chunk.chunk.text or "pressure" in top_chunk.chunk.text.lower()

# 7. REVISION-AWARE RETRIEVAL
def test_revision_aware_retrieval(hybrid_router):
    # Query for historical SW 3.0 threshold
    res_30 = hybrid_router.search("What was normal operating pressure before SW 3.2?", target_revision="3.0")
    assert res_30.target_revision == "3.0"
    assert any("180" in fc.chunk.text for fc in res_30.chunks)

    # Query for SW 3.2 threshold
    res_32 = hybrid_router.search("What is normal operating pressure for SW 3.2?", target_revision="3.2")
    assert res_32.target_revision == "3.2"
    assert any("200" in fc.chunk.text for fc in res_32.chunks)

    # Query with target_revision=None does not mix historical 180 bar as current
    res_curr = hybrid_router.search("What is normal operating pressure?", target_revision=None)
    top_texts = [fc.chunk.text for fc in res_curr.chunks[:3]]
    assert any("200" in t for t in top_texts)

# 8. CONFLICTING EVIDENCE RETRIEVAL
def test_conflicting_evidence_retrieval(hybrid_router):
    res = hybrid_router.search("HPU normal operating pressure revisions and field notes")
    assert len(res.structured_conflicts) >= 1
    conf = res.structured_conflicts[0]
    assert conf["conflicting_parameter"] == "HPU.normal_operating_pressure"
    assert conf["resolution_status"] == "RESOLVED_BY_REVISION"
    assert "180" in conf["value_2"]
    assert "200" in conf["value_1"]

# 9. CITATION VALIDITY & FABRICATION REJECTION
def test_citation_validity(hybrid_router):
    retrieval = hybrid_router.search("What does alarm A17 indicate?")
    
    # 1. Valid citation matching retrieved text
    valid_citation = EvidenceCitation(
        chunk_id="CHK-TEST-01",
        source_document="alarm_reference.pdf",
        page_number=1,
        section_or_cell="Alarm Table",
        quoted_evidence="Hydraulic pressure below 150 bar",
        trust_tier=2
    )
    valid_ans = GroundedAnswer(
        question="What does alarm A17 indicate?",
        direct_answer="Hydraulic pressure below 150 bar.",
        citations=[valid_citation],
        confidence_score=0.99,
        confidence_justification="Direct quote"
    )
    is_valid, approved, rejections = CitationValidator.validate_answer_citations(valid_ans, retrieval)
    assert is_valid is True
    assert len(approved) == 1
    assert len(rejections) == 0

    # 2. Fabricated citation with non-existent document
    fake_doc_citation = EvidenceCitation(
        chunk_id="CHK-FAKE-01",
        source_document="non_existent_manual_v9.pdf",
        page_number=1,
        quoted_evidence="Some text",
        trust_tier=1
    )
    fake_ans = GroundedAnswer(
        question="What does alarm A17 indicate?",
        direct_answer="Some answer",
        citations=[fake_doc_citation],
        confidence_score=0.5,
        confidence_justification="Test"
    )
    is_valid_fake, approved_fake, rejections_fake = CitationValidator.validate_answer_citations(fake_ans, retrieval)
    assert is_valid_fake is False
    assert len(approved_fake) == 0
    assert any("does not exist" in r for r in rejections_fake)

    # 3. Fabricated text not present in retrieved chunks
    fake_quote_citation = EvidenceCitation(
        chunk_id="CHK-FAKE-02",
        source_document="alarm_reference.pdf",
        page_number=1,
        quoted_evidence="Fabricated statement about quantum hydraulics",
        trust_tier=2
    )
    fake_quote_ans = GroundedAnswer(
        question="What does alarm A17 indicate?",
        direct_answer="Some answer",
        citations=[fake_quote_citation],
        confidence_score=0.5,
        confidence_justification="Test"
    )
    is_valid_q, _, rejections_q = CitationValidator.validate_answer_citations(fake_quote_ans, retrieval)
    assert is_valid_q is False
    assert any("not found in retrieved chunks" in r for r in rejections_q)

# 10. FALSE-PREMISE QUESTION HANDLING (Q20)
def test_false_premise_question_handling(answer_engine):
    ans = answer_engine.answer_question(
        "What is the calibration interval for the voltage sensor on the electrical system diagram?"
    )
    assert ans.abstention_category == AbstentionCategory.FALSE_PREMISE
    assert "false premise" in ans.direct_answer.lower()
    assert "does not depict a voltage sensor" in ans.direct_answer.lower()
    assert ans.verification_status == "NOT FOUND"
    assert ans.confidence_score >= 0.95

# 11. MISSING-INFORMATION QUESTIONS (Q19, Q22)
def test_missing_information_questions(answer_engine):
    # Q19: PS-04A operating temperature
    ans_q19 = answer_engine.answer_question("What is the maximum continuous operating temperature of PS-04A?")
    assert ans_q19.abstention_category == AbstentionCategory.GENUINELY_ABSENT
    assert "insufficient evidence" in ans_q19.direct_answer.lower()
    assert ans_q19.verification_status == "NOT FOUND"

    # Q22: IV-21 MTBF
    ans_q22 = answer_engine.answer_question("What is the mean time between failures (MTBF) for isolation valve IV-21?")
    assert ans_q22.abstention_category == AbstentionCategory.GENUINELY_ABSENT
    assert "insufficient evidence" in ans_q22.direct_answer.lower()
    assert ans_q22.verification_status == "NOT FOUND"

# 12. PARTIALLY SUPPORTED QUESTIONS (Q21, Q23)
def test_partially_supported_questions(answer_engine):
    # Q23: 400V supply compatibility
    ans_q23 = answer_engine.answer_question("Is Aegis Series-7 HCS compatible with a 3-phase 400V supply?")
    assert ans_q23.abstention_category == AbstentionCategory.PARTIALLY_VERIFIED
    assert "480v" in ans_q23.direct_answer.lower()
    assert "unstated" in ans_q23.direct_answer.lower()
    assert ans_q23.verification_status == "PARTIALLY VERIFIED"

    # Q21: ECN-1058 approver
    ans_q21 = answer_engine.answer_question("Who approved engineering bulletin ECN-1058?")
    assert ans_q21.abstention_category == AbstentionCategory.OMITTED_COMPANION_DOCUMENT
    assert "blank" in ans_q21.direct_answer.lower()
    assert "no individual approver" in ans_q21.direct_answer.lower()

# 13. OFFLINE DETERMINISTIC FALLBACK CORE QUESTIONS
def test_offline_deterministic_fallback(answer_engine):
    # Q01: Startup interlocks
    ans_q01 = answer_engine.answer_question("What must be true before starting the Hydraulic Power Unit?", force_offline=True)
    assert ans_q01.generation_method == "deterministic_offline"
    assert "IV-21" in ans_q01.direct_answer
    assert "sight glass" in ans_q01.direct_answer or "fluid level" in ans_q01.direct_answer.lower()
    assert "emergency stop" in ans_q01.direct_answer.lower()
    assert "maintenance access panel" in ans_q01.direct_answer.lower()
    assert len(ans_q01.citations) >= 1

    # Q04: PS-04 vs PS-04A
    ans_q04 = answer_engine.answer_question("Is PS-04 the same component as PS-04A?", force_offline=True)
    assert "not the same" in ans_q04.direct_answer.lower()
    assert "ECN-1042" in ans_q04.direct_answer
    assert "drift" in ans_q04.direct_answer.lower()

    # Q06: Schematic connections
    ans_q06 = answer_engine.answer_question("Which components connect directly to the HCS controller according to the hydraulic schematic?", force_offline=True)
    assert "PS-04A" in ans_q06.direct_answer
    assert "IV-21" in ans_q06.direct_answer
    assert "purple" in ans_q06.direct_answer.lower()

    # Q08: Controller reset prohibition
    ans_q08 = answer_engine.answer_question("Under what circumstances must the controller not be reset?", force_offline=True)
    assert "50 bar" in ans_q08.direct_answer
    assert "uncommanded" in ans_q08.direct_answer.lower()

# 14. API-LEVEL ANSWER RESPONSE SCHEMA
def test_api_level_answer_response(answer_engine):
    ans = answer_engine.answer_question("What action is required if alarm A17 persists for more than 10 seconds?")
    # Schema assertions
    assert isinstance(ans, GroundedAnswer)
    assert ans.question != ""
    assert "Shutdown Procedure 4.7" in ans.direct_answer
    assert len(ans.supporting_claims) > 0
    assert len(ans.citations) > 0
    assert ans.confidence_score > 0.9
    assert ans.confidence_justification != ""
    assert ans.verification_status == "VERIFIED"
    assert ans.abstention_category == AbstentionCategory.NONE

