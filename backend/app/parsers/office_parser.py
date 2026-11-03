"""
Office Document Parser
Handles Microsoft Word (.docx) and PowerPoint (.pptx) documents.
"""
from pathlib import Path
from typing import List
from docx import Document
from pptx import Presentation

from backend.app.parsers.base_parser import BaseParser, ExtractedDocument, DocumentBlock, TableBlock, BlockType
from backend.app.config import DOCUMENT_METADATA_REGISTRY, TrustTier

class OfficeParser(BaseParser):
    def parse(self, file_path: Path) -> ExtractedDocument:
        fn = file_path.name
        ext = file_path.suffix.lower()
        meta = DOCUMENT_METADATA_REGISTRY.get(fn, {
            "doc_id": fn,
            "trust_tier": TrustTier.TIER_2_OFFICIAL,
            "revision": None,
            "effective_date": None
        })

        blocks_out: List[DocumentBlock] = []
        tables_out: List[TableBlock] = []
        full_text_lines: List[str] = []
        errors: List[str] = []
        block_counter = 0

        if ext == ".docx":
            doc = Document(file_path)
            current_section = "General"
            
            # Paragraphs
            for p_idx, para in enumerate(doc.paragraphs, start=1):
                txt = para.text.strip()
                if not txt:
                    continue
                block_counter += 1
                full_text_lines.append(txt)
                
                b_type = BlockType.TEXT
                style_name = getattr(para.style, "name", "") or ""
                if len(txt) < 80 and (style_name.startswith("Heading") or p_idx == 1):
                    b_type = BlockType.HEADING
                    current_section = txt

                blocks_out.append(DocumentBlock(
                    block_id=f"{fn}_p{block_counter}",
                    block_type=b_type,
                    text=txt,
                    page_number=1,
                    section_name=current_section,
                    metadata={"para_index": p_idx}
                ))

            # Tables in DOCX (e.g. Terminology Glossary table)
            for t_idx, table in enumerate(doc.tables, start=1):
                if not table.rows:
                    continue
                headers = [c.text.strip() for c in table.rows[0].cells]
                rows = []
                for row in table.rows[1:]:
                    row_vals = [c.text.strip() for c in row.cells]
                    rows.append(row_vals)
                    block_counter += 1
                    row_desc = f"Glossary Term: '{row_vals[0]}' = {row_vals[1] if len(row_vals) > 1 else ''}"
                    full_text_lines.append(row_desc)
                    blocks_out.append(DocumentBlock(
                        block_id=f"{fn}_t{t_idx}_r{block_counter}",
                        block_type=BlockType.TABLE,
                        text=row_desc,
                        page_number=1,
                        section_name="Glossary Terms"
                    ))

                tables_out.append(TableBlock(
                    table_id=f"{fn}_table_{t_idx}",
                    headers=headers,
                    rows=rows,
                    page_number=1,
                    caption=f"Word Table {t_idx}"
                ))

        elif ext == ".pptx":
            prs = Presentation(file_path)
            for slide_idx, slide in enumerate(prs.slides, start=1):
                slide_texts = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            t = paragraph.text.strip()
                            if t:
                                slide_texts.append(t)
                
                if slide_texts:
                    slide_content = "\n".join(slide_texts)
                    full_text_lines.append(f"[Slide {slide_idx}]\n" + slide_content)
                    block_counter += 1
                    
                    # First text as heading / title
                    slide_title = slide_texts[0] if len(slide_texts[0]) < 80 else f"Slide {slide_idx}"
                    blocks_out.append(DocumentBlock(
                        block_id=f"{fn}_slide_{slide_idx}",
                        block_type=BlockType.TEXT,
                        text=slide_content,
                        page_number=slide_idx,
                        section_name=slide_title,
                        metadata={"slide_number": slide_idx, "items_count": len(slide_texts)}
                    ))

        return ExtractedDocument(
            filename=fn,
            file_type="office_docx" if ext == ".docx" else "presentation_pptx",
            doc_id=meta["doc_id"],
            trust_tier=int(meta["trust_tier"]),
            revision=meta.get("revision"),
            effective_date=meta.get("effective_date"),
            blocks=blocks_out,
            tables=tables_out,
            raw_text="\n\n".join(full_text_lines),
            metadata={"blocks_count": len(blocks_out)},
            extraction_errors=errors
        )
