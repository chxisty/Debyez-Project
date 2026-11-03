"""
Born-Digital PDF Parser using PyMuPDF (fitz)
Preserves page numbers, headings, warnings, and tabular sections.
"""
from pathlib import Path
from typing import List
import pymupdf as fitz
from backend.app.parsers.base_parser import BaseParser, ExtractedDocument, DocumentBlock, TableBlock, BlockType
from backend.app.config import DOCUMENT_METADATA_REGISTRY, TrustTier

class DigitalPdfParser(BaseParser):
    def parse(self, file_path: Path) -> ExtractedDocument:
        fn = file_path.name
        meta = DOCUMENT_METADATA_REGISTRY.get(fn, {
            "doc_id": fn,
            "trust_tier": TrustTier.TIER_2_OFFICIAL,
            "revision": None,
            "effective_date": None
        })
        
        doc = fitz.open(file_path)
        blocks_out: List[DocumentBlock] = []
        tables_out: List[TableBlock] = []
        full_text_parts: List[str] = []
        errors: List[str] = []
        
        current_section = "Header"
        block_counter = 0

        for page_idx, page in enumerate(doc, start=1):
            page_text = page.get_text()
            full_text_parts.append(f"[Page {page_idx}]\n" + page_text)
            
            # Check for native tables using PyMuPDF table finder
            try:
                tabs = page.find_tables()
                if tabs and len(tabs.tables) > 0:
                    for t_idx, tab in enumerate(tabs.tables):
                        extracted_tab = tab.extract()
                        if extracted_tab and len(extracted_tab) > 1:
                            headers = [str(c or "").strip() for c in extracted_tab[0]]
                            rows = [[str(c or "").strip() for c in r] for r in extracted_tab[1:]]
                            tables_out.append(TableBlock(
                                table_id=f"{fn}_p{page_idx}_t{t_idx+1}",
                                headers=headers,
                                rows=rows,
                                page_number=page_idx,
                                caption=f"Table on page {page_idx}"
                            ))
            except Exception as e:
                errors.append(f"Table detection notice on page {page_idx}: {str(e)}")

            # Extract layout text blocks with detailed metadata
            raw_blocks = page.get_text("blocks")
            for b in raw_blocks:
                # b format: (x0, y0, x1, y1, text, block_no, block_type)
                text = b[4].strip()
                if not text:
                    continue
                
                block_counter += 1
                b_type = BlockType.TEXT
                
                # Detect Section Headings (e.g., '1. Overview', '4. Operating Procedures')
                lines = text.split("\n")
                first_line = lines[0].strip()
                if (first_line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")) or
                    "Manual" in first_line or "Notice" in first_line or "Reference" in first_line):
                    if len(first_line) < 80:
                        current_section = first_line
                        b_type = BlockType.HEADING

                # Detect Safety Warnings
                if "WARNING:" in text or "CAUTION:" in text or "DANGER:" in text:
                    b_type = BlockType.WARNING

                blocks_out.append(DocumentBlock(
                    block_id=f"{fn}_b{block_counter}",
                    block_type=b_type,
                    text=text,
                    page_number=page_idx,
                    section_name=current_section,
                    bbox=[round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
                    confidence=1.0,
                    metadata={"line_count": len(lines)}
                ))

        return ExtractedDocument(
            filename=fn,
            file_type="pdf_digital",
            doc_id=meta["doc_id"],
            trust_tier=int(meta["trust_tier"]),
            revision=meta.get("revision"),
            effective_date=meta.get("effective_date"),
            blocks=blocks_out,
            tables=tables_out,
            raw_text="\n\n".join(full_text_parts),
            metadata={"total_pages": len(doc)},
            extraction_errors=errors
        )

