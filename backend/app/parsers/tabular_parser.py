"""
Tabular and Structured Data Parser
Handles Excel registers (openpyxl/pandas) and JSON machine configuration exports.
"""
from pathlib import Path
from typing import List
import json
import openpyxl

from backend.app.parsers.base_parser import BaseParser, ExtractedDocument, DocumentBlock, TableBlock, BlockType
from backend.app.config import DOCUMENT_METADATA_REGISTRY, TrustTier

class TabularParser(BaseParser):
    def parse(self, file_path: Path) -> ExtractedDocument:
        fn = file_path.name
        ext = file_path.suffix.lower()
        meta = DOCUMENT_METADATA_REGISTRY.get(fn, {
            "doc_id": fn,
            "trust_tier": TrustTier.TIER_1_MASTER,
            "revision": None,
            "effective_date": None
        })

        blocks_out: List[DocumentBlock] = []
        tables_out: List[TableBlock] = []
        full_text_lines: List[str] = []
        errors: List[str] = []
        block_counter = 0

        if ext in [".xlsx", ".xls"]:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            for sheetname in wb.sheetnames:
                ws = wb[sheetname]
                rows_data = list(ws.iter_rows(values_only=True))
                if not rows_data:
                    continue
                
                # First row as header
                raw_headers = rows_data[0]
                headers = [str(h or f"Col_{i+1}").strip() for i, h in enumerate(raw_headers)]
                
                data_rows = []
                for r_idx, r in enumerate(rows_data[1:], start=2):
                    cleaned_row = [str(c) if c is not None else "" for c in r]
                    # Skip completely empty rows
                    if any(cleaned_row):
                        data_rows.append(cleaned_row)
                        block_counter += 1
                        
                        # Create descriptive text block for each row
                        row_desc = f"Sheet '{sheetname}' Row {r_idx}: " + "; ".join(
                            f"{h} = {val}" for h, val in zip(headers, cleaned_row) if val
                        )
                        full_text_lines.append(row_desc)
                        
                        blocks_out.append(DocumentBlock(
                            block_id=f"{fn}_{sheetname}_r{r_idx}",
                            block_type=BlockType.TABLE,
                            text=row_desc,
                            page_number=1,
                            section_name=f"Sheet: {sheetname}",
                            metadata={"sheet": sheetname, "row_number": r_idx}
                        ))

                tables_out.append(TableBlock(
                    table_id=f"{fn}_{sheetname}",
                    headers=headers,
                    rows=data_rows,
                    page_number=1,
                    caption=f"Excel Sheet: {sheetname}"
                ))

        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            full_text_lines.append(json.dumps(data, indent=2))
            
            # Flatten JSON sections into structured blocks & tables
            for top_key, top_val in data.items():
                block_counter += 1
                if isinstance(top_val, dict):
                    rows = [[k, str(v)] for k, v in top_val.items()]
                    tables_out.append(TableBlock(
                        table_id=f"{fn}_{top_key}",
                        headers=["Config Key", "Config Value"],
                        rows=rows,
                        page_number=1,
                        caption=f"JSON Section: {top_key}"
                    ))
                    
                    summary_text = f"Section '{top_key}': " + "; ".join(
                        f"{k} = {v}" for k, v in top_val.items()
                    )
                    blocks_out.append(DocumentBlock(
                        block_id=f"{fn}_{top_key}",
                        block_type=BlockType.TEXT,
                        text=summary_text,
                        page_number=1,
                        section_name=top_key,
                        metadata={"json_section": top_key}
                    ))
                else:
                    blocks_out.append(DocumentBlock(
                        block_id=f"{fn}_{top_key}",
                        block_type=BlockType.TEXT,
                        text=f"{top_key}: {str(top_val)}",
                        page_number=1,
                        section_name=top_key
                    ))

        return ExtractedDocument(
            filename=fn,
            file_type="tabular_register" if ext in [".xlsx", ".xls"] else "structured_json",
            doc_id=meta["doc_id"],
            trust_tier=int(meta["trust_tier"]),
            revision=meta.get("revision"),
            effective_date=meta.get("effective_date"),
            blocks=blocks_out,
            tables=tables_out,
            raw_text="\n".join(full_text_lines),
            metadata={"tables_count": len(tables_out)},
            extraction_errors=errors
        )

