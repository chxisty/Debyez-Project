"""
IKR Database Populator
Loads verified document metadata, canonical components, facts, diagram topology, and conflicts
into the normalized SQLite database and exports ikr_export.json.
Based on the approved Source Verification Report AEG-SVR-03.
"""
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')

from backend.app.config import (
    DATA_DIR, KNOWLEDGE_DIR, DOCUMENT_METADATA_REGISTRY
)
from backend.app.knowledge.schema import (
    DocumentEntity, ComponentEntity, FactEntity, RelationshipEntity,
    ConflictEntity, ProvenanceRecord, VerificationStatus, ConflictResolutionType
)
from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.conflict_detection.conflict_detector import ConflictDetector

def compute_file_sha256(filepath: Path) -> str:
    """Computes standard 64-character SHA-256 hash."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def populate_database(db: KnowledgeDatabase):
    """Populates documents, components, facts, relationships, and runs conflict detection."""
    print("Beginning IKR Database Population...")

    # 1. POPULATE DOCUMENTS (20 files)
    print("1/5 Populating Documents...")
    all_files = list(DATA_DIR.rglob("*.*"))
    dataset_files = [f for f in all_files if f.is_file() and not f.name.startswith(".")]

    doc_entities: Dict[str, DocumentEntity] = {}

    for fpath in dataset_files:
        fname = fpath.name
        rel_path = str(fpath.relative_to(DATA_DIR)).replace("\\", "/")
        reg = DOCUMENT_METADATA_REGISTRY.get(fname, {})

        sha = compute_file_sha256(fpath)
        doc = DocumentEntity(
            document_id=reg.get("doc_id", fname),
            filename=fname,
            document_type=fpath.suffix.lstrip(".").upper(),
            source_category=reg.get("category", "unclassified"),
            revision=reg.get("revision", "1.0"),
            publication_date=reg.get("effective_date"),
            effective_date=reg.get("effective_date"),
            trust_level=int(reg.get("trust_tier", 4)),
            is_active=True,
            sha256_hash=sha,
            metadata={"relative_path": rel_path, "size_bytes": fpath.stat().st_size}
        )
        db.insert_document(doc)
        doc_entities[fname] = doc

    print(f"   Inserted {len(doc_entities)} document records.")

    # 2. POPULATE CANONICAL COMPONENTS
    print("2/5 Populating Canonical Components...")
    components = [
        ComponentEntity(
            component_id="HPU",
            canonical_name="Hydraulic Power Unit",
            aliases=["HP Unit", "Hydraulic Unit", "Hydraulic Power Pack", "The Unit", "Hydraulic Pack"],
            component_type="power_unit",
            description="Primary hydraulic pressure source for the press circuit.",
            location="Skid A, Bay 2",
            status="Active",
            source_references=["component_register.xlsx", "operator_manual.pdf", "training_slide_excerpt.pptx"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 1",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="IV-21",
            canonical_name="Isolation Valve 21",
            aliases=["IV21", "Isolation Valve", "Isolation Valve 21"],
            component_type="valve",
            description="Normally Open hydraulic isolation valve isolating HPU from the press circuit.",
            location="Hydraulic Module",
            status="Active",
            source_references=["component_register.xlsx", "maintenance_manual.pdf", "operator_manual.pdf"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 2",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="PS-04",
            canonical_name="Pressure Sensor 04",
            aliases=["P04", "PS04", "Pressure Sensor 04"],
            component_type="sensor",
            description="Legacy HPU discharge pressure sensor. Superseded by PS-04A effective SW 3.2 per ECN-1042.",
            location="HPU discharge line",
            status="Superseded",
            source_references=["component_register.xlsx", "ECN-1042.pdf", "legacy_manual_v1.html"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 3",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="PS-04A",
            canonical_name="Pressure Sensor 04A",
            aliases=["P04A", "PS04A", "P.S.04-A", "Pressure Sensor 04A", "Pressure XDCR"],
            component_type="sensor",
            description="Active HPU discharge pressure sensor. Requires controller firmware >= 3.2.",
            location="HPU discharge line",
            status="Active",
            source_references=["component_register.xlsx", "ECN-1042.pdf", "screen_03_diagnostics.png"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 4",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="PS-40",
            canonical_name="Pressure Sensor 40",
            aliases=["P40", "PS40", "Coolant Pressure Sensor 40"],
            component_type="sensor",
            description="Coolant loop pressure sensor on Skid B. Completely unrelated to HPU discharge circuit.",
            location="Coolant Loop, Skid B",
            status="Active",
            source_references=["component_register.xlsx", "configuration_export.json"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 5",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="PLC-03",
            canonical_name="HCS Controller PLC-03",
            aliases=["PLC03", "Aegis Controller", "Controller", "HCS Controller"],
            component_type="controller",
            description="Supervises startup sequencing, monitoring, interlocks, and alarms.",
            location="Control Cabinet 1",
            status="Active",
            source_references=["component_register.xlsx", "operator_manual.pdf", "system_diagram_hydraulic.pdf"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 6",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="MAIN_RESERVOIR",
            canonical_name="Main Hydraulic Fluid Reservoir",
            aliases=["Main Reservoir", "Reservoir"],
            component_type="reservoir",
            description="Primary fluid reservoir supplying hydraulic fluid to the HPU pump suction.",
            location="Line 4 Press Skid",
            status="Active",
            source_references=["system_diagram_hydraulic.pdf", "training_slide_excerpt.pptx"],
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Rect: (270.1, 415.2, 334.7, 427.6)",
                extraction_method="vector_geometry",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="AUX_RESERVOIR",
            canonical_name="Auxiliary Fluid Reservoir",
            aliases=["Aux Reservoir", "Auxiliary Reservoir"],
            component_type="reservoir",
            description="Line 4/5 specific auxiliary reservoir topping up main reservoir during peak press demand. Omitted from standard Operator Manual.",
            location="Line 4 / Line 5 Peak Demand Bay",
            status="Active",
            source_references=["system_diagram_hydraulic.pdf", "training_slide_excerpt.pptx"],
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Rect: (447.2, 410.2, 488.8, 433.6)",
                extraction_method="vector_geometry",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="TB-7",
            canonical_name="Terminal Block 7",
            aliases=["TB7", "Terminal Block 7"],
            component_type="electrical",
            description="Control cabinet terminal block providing wiring interface for PS-04A 4-20mA sensor loop.",
            location="Control Cabinet 1",
            status="Active",
            source_references=["component_register.xlsx", "wiring_diagram.pdf"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 10",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="Q1",
            canonical_name="Main Disconnect Switch Q1",
            aliases=["Disconnect Q1", "Q1"],
            component_type="electrical",
            description="Incoming 3-phase power disconnect switch (480V 3-phase).",
            location="Control Cabinet 1",
            status="Active",
            source_references=["component_register.xlsx", "system_diagram_electrical.png"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 11",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="T1",
            canonical_name="Control Power Transformer T1",
            aliases=["Transformer T1", "T1"],
            component_type="electrical",
            description="Step-down transformer converting 480V to 120V AC for control power.",
            location="Control Cabinet 1",
            status="Active",
            source_references=["component_register.xlsx", "system_diagram_electrical.png"],
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 12",
                extraction_method="openpyxl",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="A17",
            canonical_name="Alarm A17: Hydraulic Pressure Low",
            aliases=["Alarm A17", "A17"],
            component_type="alarm",
            description="Triggers when hydraulic pressure drops below 150 bar. Requires Shutdown Procedure 4.7 if persistent > 10 s.",
            location="N/A (software alarm)",
            status="Active",
            source_references=["alarm_reference.pdf", "screen_02_alarms.png", "ECN-1058.pdf"],
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Table",
                extraction_method="pdf_native",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="A18",
            canonical_name="Alarm A18: Hydraulic Pressure High",
            aliases=["Alarm A18", "A18"],
            component_type="alarm",
            description="Triggers when hydraulic pressure exceeds 220 bar. Requires immediate HPU stop.",
            location="N/A (software alarm)",
            status="Active",
            source_references=["alarm_reference.pdf"],
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Table",
                extraction_method="pdf_native",
                confidence=1.0
            )
        ),
        ComponentEntity(
            component_id="A19",
            canonical_name="Alarm A19: Pressure Sensor Signal Invalid",
            aliases=["Alarm A19", "A19"],
            component_type="alarm",
            description="Triggers when sensor signal is invalid or drift exceeds tolerance (drift issue resolved by PS-04A).",
            location="N/A (software alarm)",
            status="Active",
            source_references=["alarm_reference.pdf", "ECN-1042.pdf"],
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Table",
                extraction_method="pdf_native",
                confidence=1.0
            )
        )
    ]

    for comp in components:
        db.insert_component(comp)
    print(f"   Inserted {len(components)} canonical components.")

    # 3. POPULATE FACTS (All 25 Verified Claims)
    print("3/5 Populating Facts...")
    facts = [
        # CLM-01 / Q01: Startup interlocks
        FactEntity(
            fact_id="FACT-01",
            subject="HPU",
            predicate="startup_interlock_iv21",
            object_value="OPEN",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Section 4.3 Starting the Hydraulic Power Unit",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="IV-21 must be verified OPEN prior to starting HPU."
        ),
        FactEntity(
            fact_id="FACT-02",
            subject="HPU",
            predicate="startup_interlock_fluid_level",
            object_value="NORMAL",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Section 4.3 Starting the Hydraulic Power Unit",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Hydraulic fluid level must be within normal band on sight glass."
        ),
        FactEntity(
            fact_id="FACT-03",
            subject="HPU",
            predicate="startup_interlock_estop",
            object_value="RESET",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Section 4.3 Starting the Hydraulic Power Unit",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Emergency stop circuit must be RESET."
        ),
        FactEntity(
            fact_id="FACT-04",
            subject="HPU",
            predicate="startup_interlock_access_panel",
            object_value="CLOSED",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Section 4.3 Starting the Hydraulic Power Unit",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="WARNING: Do not start unit with maintenance access panel removed."
        ),

        # CLM-02 / Q02, Q14, Q15, Q16: Normal operating pressure (Current SW 3.2+)
        FactEntity(
            fact_id="FACT-05",
            subject="HPU",
            predicate="normal_operating_pressure",
            object_value="200",
            unit="bar",
            applicable_revision_start="3.2",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="ECN-1042.pdf",
                page_number=1,
                section_name="Section 1 Description of Change",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Normal HPU discharge pressure setpoint revised from 180 bar to 200 bar effective SW 3.2."
        ),

        # CLM-03 / Q09, Q16, Q18: Historical operating pressure (SW 3.0 - 3.1)
        FactEntity(
            fact_id="FACT-06",
            subject="HPU",
            predicate="normal_operating_pressure",
            object_value="180",
            unit="bar",
            applicable_revision_start="3.0",
            applicable_revision_end="3.2",
            is_current=False,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Section 5 Normal Operating Ranges",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Normal discharge pressure on revisions prior to 3.2 was 180 bar, measured by PS-04."
        ),

        # CLM-03 / Field Notes informal discrepancy
        FactEntity(
            fact_id="FACT-07",
            subject="HPU",
            predicate="normal_operating_pressure",
            object_value="175",
            unit="bar",
            applicable_revision_start="3.2",
            is_current=False,
            provenance=ProvenanceRecord(
                source_document="site_survey_notes.docx",
                page_number=1,
                section_name="Site Visit Notes",
                extraction_method="docx_native",
                confidence=0.85
            ),
            verification_status=VerificationStatus.PARTIALLY_VERIFIED,
            notes="Informal observation by J. Torres using uncalibrated local gauge; unverified field note."
        ),

        # CLM-04 / Q03, Q10: Alarm A17 condition and threshold
        FactEntity(
            fact_id="FACT-08",
            subject="A17",
            predicate="trigger_threshold",
            object_value="< 150",
            unit="bar",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Reference Table",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Condition: Hydraulic pressure below 150 bar."
        ),
        FactEntity(
            fact_id="FACT-09",
            subject="A17",
            predicate="panel_color",
            object_value="RED",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Reference Table",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Panel Indication: RED."
        ),

        # CLM-05 / Q03: Alarm A17 possible causes
        FactEntity(
            fact_id="FACT-10",
            subject="A17",
            predicate="possible_causes",
            object_value="1. IV-21 closed or partially closed; 2. Low hydraulic fluid; 3. Pressure sensor signal invalid",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="alarm_reference.pdf",
                page_number=1,
                section_name="Alarm Reference Table",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Possible causes listed in AEG-AL-700."
        ),

        # CLM-06 / Q07: Alarm A17 persistent action
        FactEntity(
            fact_id="FACT-11",
            subject="A17",
            predicate="persistent_action",
            object_value="Execute Shutdown Procedure 4.7 if persistent > 10 seconds (close IV-21, confirm pressure decay, set POWER to OFF, tag out)",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="maintenance_manual.pdf",
                page_number=1,
                section_name="Section 4 Alarm A17 Response",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Transient A17 clears on own; persistent > 10s requires Shutdown Procedure 4.7."
        ),

        # CLM-07 / Q08: Controller reset restriction
        FactEntity(
            fact_id="FACT-12",
            subject="PLC-03",
            predicate="safe_reset_condition",
            object_value="Hydraulic pressure must be below 50 bar. Do NOT reset while pressure > 50 bar.",
            unit="bar",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=2,
                section_name="Section 7 Controller Reset",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Resetting under pressure (>50 bar) can cause uncommanded actuation of IV-21."
        ),

        # CLM-08 / Q04, Q17: PS-04 vs PS-04A distinction
        FactEntity(
            fact_id="FACT-13",
            subject="PS-04",
            predicate="identity_distinction",
            object_value="NOT identical to PS-04A. PS-04A has updated signal conditioning to correct 18-month drift, requires FW >= 3.2, and is not a form-fit-function replacement.",
            is_current=False,
            provenance=ProvenanceRecord(
                source_document="ECN-1042.pdf",
                page_number=1,
                section_name="Section 1 & 2",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="ECN-1042 explicitly states PS-04A is not a form-fit-function replacement for PS-04."
        ),

        # CLM-09 / Q05, Q14: ECN-1042 introducing PS-04A
        FactEntity(
            fact_id="FACT-14",
            subject="PS-04A",
            predicate="introducing_document",
            object_value="ECN-1042",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="ECN-1042.pdf",
                page_number=1,
                section_name="Header",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="ECN-1042 introduced sensor change from PS-04 to PS-04A effective SW 3.2."
        ),
        FactEntity(
            fact_id="FACT-15",
            subject="PS-04A",
            predicate="required_firmware_version",
            object_value=">= 3.2",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="ECN-1042.pdf",
                page_number=1,
                section_name="Section 1",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Controller firmware must be revision 3.2 or later to read PS-04A correctly."
        ),

        # CLM-10 / Q06: Direct schematic connections to PLC-03
        FactEntity(
            fact_id="FACT-16",
            subject="PLC-03",
            predicate="direct_schematic_connections",
            object_value="PS-04A and IV-21 (purple control/signal lines)",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Legend & Drawing Lines",
                extraction_method="vector_geometry",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Direct purple lines connect PLC-03 to PS-04A and IV-21. HPU connects via grey fluid path."
        ),

        # CLM-11 / Q11: IV-21 Location
        FactEntity(
            fact_id="FACT-17",
            subject="IV-21",
            predicate="location",
            object_value="Hydraulic Module",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 2",
                extraction_method="openpyxl",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Location specified in Component Register AEG-CR-700."
        ),

        # CLM-12 / Q12: Auxiliary Reservoir in training slides
        FactEntity(
            fact_id="FACT-18",
            subject="AUX_RESERVOIR",
            predicate="training_deck_introduction",
            object_value="Auxiliary Reservoir is introduced in training deck as Line 4/5 specific detail for peak demand top-up; explicitly omitted from standard Operator Manual",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="training_slide_excerpt.pptx",
                page_number=1,
                section_name="Slide 2 What is the HPU?",
                extraction_method="pptx_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Slide 2: 'tops up from a smaller Auxiliary Reservoir during peak demand. Note: Line 4/5-specific detail and is not covered in standard Operator Manual.'"
        ),

        # CLM-13 / Q13: Diagnostics screen sensor tag
        FactEntity(
            fact_id="FACT-19",
            subject="PS-04A",
            predicate="diagnostics_screen_tag",
            object_value="P.S.04-A",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="screen_03_diagnostics.png",
                page_number=1,
                cell_or_bbox="Sensor Diagnostics Tag Field",
                extraction_method="rapidocr_onnx",
                confidence=0.996
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Screen displays 'P.S.04-A', which corresponds to canonical component PS-04A as printed on physical unit label."
        ),

        # CLM-14 / Q14: Software Revision 3.2 Release Date
        FactEntity(
            fact_id="FACT-20",
            subject="SW_3_2",
            predicate="release_date",
            object_value="2025-09-30",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="revision_history.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Revision History, Row 3",
                extraction_method="openpyxl",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Revision 3.2 released 2025-09-30. PS-04 replaced by PS-04A; pressure changed from 180 to 200 bar."
        ),

        # CLM-15 / Q15: Configuration export threshold correspondence
        FactEntity(
            fact_id="FACT-21",
            subject="sensor_ps04a_threshold_bar",
            predicate="manual_terminology_correspondence",
            object_value="Normal operating pressure (or normal HPU discharge pressure setpoint = 200 bar)",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="configuration_export.json",
                page_number=1,
                section_name="Section: sensors",
                extraction_method="json_parser",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Corresponds to 200 bar normal operating pressure in Operator Manual Section 5."
        ),

        # CLM-16 / Q16: 200 bar applicability scope
        FactEntity(
            fact_id="FACT-22",
            subject="HPU",
            predicate="operating_pressure_applicability",
            object_value="Units on software revision >= 3.2 manufactured after 2024. Units running earlier software operate at 180 bar.",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="ECN-1042.pdf",
                page_number=1,
                section_name="Section 1",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="ECN-1042 confirms higher setpoint applies to post-2024 Series-7 units on SW >= 3.2."
        ),

        # CLM-17 / Q17: PS-40 distinction
        FactEntity(
            fact_id="FACT-23",
            subject="PS-40",
            predicate="identity_distinction",
            object_value="Located on Coolant Loop, Skid B. Completely unrelated to HPU discharge circuit. 0-10 bar sensor.",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 5",
                extraction_method="openpyxl",
                confidence=1.0
            ),
            verification_status=VerificationStatus.VERIFIED,
            notes="Explicitly marked unrelated to HPU circuit in component register and configuration export."
        ),

        # CLM-19 / Q23: 400V supply compatibility
        FactEntity(
            fact_id="FACT-24",
            subject="Q1",
            predicate="incoming_power_rating",
            object_value="480V, 3-Phase",
            unit="V",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="component_register.xlsx",
                page_number=1,
                cell_or_bbox="Sheet: Components, Row 11",
                extraction_method="openpyxl",
                confidence=1.0
            ),
            verification_status=VerificationStatus.PARTIALLY_VERIFIED,
            notes="Incoming disconnect Q1 is rated for 480V 3-phase. 400V operation is not documented (Category C)."
        ),

        # CLM-20 / Q19: PS-04A operating temperature (Category A: Absent)
        FactEntity(
            fact_id="FACT-25",
            subject="PS-04A",
            predicate="continuous_operating_temperature_max",
            object_value="NOT_FOUND",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="operator_manual.pdf",
                page_number=1,
                section_name="Specifications",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.NOT_FOUND,
            notes="Operating temperature for PS-04A is completely absent from all dataset documents (Category A unanswerable)."
        ),

        # CLM-21 / Q20: Voltage sensor calibration interval (Category B: False Premise)
        FactEntity(
            fact_id="FACT-26",
            subject="ELEC_SYSTEM",
            predicate="voltage_sensor_calibration_interval",
            object_value="FALSE_PREMISE_NOT_PRESENT",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="system_diagram_electrical.png",
                page_number=1,
                section_name="Diagram AEG-DWG-E02",
                extraction_method="rapidocr_onnx",
                confidence=1.0
            ),
            verification_status=VerificationStatus.NOT_FOUND,
            notes="No voltage sensor exists on electrical diagram AEG-DWG-E02 (Category B false premise)."
        ),

        # CLM-22 / Q21: ECN-1058 approver (Category D: Omitted Companion Document)
        FactEntity(
            fact_id="FACT-27",
            subject="ECN-1058",
            predicate="approver_signature",
            object_value="OMITTED_BLANK",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="ECN-1058.pdf",
                page_number=1,
                section_name="Header",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.PARTIALLY_VERIFIED,
            notes="ECN-1058 is marked 'Released' but individual approval signature block is blank (Category D)."
        ),

        # CLM-23 / Q22: IV-21 MTBF (Category A: Absent)
        FactEntity(
            fact_id="FACT-28",
            subject="IV-21",
            predicate="mean_time_between_failures",
            object_value="NOT_FOUND",
            is_current=True,
            provenance=ProvenanceRecord(
                source_document="maintenance_manual.pdf",
                page_number=1,
                section_name="Section 1",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            verification_status=VerificationStatus.NOT_FOUND,
            notes="MTBF / reliability engineering metrics are completely absent from documentation (Category A unanswerable)."
        )
    ]

    for fact in facts:
        db.insert_fact(fact)
    print(f"   Inserted {len(facts)} verified facts.")

    # 4. POPULATE DIAGRAM RELATIONSHIPS
    print("4/5 Populating Topological Relationships...")
    relationships = [
        RelationshipEntity(
            rel_id="REL-01",
            source_component="PLC-03",
            relationship_type="controls",
            target_component="PS-04A",
            line_type="solid_purple",
            endpoints="(230.4, 231.8) -> (187.2, 324.0)",
            drawing_reference="AEG-DWG-H01",
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Stroke RGB: [0.541, 0.294, 0.612]",
                extraction_method="vector_geometry",
                confidence=1.0
            ),
            notes="Purple control/signal line connects PLC-03 output boundary to PS-04A sensor boundary."
        ),
        RelationshipEntity(
            rel_id="REL-02",
            source_component="PLC-03",
            relationship_type="controls",
            target_component="IV-21",
            line_type="solid_purple",
            endpoints="(374.4, 231.8) -> (388.8, 324.0)",
            drawing_reference="AEG-DWG-H01",
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Stroke RGB: [0.541, 0.294, 0.612]",
                extraction_method="vector_geometry",
                confidence=1.0
            ),
            notes="Purple control line connects PLC-03 valve driver boundary to IV-21 solenoid driver boundary."
        ),
        RelationshipEntity(
            rel_id="REL-03",
            source_component="HPU",
            relationship_type="supplies_fluid_to",
            target_component="MAIN_RESERVOIR",
            line_type="solid_grey",
            endpoints="(302.4, 345.6) -> (302.4, 403.2)",
            drawing_reference="AEG-DWG-H01",
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Stroke RGB: [0.333, 0.333, 0.333]",
                extraction_method="vector_geometry",
                confidence=1.0
            ),
            notes="Grey hydraulic fluid path connects HPU pump suction to Main Reservoir."
        ),
        RelationshipEntity(
            rel_id="REL-04",
            source_component="MAIN_RESERVOIR",
            relationship_type="interconnects",
            target_component="AUX_RESERVOIR",
            line_type="solid_tan",
            endpoints="(374.4, 424.8) -> (410.4, 424.8)",
            drawing_reference="AEG-DWG-H01",
            provenance=ProvenanceRecord(
                source_document="system_diagram_hydraulic.pdf",
                page_number=1,
                cell_or_bbox="Stroke RGB: [0.690, 0.541, 0.306]",
                extraction_method="vector_geometry",
                confidence=1.0
            ),
            notes="Tan reservoir interconnect line connects Main Reservoir to Auxiliary Reservoir (Line 4/5 peak top-up)."
        ),
        RelationshipEntity(
            rel_id="REL-05",
            source_component="TB-7",
            relationship_type="wires_to",
            target_component="PS-04A",
            line_type="wiring_lead",
            endpoints="Terminal Block TB-7 (Connector J-14) -> PRESSURE XDCR (PS-04A)",
            drawing_reference="AEG-DWG-W03",
            provenance=ProvenanceRecord(
                source_document="wiring_diagram.pdf",
                page_number=1,
                cell_or_bbox="Drawing Boxes TB-7 and J-14",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            notes="Note 1 explicitly clarifies that field device labeled 'PRESSURE XDCR' at TB-7/J-14 is PS-04A."
        ),
        RelationshipEntity(
            rel_id="REL-06",
            source_component="TB-7",
            relationship_type="wires_to",
            target_component="IV-21",
            line_type="wiring_lead",
            endpoints="Terminal Block TB-7 (Connector J-15) -> IV-21 SOLENOID",
            drawing_reference="AEG-DWG-W03",
            provenance=ProvenanceRecord(
                source_document="wiring_diagram.pdf",
                page_number=1,
                cell_or_bbox="Drawing Box IV-21 SOLENOID",
                extraction_method="pdf_native",
                confidence=1.0
            ),
            notes="Wiring diagram connects TB-7 to IV-21 solenoid driver."
        ),
        RelationshipEntity(
            rel_id="REL-07",
            source_component="Q1",
            relationship_type="powers",
            target_component="T1",
            line_type="3_phase_ac",
            endpoints="Q1 Disconnect -> 30A Primary Fuses -> T1 Primary",
            drawing_reference="AEG-DWG-E02",
            provenance=ProvenanceRecord(
                source_document="system_diagram_electrical.png",
                page_number=1,
                cell_or_bbox="Top Power Distribution Rail",
                extraction_method="rapidocr_onnx",
                confidence=0.98
            ),
            notes="480V 3-phase incoming power feeds control transformer T1 through 30A primary fuses."
        ),
        RelationshipEntity(
            rel_id="REL-08",
            source_component="T1",
            relationship_type="powers",
            target_component="PLC-03",
            line_type="120v_ac",
            endpoints="T1 Secondary -> PLC-03 24VDC Power Supply",
            drawing_reference="AEG-DWG-E02",
            provenance=ProvenanceRecord(
                source_document="system_diagram_electrical.png",
                page_number=1,
                cell_or_bbox="Control Power Sub-circuit",
                extraction_method="rapidocr_onnx",
                confidence=0.98
            ),
            notes="120V AC secondary supply powers the 24V DC power supply feeding PLC-03."
        )
    ]

    for rel in relationships:
        db.insert_relationship(rel)
    print(f"   Inserted {len(relationships)} topological relationships.")

    # 5. DETECT CONFLICTS AND PERSIST
    print("5/5 Running Conflict Detection Engine...")
    detector = ConflictDetector(documents=doc_entities)
    all_facts = db.get_all_facts()
    conflicts = detector.detect_conflicts(all_facts)

    for conf in conflicts:
        db.insert_conflict(conf)
    print(f"   Detected and persisted {len(conflicts)} conflict records.")

    # 6. EXPORT IKR JSON
    ikr_export = db.export_ikr_to_json()
    print(f"IKR Export successfully written to {KNOWLEDGE_DIR / 'ikr_export.json'} (Total facts: {ikr_export.total_facts}, Total conflicts: {ikr_export.total_conflicts}).")

if __name__ == "__main__":
    db = KnowledgeDatabase()
    populate_database(db)
