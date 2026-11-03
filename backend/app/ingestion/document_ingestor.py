"""
Document Ingestion Coordinator
Orchestrates multi-format parsing, validates completeness, and persists extracted documents.
"""
from pathlib import Path
from typing import List, Dict, Any
import json
import time

from backend.app.config import DATA_DIR, PROCESSED_DIR, DOCUMENT_METADATA_REGISTRY
from backend.app.parsers import (
    ExtractedDocument,
    DigitalPdfParser,
    ScanOcrParser,
    DiagramParser,
    TabularParser,
    OfficeParser,
    LegacyHtmlParser
)

class DocumentIngestionEngine:
    def __init__(self, dataset_dir: Path = DATA_DIR):
        self.dataset_dir = Path(dataset_dir)
        self.pdf_parser = DigitalPdfParser()
        self.ocr_parser = ScanOcrParser()
        self.diagram_parser = DiagramParser()
        self.tabular_parser = TabularParser()
        self.office_parser = OfficeParser()
        self.html_parser = LegacyHtmlParser()

    def get_parser_for_file(self, file_path: Path):
        fn = file_path.name
        ext = file_path.suffix.lower()

        # Specific diagram and schematic handlers
        if fn in ["system_diagram_hydraulic.pdf", "wiring_diagram.pdf", "system_diagram_electrical.png"]:
            return self.diagram_parser

        # Scanned PDF or Screenshots
        if fn == "scanned_appendix_calibration.pdf" or ext in [".png", ".jpg", ".jpeg"]:
            return self.ocr_parser

        # Digital PDFs
        if ext == ".pdf":
            return self.pdf_parser

        # Tabular registers & machine JSON
        if ext in [".xlsx", ".xls", ".json"]:
            return self.tabular_parser

        # Office formats
        if ext in [".docx", ".pptx"]:
            return self.office_parser

        # Legacy HTML
        if ext in [".html", ".htm"]:
            return self.html_parser

        raise ValueError(f"Unsupported file format: {file_path}")

    def ingest_single_file(self, file_path: Path) -> ExtractedDocument:
        parser = self.get_parser_for_file(file_path)
        return parser.parse(file_path)

    def ingest_all(self) -> Dict[str, Any]:
        """Ingest all 20 files in aegis-dataset and return comprehensive results."""
        start_time = time.time()
        extracted_docs: List[ExtractedDocument] = []
        summary = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "total_blocks": 0,
            "total_tables": 0,
            "total_connections": 0,
            "files": [],
            "duration_seconds": 0.0
        }

        # Locate all files
        all_files = sorted(list(self.dataset_dir.rglob("*.*")))
        all_files = [f for f in all_files if f.is_file() and not f.name.startswith(".")]

        summary["total_files"] = len(all_files)

        for fpath in all_files:
            try:
                doc = self.ingest_single_file(fpath)
                extracted_docs.append(doc)
                summary["processed_files"] += 1
                summary["total_blocks"] += len(doc.blocks)
                summary["total_tables"] += len(doc.tables)
                summary["total_connections"] += len(doc.connections)
                
                summary["files"].append({
                    "filename": doc.filename,
                    "doc_id": doc.doc_id,
                    "file_type": doc.file_type,
                    "trust_tier": doc.trust_tier,
                    "revision": doc.revision,
                    "blocks_count": len(doc.blocks),
                    "tables_count": len(doc.tables),
                    "connections_count": len(doc.connections),
                    "raw_text_length": len(doc.raw_text),
                    "status": "SUCCESS"
                })
            except Exception as e:
                summary["failed_files"] += 1
                summary["files"].append({
                    "filename": fpath.name,
                    "status": "ERROR",
                    "error_message": str(e)
                })

        summary["duration_seconds"] = round(time.time() - start_time, 2)

        # Cache extracted documents to disk for subsequent stages
        cache_path = PROCESSED_DIR / "extracted_docs.json"
        with open(cache_path, "w", encoding="utf-8") as fp:
            json.dump([doc.model_dump() for doc in extracted_docs], fp, indent=2, ensure_ascii=False)

        summary["cache_path"] = str(cache_path)
        return summary

