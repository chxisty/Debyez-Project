"""
Automated Test Suite for Phase 2 & Phase 3 (Refined Baseline)
Intermediate Knowledge Representation (IKR), Database Archival & Integrity,
Entity Resolution, Revision-Aware Retrieval, and Conflict Semantics.
"""
import pytest
import sqlite3
import json
from pathlib import Path
import tempfile

from backend.app.knowledge.schema import (
    DocumentEntity, ComponentEntity, FactEntity, RelationshipEntity,
    ConflictEntity, ProvenanceRecord, VerificationStatus, ConflictResolutionType, IKRExport
)
from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.entity_resolution.normalizer import IdentifierNormalizer
from backend.app.entity_resolution.disambiguator import EntityDisambiguator
from backend.app.conflict_detection.revision_engine import RevisionEngine
from backend.app.conflict_detection.conflict_detector import ConflictDetector
from backend.app.knowledge.populator import populate_database
from backend.app.config import KNOWLEDGE_DIR

@pytest.fixture(scope="module")
def populated_db():
    """Returns the pre-populated knowledge database."""
    db = KnowledgeDatabase()
    populate_database(db)
    return db

# 1. DATABASE INTEGRITY & FOREIGN KEY CONSTRAINTS
def test_foreign_key_enforcement():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test_aegis.db"
        db = KnowledgeDatabase(test_db_path)

        # Attempting to insert a fact referencing a non-existent document MUST fail
        invalid_fact = FactEntity(
            fact_id="FACT-ERR-01",
            subject="HPU",
            predicate="test_predicate",
            object_value="100",
            provenance=ProvenanceRecord(
                source_document="non_existent_doc.pdf",
                page_number=1,
                extraction_method="test"
            )
        )

        with pytest.raises(sqlite3.IntegrityError):
            db.insert_fact(invalid_fact)

        # Now insert the document first
        doc = DocumentEntity(
            document_id="DOC-TEST-01",
            filename="valid_doc.pdf",
            document_type="PDF",
            source_category="test",
            trust_level=2
        )
        db.insert_document(doc)

        # Now inserting fact with valid foreign key must succeed
        valid_fact = FactEntity(
            fact_id="FACT-OK-01",
            subject="HPU",
            predicate="test_predicate",
            object_value="100",
            provenance=ProvenanceRecord(
                source_document="valid_doc.pdf",
                page_number=1,
                extraction_method="test"
            )
        )
        db.insert_fact(valid_fact)

        # Verify fact was stored
        facts = db.get_facts_by_subject("HPU")
        assert len(facts) == 1
        assert facts[0].object_value == "100"

# 2. DOCUMENT ARCHIVAL & SOFT DELETION PRESERVES FACTS
def test_document_archival_preserves_facts_and_provenance():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test_aegis_archival.db"
        db = KnowledgeDatabase(test_db_path)

        doc = DocumentEntity(
            document_id="DOC-ARCH-01",
            filename="archived_manual.pdf",
            document_type="PDF",
            source_category="manual",
            trust_level=2
        )
        db.insert_document(doc)

        fact = FactEntity(
            fact_id="FACT-ARCH-01",
            subject="IV-21",
            predicate="state",
            object_value="OPEN",
            provenance=ProvenanceRecord(
                source_document="archived_manual.pdf",
                page_number=1,
                extraction_method="test"
            )
        )
        db.insert_fact(fact)

        # 1. Soft-archive the document
        db.archive_document("archived_manual.pdf", reason="Superseded by Rev 4")

        # Document must be flagged archived
        archived_docs = db.get_archived_documents()
        assert len(archived_docs) == 1
        assert archived_docs[0].filename == "archived_manual.pdf"
        assert archived_docs[0].is_archived is True
        assert archived_docs[0].archival_reason == "Superseded by Rev 4"

        # Active documents must exclude it
        active_docs = db.get_active_documents()
        assert len(active_docs) == 0

        # Facts must NOT be deleted; they remain in the database for auditing
        all_facts = db.get_all_facts(include_archived=True)
        assert len(all_facts) == 1
        assert all_facts[0].fact_id == "FACT-ARCH-01"
        assert all_facts[0].is_archived is True
        assert all_facts[0].provenance.source_document == "archived_manual.pdf"

        # 2. Hard deletion protection: attempting to DELETE a referenced document must fail
        with pytest.raises(sqlite3.IntegrityError):
            with db.get_connection() as conn:
                conn.execute("DELETE FROM documents WHERE filename = ?", ("archived_manual.pdf",))

# 3. PROVENANCE PRESERVATION
def test_provenance_preservation(populated_db):
    facts = populated_db.get_all_facts()
    assert len(facts) >= 25

    for f in facts:
        assert f.provenance.source_document != "", f"Fact {f.fact_id} missing source_document"
        assert f.provenance.page_number >= 1, f"Fact {f.fact_id} invalid page number"
        assert f.provenance.extraction_method != "", f"Fact {f.fact_id} missing extraction_method"
        assert 0.0 <= f.provenance.confidence <= 1.0, f"Fact {f.fact_id} invalid confidence"
        assert isinstance(f.verification_status, VerificationStatus)

# 4. DETERMINISTIC ALIAS NORMALIZATION
def test_alias_normalization():
    assert IdentifierNormalizer.normalize_token("P.S.04-A") == "PS04A"
    assert IdentifierNormalizer.normalize_token("PS-04") == "PS04"
    assert IdentifierNormalizer.normalize_token("IV-21") == "IV21"
    assert IdentifierNormalizer.normalize_token("HP unit") == "HPU"
    assert IdentifierNormalizer.normalize_token("HYDRAULIC POWER PACK") == "HPU"
    assert IdentifierNormalizer.normalize_token("THE UNIT") == "HPU"
    assert IdentifierNormalizer.normalize_token("Aegis Controller") == "PLC03"

    assert IdentifierNormalizer.to_canonical_id("P.S.04-A") == "PS-04A"
    assert IdentifierNormalizer.to_canonical_id("PS04A") == "PS-04A"
    assert IdentifierNormalizer.to_canonical_id("P04A") == "PS-04A"
    assert IdentifierNormalizer.to_canonical_id("PS-04") == "PS-04"
    assert IdentifierNormalizer.to_canonical_id("PS04") == "PS-04"
    assert IdentifierNormalizer.to_canonical_id("PS40") == "PS-40"
    assert IdentifierNormalizer.to_canonical_id("IV21") == "IV-21"
    assert IdentifierNormalizer.to_canonical_id("PLC03") == "PLC-03"

# 5. NEGATIVE DISAMBIGUATION RULES & FALSE-FRIEND PROTECTION
def test_negative_disambiguation_rules():
    # PS-04 != PS-40
    res_40 = EntityDisambiguator.check_identity("PS-04", "PS-40")
    assert res_40.is_same_component is False
    assert "Coolant Loop, Skid B" in res_40.explanation

    # PS-04 != PS-04A
    res_04a = EntityDisambiguator.check_identity("PS-04", "PS-04A")
    assert res_04a.is_same_component is False
    assert "ECN-1042" in res_04a.explanation
    assert "NOT a form-fit-function replacement" in res_04a.explanation

    # PS-40 != PS-04A
    res_cross = EntityDisambiguator.check_identity("PS-40", "PS-04A")
    assert res_cross.is_same_component is False

    # Positive matches
    res_pos1 = EntityDisambiguator.check_identity("P.S.04-A", "PS-04A")
    assert res_pos1.is_same_component is True
    assert res_pos1.canonical_id == "PS-04A"

    res_pos2 = EntityDisambiguator.check_identity("PRESSURE SENSOR 04", "PS-04")
    assert res_pos2.is_same_component is True
    assert res_pos2.canonical_id == "PS-04"

# 6. REVISION ENGINE INTERVAL LOGIC
def test_revision_engine():
    # Version comparisons
    assert RevisionEngine.compare_versions("3.0", "3.2") == -1
    assert RevisionEngine.compare_versions("3.2", "3.0") == 1
    assert RevisionEngine.compare_versions("3.2", "3.2.0") == 0
    assert RevisionEngine.compare_versions("3.2.1", "3.2") == 1
    assert RevisionEngine.compare_versions("3.3", "3.2") == 1

    # Overlap logic
    # [3.0, 3.2) and [3.2, inf) do NOT overlap
    assert RevisionEngine.intervals_overlap("3.0", "3.2", "3.2", None) is False
    # [3.0, 3.2) and [3.1, 3.3) DO overlap
    assert RevisionEngine.intervals_overlap("3.0", "3.2", "3.1", "3.3") is True
    # [3.2, inf) and [3.2, inf) DO overlap
    assert RevisionEngine.intervals_overlap("3.2", None, "3.2", None) is True

# 7. REVISION-SPECIFIC RETRIEVAL ACROSS 3.0, 3.1, 3.2, 3.3 & UNSPECIFIED
def test_revision_specific_retrieval(populated_db):
    # Revision 3.0 must return 180 bar
    active_30 = populated_db.get_active_facts_for_revision("3.0")
    press_30 = [f for f in active_30 if f.predicate == "normal_operating_pressure"]
    assert len(press_30) == 1
    assert press_30[0].object_value == "180"
    assert press_30[0].fact_type == "historical_setpoint"

    # Revision 3.1 must return 180 bar
    active_31 = populated_db.get_active_facts_for_revision("3.1")
    press_31 = [f for f in active_31 if f.predicate == "normal_operating_pressure"]
    assert len(press_31) == 1
    assert press_31[0].object_value == "180"
    assert press_31[0].fact_type == "historical_setpoint"

    # Revision 3.2 must return 200 bar
    active_32 = populated_db.get_active_facts_for_revision("3.2")
    press_32 = [f for f in active_32 if f.predicate == "normal_operating_pressure"]
    assert len(press_32) == 1
    assert press_32[0].object_value == "200"
    assert press_32[0].fact_type == "specified_setpoint"

    # Revision 3.3 must return 200 bar
    active_33 = populated_db.get_active_facts_for_revision("3.3")
    press_33 = [f for f in active_33 if f.predicate == "normal_operating_pressure"]
    assert len(press_33) == 1
    assert press_33[0].object_value == "200"
    assert press_33[0].fact_type == "specified_setpoint"

    # Query without specified revision (revision=None) must NOT silently mix historical or observation values
    current_default = populated_db.get_active_facts_for_revision(None)
    current_pressure = [f for f in current_default if f.predicate == "normal_operating_pressure"]
    assert len(current_pressure) == 1
    assert current_pressure[0].object_value == "200"
    assert current_pressure[0].is_current is True
    # Ensure 180 and 175 are NOT in default current results
    assert "180" not in [f.object_value for f in current_pressure]
    assert "175" not in [f.object_value for f in current_pressure]

# 8. CONFLICT SEMANTICS: SETPOINT VS MEASUREMENT DISTINCTION
def test_conflict_semantics_distinguishes_observation_from_setpoint(populated_db):
    conflicts = populated_db.get_all_conflicts()
    
    # 1. 180 bar vs 200 bar IS a valid revision supersession conflict
    rev_conflicts = [c for c in conflicts if c.resolution_status == ConflictResolutionType.RESOLVED_BY_REVISION]
    assert len(rev_conflicts) == 1
    c = rev_conflicts[0]
    assert c.conflicting_parameter == "HPU.normal_operating_pressure"
    assert c.value_1 == "200 bar"
    assert c.value_2 == "180 bar"
    assert "superseded" in c.explanation.lower()

    # 2. 175 bar field observation MUST NOT be classified as a contradiction of 200 bar setpoint
    contradiction_conflicts = [
        c for c in conflicts 
        if ("175" in c.value_1 or "175" in c.value_2) and ("200" in c.value_1 or "200" in c.value_2)
    ]
    assert len(contradiction_conflicts) == 0, (
        "175 bar field observation must not be automatically classified as contradicting the 200 bar setpoint!"
    )

# 9. EVIDENCE PRESERVATION: HISTORICAL, OBSERVATIONAL & CONFLICTS REMAIN ACCESSIBLE
def test_evidence_preservation_accessible(populated_db):
    all_hpu_facts = populated_db.get_facts_by_subject("HPU")
    values = {f.object_value: f for f in all_hpu_facts}

    # Historical setpoint preserved with metadata
    assert "180" in values
    assert values["180"].fact_type == "historical_setpoint"
    assert values["180"].verification_status == VerificationStatus.VERIFIED
    assert values["180"].applicable_revision_start == "3.0"
    assert values["180"].applicable_revision_end == "3.2"

    # Current official setpoint preserved with metadata
    assert "200" in values
    assert values["200"].fact_type == "specified_setpoint"
    assert values["200"].is_current is True
    assert values["200"].provenance.source_document == "ECN-1042.pdf"

    # Field observation preserved with its low reliability and original source
    assert "175" in values
    assert values["175"].fact_type == "observed_measurement"
    assert values["175"].verification_status == VerificationStatus.PARTIALLY_VERIFIED
    assert values["175"].provenance.source_document == "site_survey_notes.docx"
    assert "uncalibrated local gauge" in values["175"].notes

# 10. MISSING INFORMATION & ABSTENTION TAXONOMY HANDLING
def test_missing_information_taxonomy(populated_db):
    all_facts = populated_db.get_all_facts()

    # Category A: Genuinely absent (PS-04A operating temp, IV-21 MTBF)
    temp_fact = [f for f in all_facts if f.predicate == "continuous_operating_temperature_max"][0]
    assert temp_fact.verification_status == VerificationStatus.NOT_FOUND
    assert temp_fact.object_value == "NOT_FOUND"

    mtbf_fact = [f for f in all_facts if f.predicate == "mean_time_between_failures"][0]
    assert mtbf_fact.verification_status == VerificationStatus.NOT_FOUND
    assert mtbf_fact.object_value == "NOT_FOUND"

    # Category B: False Premise (Voltage sensor)
    volt_fact = [f for f in all_facts if f.predicate == "voltage_sensor_calibration_interval"][0]
    assert volt_fact.verification_status == VerificationStatus.NOT_FOUND
    assert "FALSE_PREMISE" in volt_fact.object_value

    # Category C: Partially Supported / Unconfirmed (400V supply)
    volt_400 = [f for f in all_facts if f.predicate == "incoming_power_rating"][0]
    assert volt_400.verification_status == VerificationStatus.PARTIALLY_VERIFIED

    # Category D: Omitted Companion Document (ECN-1058 approver signature)
    ecn_approver = [f for f in all_facts if f.predicate == "approver_signature"][0]
    assert ecn_approver.verification_status == VerificationStatus.PARTIALLY_VERIFIED
    assert ecn_approver.object_value == "OMITTED_BLANK"

# 11. IKR JSON EXPORT AND IMPORT CONSISTENCY
def test_ikr_export_json_consistency(populated_db):
    export_path = KNOWLEDGE_DIR / "ikr_export.json"
    assert export_path.exists(), "ikr_export.json does not exist"

    with open(export_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate schema
    export_obj = IKRExport(**data)
    assert export_obj.total_documents == 20
    assert export_obj.total_components == 14
    assert export_obj.total_facts >= 28
    assert export_obj.total_relationships >= 8
    assert export_obj.total_conflicts == 1

    # Check topological relationships integrity
    purple_rels = [r for r in export_obj.relationships if r.line_type == "solid_purple"]
    assert len(purple_rels) == 2
    targets = [r.target_component for r in purple_rels]
    assert "PS-04A" in targets
    assert "IV-21" in targets

    # Ensure HPU does not have a purple line
    hpu_purple = [r for r in purple_rels if r.source_component == "PLC-03" and r.target_component == "HPU"]
    assert len(hpu_purple) == 0, "HPU must NOT have a purple direct control line from PLC-03"
