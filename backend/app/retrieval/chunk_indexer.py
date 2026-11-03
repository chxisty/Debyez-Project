"""
Chunk Indexer
Compiles document blocks, table extracts, and IKR facts into unified RetrievalChunks for indexing.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

from backend.app.config import PROCESSED_DIR, KNOWLEDGE_DIR, DOCUMENT_METADATA_REGISTRY
from backend.app.retrieval.models import RetrievalChunk
from backend.app.knowledge.database import KnowledgeDatabase

class ChunkIndexer:
    @staticmethod
    def load_chunks() -> List[RetrievalChunk]:
        """Loads and converts all extracted document blocks and IKR facts into RetrievalChunks."""
        chunks: List[RetrievalChunk] = []
        chunk_idx = 1

        # 1. Ingest processed document blocks
        extracted_file = PROCESSED_DIR / "extracted_docs.json"
        if extracted_file.exists():
            with open(extracted_file, "r", encoding="utf-8") as f:
                docs = json.load(f)

            for doc in docs:
                fname = doc.get("filename", "")
                doc_id = doc.get("doc_id", fname)
                trust_tier = int(doc.get("trust_tier", 2))
                rev = doc.get("revision")

                # Blocks
                for b in doc.get("blocks", []):
                    txt = b.get("text", "").strip()
                    if not txt:
                        continue
                    
                    # Detect entity references in text
                    entities = []
                    for code in ["PS-04A", "PS-04", "PS-40", "IV-21", "PLC-03", "HPU", "A17", "A18", "A19", "Q1", "T1", "TB-7", "MAIN_RESERVOIR", "AUX_RESERVOIR"]:
                        if code in txt or code.replace("-", "") in txt:
                            entities.append(code)

                    chunks.append(RetrievalChunk(
                        chunk_id=f"CHK-{chunk_idx:04d}",
                        text=txt,
                        document_id=doc_id,
                        filename=fname,
                        page_number=b.get("page_number", 1),
                        section_name=b.get("section_name"),
                        cell_or_bbox=str(b.get("bbox")) if b.get("bbox") else None,
                        trust_tier=trust_tier,
                        applicable_revision_start=rev,
                        is_current=True,
                        extraction_method=doc.get("file_type", "pdf").lower(),
                        verification_status="VERIFIED",
                        entity_references=entities,
                        metadata={"block_type": b.get("block_type")}
                    ))
                    chunk_idx += 1

                # Tables
                for t in doc.get("tables", []):
                    table_rows = t.get("rows", [])
                    headers = t.get("headers", [])
                    table_text = f"Table {t.get('caption', '')}: " + " | ".join(headers) + "\n"
                    table_text += "\n".join([" | ".join([str(c) for c in row]) for row in table_rows])
                    
                    chunks.append(RetrievalChunk(
                        chunk_id=f"CHK-{chunk_idx:04d}",
                        text=table_text,
                        document_id=doc_id,
                        filename=fname,
                        page_number=t.get("page_number", 1),
                        section_name=t.get("caption"),
                        cell_or_bbox="Table Data",
                        trust_tier=trust_tier,
                        applicable_revision_start=rev,
                        is_current=True,
                        extraction_method="tabular_extract",
                        verification_status="VERIFIED",
                        metadata={"table_id": t.get("table_id")}
                    ))
                    chunk_idx += 1

        # 2. Ingest IKR Facts
        db = KnowledgeDatabase()
        facts = db.get_all_facts(include_archived=False)
        for f in facts:
            reg = DOCUMENT_METADATA_REGISTRY.get(f.provenance.source_document, {})
            tier = int(reg.get("trust_tier", 2))
            
            fact_summary = (
                f"Subject: {f.subject} | Parameter: {f.predicate} | Value: {f.object_value} {f.unit or ''} | "
                f"Type: {f.fact_type} | Revisions: [{f.applicable_revision_start or 'Any'}, {f.applicable_revision_end or 'Inf'}) | "
                f"Current: {f.is_current} | Notes: {f.notes or ''}"
            ).strip()

            chunks.append(RetrievalChunk(
                chunk_id=f"FACT-CHK-{f.fact_id}",
                text=fact_summary,
                document_id=reg.get("doc_id", f.provenance.source_document),
                filename=f.provenance.source_document,
                page_number=f.provenance.page_number,
                section_name=f.provenance.section_name,
                cell_or_bbox=f.provenance.cell_or_bbox,
                trust_tier=tier,
                applicable_revision_start=f.applicable_revision_start,
                applicable_revision_end=f.applicable_revision_end,
                is_current=f.is_current,
                extraction_method=f.provenance.extraction_method,
                verification_status=f.verification_status.value if hasattr(f.verification_status, "value") else str(f.verification_status),
                entity_references=[f.subject],
                metadata={"fact_id": f.fact_id, "predicate": f.predicate, "fact_type": f.fact_type}
            ))

        return chunks

