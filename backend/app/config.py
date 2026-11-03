"""
Aegis Knowledge System - Global Configuration & Trust Levels
"""
import os
from pathlib import Path
from enum import IntEnum

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "aegis-dataset"
STORAGE_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = STORAGE_DIR / "knowledge"
PROCESSED_DIR = STORAGE_DIR / "processed"
EVALUATION_DIR = STORAGE_DIR / "evaluation"

for d in [STORAGE_DIR, KNOWLEDGE_DIR, PROCESSED_DIR, EVALUATION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class TrustTier(IntEnum):
    """
    Source Reliability Hierarchy (Tiers 1 to 6)
    Tier 1 is highest authority; Tier 6 is noise.
    """
    TIER_1_MASTER = 1      # ECNs, Master Registers, Machine Config Exports
    TIER_2_OFFICIAL = 2    # Current Official Manuals, Schematics, Verified Calibration Records
    TIER_3_OPERATIONAL = 3 # Operational HMI, Verified Training Decks
    TIER_4_LEGACY = 4      # Superseded documentation (valid only for historical revision queries)
    TIER_5_INFORMAL = 5    # Unreviewed field notes, informal reports
    TIER_6_NOISE = 6       # Unrelated background material (MSDS)

DOCUMENT_METADATA_REGISTRY = {
    "ECN-1042.pdf": {
        "doc_id": "ECN-1042",
        "title": "Engineering Change Notice - Sensor Replacement & Pressure Update",
        "trust_tier": TrustTier.TIER_1_MASTER,
        "revision": "3.2",
        "effective_date": "2025-09-30",
        "status": "Released",
        "category": "engineering_bulletin"
    },
    "ECN-1058.pdf": {
        "doc_id": "ECN-1058",
        "title": "Engineering Change Notice - Alarm A17 Threshold Reference Correction",
        "trust_tier": TrustTier.TIER_1_MASTER,
        "revision": "3.2.1",
        "effective_date": "2025-11-18",
        "status": "Released",
        "category": "engineering_bulletin"
    },
    "component_register.xlsx": {
        "doc_id": "AEG-CR-700",
        "title": "Aegis Series-7 Master Component Register",
        "trust_tier": TrustTier.TIER_1_MASTER,
        "revision": "Current",
        "effective_date": "2025-09-30",
        "status": "Active",
        "category": "master_register"
    },
    "revision_history.xlsx": {
        "doc_id": "AEG-RH-700",
        "title": "Aegis Series-7 Software & Hardware Revision Timeline",
        "trust_tier": TrustTier.TIER_1_MASTER,
        "revision": "3.2.1",
        "effective_date": "2025-11-18",
        "status": "Active",
        "category": "timeline_authority"
    },
    "configuration_export.json": {
        "doc_id": "CFG-PLC03-321",
        "title": "HCS Controller PLC-03 Machine Configuration Export",
        "trust_tier": TrustTier.TIER_1_MASTER,
        "revision": "3.2.1",
        "effective_date": "2026-02-03",
        "status": "Live Production",
        "category": "machine_export"
    },
    "operator_manual.pdf": {
        "doc_id": "AEG-OM-700",
        "title": "Aegis Series-7 HCS Operator Manual",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Rev 4",
        "effective_date": "2025-09-30",
        "status": "Active (Applies to SW >= 3.2)",
        "category": "official_manual"
    },
    "maintenance_manual.pdf": {
        "doc_id": "AEG-MM-700",
        "title": "Aegis Series-7 HCS Maintenance Manual",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Rev 3",
        "effective_date": "2025-09-30",
        "status": "Active",
        "category": "official_manual"
    },
    "alarm_reference.pdf": {
        "doc_id": "AEG-AL-700",
        "title": "Aegis Series-7 HCS Alarm Reference",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Rev 5",
        "effective_date": "2025-11-18",
        "status": "Active (incorporates ECN-1058)",
        "category": "official_reference"
    },
    "system_diagram_hydraulic.pdf": {
        "doc_id": "AEG-DWG-H01",
        "title": "Aegis Series-7 HCS Hydraulic Schematic",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Current",
        "effective_date": "2025-09-30",
        "status": "Active",
        "category": "engineering_drawing"
    },
    "wiring_diagram.pdf": {
        "doc_id": "AEG-DWG-W03",
        "title": "Aegis Series-7 HCS Instrumentation Wiring Diagram",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Current",
        "effective_date": "2025-09-30",
        "status": "Active",
        "category": "engineering_drawing"
    },
    "system_diagram_electrical.png": {
        "doc_id": "AEG-DWG-E02",
        "title": "Aegis Series-7 HCS Electrical Schematic",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Current",
        "effective_date": "2025-09-30",
        "status": "Active",
        "category": "engineering_drawing"
    },
    "scanned_appendix_calibration.pdf": {
        "doc_id": "CAL-APP-C",
        "title": "Appendix C - Sensor Calibration Record",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Uncontrolled Binder Copy",
        "effective_date": "2026-01-09",
        "status": "Active",
        "category": "calibration_record"
    },
    "terminology_glossary.docx": {
        "doc_id": "AEG-GL-700",
        "title": "Aegis Series-7 HCS Terminology Glossary",
        "trust_tier": TrustTier.TIER_2_OFFICIAL,
        "revision": "Rev 2",
        "effective_date": "2024-03-01",
        "status": "Incomplete Reference",
        "category": "official_reference"
    },
    "screen_01_home.png": {
        "doc_id": "HMI-SCR-01",
        "title": "HMI Screen 01 - System Home & Interlocks",
        "trust_tier": TrustTier.TIER_3_OPERATIONAL,
        "revision": "SW Rev 3.2",
        "effective_date": "2026-01-09",
        "status": "Active",
        "category": "hmi_screen"
    },
    "screen_02_alarms.png": {
        "doc_id": "HMI-SCR-02",
        "title": "HMI Screen 02 - Active Alarm List",
        "trust_tier": TrustTier.TIER_3_OPERATIONAL,
        "revision": "SW Rev 3.2",
        "effective_date": "2026-01-09",
        "status": "Active",
        "category": "hmi_screen"
    },
    "screen_03_diagnostics.png": {
        "doc_id": "HMI-SCR-03",
        "title": "HMI Screen 03 - Sensor Diagnostics",
        "trust_tier": TrustTier.TIER_3_OPERATIONAL,
        "revision": "SW Rev 3.2 / Firmware 3.2.1",
        "effective_date": "2026-01-09",
        "status": "Active",
        "category": "hmi_screen"
    },
    "training_slide_excerpt.pptx": {
        "doc_id": "TRN-SLD-07",
        "title": "New Operator Orientation - HPU Basics",
        "trust_tier": TrustTier.TIER_3_OPERATIONAL,
        "revision": "Excerpt Slides 4-6",
        "effective_date": "2025-06-01",
        "status": "Active (Line 4/5 specific detail)",
        "category": "training_material"
    },
    "legacy_manual_v1.html": {
        "doc_id": "AEG-OM-700-V1",
        "title": "Aegis Series-7 Operator Manual (Legacy v1 export)",
        "trust_tier": TrustTier.TIER_4_LEGACY,
        "revision": "Rev 1",
        "effective_date": "2023-06-02",
        "status": "Partially Superseded (Applies to SW 3.0-3.1 only)",
        "category": "legacy_manual"
    },
    "site_survey_notes.docx": {
        "doc_id": "FLD-NOT-04",
        "title": "Site Visit Notes - Line 4 HPU (J. Torres)",
        "trust_tier": TrustTier.TIER_5_INFORMAL,
        "revision": "Uncontrolled / Undated",
        "effective_date": "Unknown",
        "status": "Unreviewed Notebook",
        "category": "field_notes"
    },
    "safety_data_sheet_hydraulic_fluid.pdf": {
        "doc_id": "HF32-SDS-06",
        "title": "Safety Data Sheet - HydroFluid-32",
        "trust_tier": TrustTier.TIER_6_NOISE,
        "revision": "Rev 2025-02-11",
        "effective_date": "2025-02-11",
        "status": "Product SDS Only",
        "category": "noise_reference"
    }
}

