"""
Unit and Integration Tests for Document Ingestion Pipeline
"""
import pytest
from pathlib import Path
from backend.app.config import DATA_DIR
from backend.app.ingestion.document_ingestor import DocumentIngestionEngine
from backend.app.parsers import (
    DigitalPdfParser,
    ScanOcrParser,
    DiagramParser,
    TabularParser,
    OfficeParser,
    LegacyHtmlParser
)

@pytest.fixture(scope="module")
def ingestion_engine():
    return DocumentIngestionEngine(DATA_DIR)

def test_full_dataset_ingestion(ingestion_engine):
    """Verify that all 20 dataset files are ingested with 0 failures."""
    summary = ingestion_engine.ingest_all()
    assert summary["total_files"] == 20, f"Expected 20 files, found {summary['total_files']}"
    assert summary["processed_files"] == 20, f"Expected 20 processed, got {summary['processed_files']}"
    assert summary["failed_files"] == 0, f"Failed files: {summary['failed_files']}"
    assert summary["total_blocks"] > 100, "Should extract substantial number of blocks"
    assert summary["total_tables"] >= 5, "Should extract tabular structures"
    assert summary["total_connections"] >= 4, "Should extract schematic topological connections"

def test_digital_pdf_parser():
    """Verify digital PDF parser extracts sections and 200 bar setpoint."""
    parser = DigitalPdfParser()
    p = DATA_DIR / "manuals" / "operator_manual.pdf"
    doc = parser.parse(p)
    assert doc.doc_id == "AEG-OM-700"
    assert doc.trust_tier == 2
    assert "200 bar" in doc.raw_text
    assert "IV-21 is OPEN" in doc.raw_text
    assert len(doc.blocks) > 0

def test_scanned_pdf_ocr():
    """Verify OCR extracts calibration table and disclaimer from scanned appendix."""
    parser = ScanOcrParser()
    p = DATA_DIR / "scans" / "scanned_appendix_calibration.pdf"
    doc = parser.parse(p)
    assert doc.doc_id == "CAL-APP-C"
    assert len(doc.blocks) > 0
    # Check for calibration points
    assert "200" in doc.raw_text
    assert "PS-04A" in doc.raw_text or "PS-04" in doc.raw_text

def test_hydraulic_schematic_topology():
    """Verify vector parser extracts direct control connections from PLC-03 to PS-04A and IV-21."""
    parser = DiagramParser()
    p = DATA_DIR / "diagrams" / "system_diagram_hydraulic.pdf"
    doc = parser.parse(p)
    assert doc.doc_id == "AEG-DWG-H01"
    
    # Check topological connections
    connections = [(c.source_component, c.target_component) for c in doc.connections]
    assert ("PLC-03", "PS-04A") in connections, "PLC-03 must connect to PS-04A via purple line"
    assert ("PLC-03", "IV-21") in connections, "PLC-03 must connect to IV-21 via purple line"

def test_component_register_and_revision_history():
    """Verify Excel parser extracts component statuses and revision dates."""
    parser = TabularParser()
    p_comp = DATA_DIR / "reference" / "component_register.xlsx"
    doc_comp = parser.parse(p_comp)
    assert len(doc_comp.tables) > 0
    assert "PS-04" in doc_comp.raw_text
    assert "PS-04A" in doc_comp.raw_text
    assert "Coolant Loop" in doc_comp.raw_text  # PS-40 location

    p_rev = DATA_DIR / "reference" / "revision_history.xlsx"
    doc_rev = parser.parse(p_rev)
    assert "2025-09-30" in doc_rev.raw_text  # Rev 3.2 release date

def test_configuration_export_json():
    """Verify machine JSON parser extracts thresholds and revision rules."""
    parser = TabularParser()
    p_cfg = DATA_DIR / "configuration" / "configuration_export.json"
    doc_cfg = parser.parse(p_cfg)
    assert "sensor_ps04a_threshold_bar" in doc_cfg.raw_text
    assert "200" in doc_cfg.raw_text
    assert "150" in doc_cfg.raw_text  # Low alarm

def test_office_and_html_parsers():
    """Verify Word, PowerPoint, and Legacy HTML parsers."""
    office_parser = OfficeParser()
    p_slide = DATA_DIR / "extra" / "training_slide_excerpt.pptx"
    doc_slide = office_parser.parse(p_slide)
    assert "Auxiliary Reservoir" in doc_slide.raw_text

    html_parser = LegacyHtmlParser()
    p_html = DATA_DIR / "manuals" / "legacy_manual_v1.html"
    doc_html = html_parser.parse(p_html)
    assert "180 bar" in doc_html.raw_text
    assert doc_html.trust_tier == 4

