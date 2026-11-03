"""
Legacy HTML Manual Parser
Parses CMS HTML exports, extracts headings, warnings, tables, and supersession banners.
"""
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup

from backend.app.parsers.base_parser import BaseParser, ExtractedDocument, DocumentBlock, TableBlock, BlockType
from backend.app.config import DOCUMENT_METADATA_REGISTRY, TrustTier

class LegacyHtmlParser(BaseParser):
    def parse(self, file_path: Path) -> ExtractedDocument:
        fn = file_path.name
        meta = DOCUMENT_METADATA_REGISTRY.get(fn, {
            "doc_id": fn,
            "trust_tier": TrustTier.TIER_4_LEGACY,
            "revision": "Rev 1",
            "effective_date": "2023-06-02"
        })

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        blocks_out: List[DocumentBlock] = []
        tables_out: List[TableBlock] = []
        full_text_lines: List[str] = []
        errors: List[str] = []
        block_counter = 0

        # Title
        if soup.title:
            t_str = soup.title.string.strip()
            blocks_out.append(DocumentBlock(
                block_id=f"{fn}_title",
                block_type=BlockType.HEADING,
                text=t_str,
                page_number=1,
                section_name="Title"
            ))
            full_text_lines.append(t_str)

        current_section = "Introduction"

        for elem in soup.find_all(["h1", "h2", "h3", "p", "div", "table", "ul", "ol"]):
            text = elem.get_text().strip()
            if not text:
                continue

            if elem.name in ["h1", "h2", "h3"]:
                current_section = text
                block_counter += 1
                blocks_out.append(DocumentBlock(
                    block_id=f"{fn}_b{block_counter}",
                    block_type=BlockType.HEADING,
                    text=text,
                    page_number=1,
                    section_name=current_section
                ))
                full_text_lines.append(f"\n--- {text} ---")

            elif elem.name == "table":
                # Extract HTML table
                rows = []
                for tr in elem.find_all("tr"):
                    cells = [td.get_text().strip() for td in tr.find_all(["td", "th"])]
                    if cells:
                        rows.append(cells)
                if rows:
                    headers = rows[0]
                    data_rows = rows[1:] if len(rows) > 1 else []
                    tables_out.append(TableBlock(
                        table_id=f"{fn}_table_{len(tables_out)+1}",
                        headers=headers,
                        rows=data_rows,
                        page_number=1,
                        caption=f"Table under {current_section}"
                    ))
                    table_summary = f"Table in {current_section}: " + " | ".join(
                        ", ".join(r) for r in data_rows
                    )
                    block_counter += 1
                    blocks_out.append(DocumentBlock(
                        block_id=f"{fn}_b{block_counter}",
                        block_type=BlockType.TABLE,
                        text=table_summary,
                        page_number=1,
                        section_name=current_section
                    ))
                    full_text_lines.append(table_summary)

            elif elem.name in ["p", "div"]:
                # Check for warnings or supersession banners
                b_type = BlockType.TEXT
                if "WARNING:" in text or "supersede" in text.lower() or "legacy export" in text.lower():
                    b_type = BlockType.WARNING

                block_counter += 1
                blocks_out.append(DocumentBlock(
                    block_id=f"{fn}_b{block_counter}",
                    block_type=b_type,
                    text=text,
                    page_number=1,
                    section_name=current_section
                ))
                full_text_lines.append(text)

        return ExtractedDocument(
            filename=fn,
            file_type="legacy_html",
            doc_id=meta["doc_id"],
            trust_tier=int(meta["trust_tier"]),
            revision=meta.get("revision"),
            effective_date=meta.get("effective_date"),
            blocks=blocks_out,
            tables=tables_out,
            raw_text="\n\n".join(full_text_lines),
            metadata={"elements_parsed": block_counter},
            extraction_errors=errors
        )

