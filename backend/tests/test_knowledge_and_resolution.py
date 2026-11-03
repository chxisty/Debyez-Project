"""
Automated Test Suite for Phase 2 & Phase 3
Intermediate Knowledge Representation (IKR), Database Integrity, Entity Resolution, and Conflict Detection.
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
from backend.app.entity_resolution.resolver import EntityResolver
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

def test_document_deletion_cascades_facts():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test_aegis_cascade.db"
        db = KnowledgeDatabase(test_db_path)

        doc = DocumentEntity(
            document_id="DOC-CASC-01",
            filename="cascade_doc.pdf",
            document_type="PDF",
            source_category="test",
            trust_level=2
        )
        db.insert_document(doc)

        fact = FactEntity(
            fact_id="FACT-CASC-01",
            subject="IV-21",
            predicate="state",
            object_value="OPEN",
            provenance=ProvenanceRecord(
                source_document="cascade_doc.pdf",
                page_number=1,
                extraction_method="test"
            )
        )
        db.insert_fact(fact)

        # Verify fact exists
        assert len(db.get_facts_by_subject("IV-21")) == 1

        # Delete parent document
        with db.get_connection() as conn:
            conn.execute("DELETE FROM documents WHERE filename = ?", ("cascade_doc.pdf",))
            conn.commit()

        # Fact must be cascade deleted
        assert len(db.get_facts_by_subject("IV-21")) == 0

# 2. PROVENANCE PRESERVATION
def test_provenance_preservation(populated_db):
    facts = populated_db.get_all_facts()
    assert len(facts) >= 25

    for f in facts:
        assert f.provenance.source_document != "", f"Fact {f.fact_id} missing source_document"
        assert f.provenance.page_number >= 1, f"Fact {f.fact_id} invalid page number"
        assert f.provenance.extraction_method != "", f"Fact {f.fact_id} missing extraction_method"
        assert 0.0 <= f.provenance.confidence <= 1.0, f"Fact {f.fact_id} invalid confidence"
        assert isinstance(f.verification_status, VerificationStatus)

# 3. DETERMINISTIC ALIAS NORMALIZATION
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

# 4. NEGATIVE DISAMBIGUATION RULES & FALSE-FRIEND PROTECTION
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

# 5. REVISION INTERVAL LOGIC
def test_revision_engine():
    # Version comparisons
    assert RevisionEngine.compare_versions("3.0", "3.2") == -1
    assert RevisionEngine.compare_versions("3.2", "3.0") == 1
    assert RevisionEngine.compare_versions("3.2", "3.2.0") == 0
    assert RevisionEngine.compare_versions("3.2.1", "3.2") == 1

    # Overlap logic
    # [3.0, 3.2) and [3.2, inf) do NOT overlap
    assert RevisionEngine.intervals_overlap("3.0", "3.2", "3.2", None) is False
    # [3.0, 3.2) and [3.1, 3.3) DO overlap
    assert RevisionEngine.intervals_overlap("3.0", "3.2", "3.1", "3.3") is True
    # [3.2, inf) and [3.2, inf) DO overlap
    assert RevisionEngine.intervals_overlap("3.2", None, "3.2", None) is True

    # Fact applicability
    fact_hist = FactEntity(
        fact_id="F-H",
        subject="HPU",
        predicate="pressure",
        object_value="180",
        applicable_revision_start="3.0",
        applicable_revision_end="3.2",
        is_current=False,
        provenance=ProvenanceRecord(source_document="doc.pdf")
    )
    assert RevisionEngine.is_fact_applicable(fact_hist, "3.0") is True
    assert RevisionEngine.is_fact_applicable(fact_hist, "3.1") is True
    assert RevisionEngine.is_fact_applicable(fact_hist, "3.2") is False

    fact_curr = FactEntity(
        fact_id="F-C",
        subject="HPU",
        predicate="pressure",
        object_value="200",
        applicable_revision_start="3.2",
        applicable_revision_end=None,
        is_current=True,
        provenance=ProvenanceRecord(source_document="doc.pdf")
    )
    assert RevisionEngine.is_fact_applicable(fact_curr, "3.0") is False
    assert RevisionEngine.is_fact_applicable(fact_curr, "3.2") is True
    assert RevisionEngine.is_fact_applicable(fact_curr, "3.2.1") is True

# 6. HISTORICAL VS CURRENT OPERATING PRESSURE VALUES
def test_historical_vs_current_pressure(populated_db):
    hpu_pressure_facts = [
        f for f in populated_db.get_facts_by_subject("HPU")
        if f.predicate == "normal_operating_pressure"
    ]
    assert len(hpu_pressure_facts) >= 3

    # Check 180 bar historical fact
    fact_180 = [f for f in hpu_pressure_facts if f.object_value == "180"][0]
    assert fact_180.is_current is False
    assert fact_180.applicable_revision_start == "3.0"
    assert fact_180.applicable_revision_end == "3.2"

    # Check 200 bar current fact
    fact_200 = [f for f in hpu_pressure_facts if f.object_value == "200"][0]
    assert fact_200.is_current is True
    assert fact_200.applicable_revision_start == "3.2"
    assert fact_200.provenance.source_document == "ECN-1042.pdf"

    # Active facts for revision 3.0 must return 180 bar, not 200 bar
    active_30 = populated_db.get_active_facts_for_revision("3.0")
    active_30_pressure = [f for f in active_30 if f.predicate == "normal_operating_pressure"]
    assert len(active_30_pressure) == 1
    assert active_30_pressure[0].object_value == "180"

    # Active facts for revision 3.2 must return 200 bar
    active_32 = populated_db.get_active_facts_for_revision("3.2")
    active_32_pressure = [f for f in active_32 if f.predicate == "normal_operating_pressure" and f.is_current]
    assert len(active_32_pressure) == 1
    assert active_32_pressure[0].object_value == "200"

# 7. CONFLICT DETECTION WITHOUT DELETING OR OVERWRITING
def test_conflict_detection_preserves_facts(populated_db):
    conflicts = populated_db.get_all_conflicts()
    assert len(conflicts) >= 2

    # Verify 180 vs 200 revision supersession conflict
    rev_conflicts = [c for c in conflicts if c.resolution_status == ConflictResolutionType.RESOLVED_BY_REVISION]
    assert len(rev_conflicts) >= 1
    rev_c = rev_conflicts[0]
    assert rev_c.conflicting_parameter == "HPU.normal_operating_pressure"
    assert "superseded" in rev_c.explanation.lower()

    # Verify 200 vs 175 source trust conflict
    trust_conflicts = [c for c in conflicts if c.resolution_status == ConflictResolutionType.RESOLVED_BY_SOURCE_TRUST]
    assert len(trust_conflicts) >= 1
    trust_c = trust_conflicts[0]
    assert "Tier 1" in trust_c.explanation
    assert "Tier 5" in trust_c.explanation

    # Confirm neither fact was overwritten in DB
    all_facts = populated_db.get_facts_by_subject("HPU")
    values = [f.object_value for f in all_facts if f.predicate == "normal_operating_pressure"]
    assert "180" in values
    assert "200" in values
    assert "175" in values

# 8. MISSING INFORMATION & ABSTENTION TAXONOMY HANDLING
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

# 9. IKR JSON EXPORT AND IMPORT CONSISTENCY
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
    assert export_obj.total_conflicts >= 3

    # Check topological relationships integrity
    purple_rels = [r for r in export_obj.relationships if r.line_type == "solid_purple"]
    assert len(purple_rels) == 2
    targets = [r.target_component for r in purple_rels]
    assert "PS-04A" in targets
    assert "IV-21" in targets

    # Ensure HPU does not have a purple line
    hpu_purple = [r for r in purple_rels if r.source_component == "PLC-03" and r.target_component == "HPU"]
    assert len(hpu_purple) == 0, "HPU must NOT have a purple direct control line from PLC-03"
