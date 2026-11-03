"""
SQLite Knowledge Base Storage Manager
Provides relational persistence, foreign key enforcement (ON DELETE RESTRICT),
soft deletion/archival, indexing, and IKR export.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Generator
from datetime import datetime
from contextlib import contextmanager

from backend.app.config import KNOWLEDGE_DIR
from backend.app.knowledge.schema import (
    DocumentEntity, ComponentEntity, FactEntity, RelationshipEntity,
    ConflictEntity, ProvenanceRecord, VerificationStatus, ConflictResolutionType, IKRExport
)

DB_PATH = KNOWLEDGE_DIR / "aegis_knowledge.db"

class KnowledgeDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Documents Table with Archival Support
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                document_type TEXT NOT NULL,
                source_category TEXT NOT NULL,
                revision TEXT,
                publication_date TEXT,
                effective_date TEXT,
                trust_level INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_archived BOOLEAN DEFAULT 0,
                archived_at TEXT,
                archival_reason TEXT,
                sha256_hash TEXT,
                metadata_json TEXT
            )
            """)

            # 2. Components Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                component_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                aliases_json TEXT NOT NULL,
                component_type TEXT NOT NULL,
                description TEXT,
                location TEXT,
                status TEXT NOT NULL DEFAULT 'Active',
                source_references_json TEXT NOT NULL,
                provenance_json TEXT NOT NULL
            )
            """)

            # 3. Facts Table with Fact Type & Archival Support (ON DELETE RESTRICT protects audit trail)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                fact_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object_value TEXT NOT NULL,
                unit TEXT,
                fact_type TEXT NOT NULL DEFAULT 'specified_setpoint',
                applicable_revision_start TEXT,
                applicable_revision_end TEXT,
                is_current BOOLEAN NOT NULL DEFAULT 1,
                is_archived BOOLEAN DEFAULT 0,
                source_document TEXT NOT NULL,
                page_number INTEGER DEFAULT 1,
                section TEXT,
                cell_or_bbox TEXT,
                extraction_method TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,
                verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
                notes TEXT,
                FOREIGN KEY (source_document) REFERENCES documents(filename) ON DELETE RESTRICT
            )
            """)

            # 4. Relationships Table with Archival Support (ON DELETE RESTRICT)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                rel_id TEXT PRIMARY KEY,
                source_component TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                target_component TEXT NOT NULL,
                line_type TEXT,
                endpoints TEXT,
                drawing_reference TEXT,
                is_archived BOOLEAN DEFAULT 0,
                source_document TEXT NOT NULL,
                page_number INTEGER DEFAULT 1,
                cell_or_bbox TEXT,
                extraction_method TEXT NOT NULL DEFAULT 'vector_geometry',
                confidence REAL NOT NULL DEFAULT 1.0,
                notes TEXT,
                FOREIGN KEY (source_document) REFERENCES documents(filename) ON DELETE RESTRICT
            )
            """)

            # 5. Conflicts Table (ON DELETE RESTRICT)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                conflict_id TEXT PRIMARY KEY,
                fact_1_id TEXT NOT NULL,
                fact_2_id TEXT NOT NULL,
                conflicting_parameter TEXT NOT NULL,
                value_1 TEXT NOT NULL,
                value_2 TEXT NOT NULL,
                affected_revision TEXT NOT NULL,
                resolution_status TEXT NOT NULL,
                explanation TEXT NOT NULL,
                source_1 TEXT NOT NULL,
                source_2 TEXT NOT NULL,
                FOREIGN KEY (fact_1_id) REFERENCES facts(fact_id) ON DELETE RESTRICT,
                FOREIGN KEY (fact_2_id) REFERENCES facts(fact_id) ON DELETE RESTRICT
            )
            """)

            # Indexes for high-speed deterministic lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_current ON facts(is_current);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(fact_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_archived ON facts(is_archived);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_archived ON documents(is_archived);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_component);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_component);")
            conn.commit()

    def insert_document(self, doc: DocumentEntity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (document_id, filename, document_type, source_category, revision, publication_date, effective_date,
             trust_level, is_active, is_archived, archived_at, archival_reason, sha256_hash, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.document_id, doc.filename, doc.document_type, doc.source_category,
                doc.revision, doc.publication_date, doc.effective_date, doc.trust_level,
                1 if doc.is_active else 0, 1 if doc.is_archived else 0, doc.archived_at, doc.archival_reason,
                doc.sha256_hash, json.dumps(doc.metadata)
            ))
            conn.commit()

    def archive_document(self, filename: str, reason: str = "Administrative Archival"):
        """
        Soft-deletes a document and its associated facts and relationships.
        Does NOT physically remove data; preserves audit trail and foreign key integrity.
        """
        now_ts = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE documents 
            SET is_archived = 1, is_active = 0, archived_at = ?, archival_reason = ?
            WHERE filename = ?
            """, (now_ts, reason, filename))
            
            cursor.execute("UPDATE facts SET is_archived = 1 WHERE source_document = ?", (filename,))
            cursor.execute("UPDATE relationships SET is_archived = 1 WHERE source_document = ?", (filename,))
            conn.commit()

    def unarchive_document(self, filename: str):
        """Restores an archived document and its associated records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE documents 
            SET is_archived = 0, is_active = 1, archived_at = NULL, archival_reason = NULL
            WHERE filename = ?
            """, (filename,))
            
            cursor.execute("UPDATE facts SET is_archived = 0 WHERE source_document = ?", (filename,))
            cursor.execute("UPDATE relationships SET is_archived = 0 WHERE source_document = ?", (filename,))
            conn.commit()

    def insert_component(self, comp: ComponentEntity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO components
            (component_id, canonical_name, aliases_json, component_type, description, location, status, source_references_json, provenance_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comp.component_id, comp.canonical_name, json.dumps(comp.aliases),
                comp.component_type, comp.description, comp.location, comp.status,
                json.dumps(comp.source_references), json.dumps(comp.provenance.model_dump())
            ))
            conn.commit()

    def insert_fact(self, fact: FactEntity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            prov = fact.provenance
            cursor.execute("""
            INSERT OR REPLACE INTO facts
            (fact_id, subject, predicate, object_value, unit, fact_type, applicable_revision_start, applicable_revision_end,
             is_current, is_archived, source_document, page_number, section, cell_or_bbox, extraction_method, confidence, verification_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact.fact_id, fact.subject, fact.predicate, fact.object_value, fact.unit,
                fact.fact_type, fact.applicable_revision_start, fact.applicable_revision_end,
                1 if fact.is_current else 0, 1 if fact.is_archived else 0,
                prov.source_document, prov.page_number, prov.section_name,
                prov.cell_or_bbox, prov.extraction_method, prov.confidence,
                fact.verification_status.value if isinstance(fact.verification_status, VerificationStatus) else str(fact.verification_status),
                fact.notes
            ))
            conn.commit()

    def insert_relationship(self, rel: RelationshipEntity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            prov = rel.provenance
            cursor.execute("""
            INSERT OR REPLACE INTO relationships
            (rel_id, source_component, relationship_type, target_component, line_type, endpoints, drawing_reference,
             is_archived, source_document, page_number, cell_or_bbox, extraction_method, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rel.rel_id, rel.source_component, rel.relationship_type, rel.target_component,
                rel.line_type, rel.endpoints, rel.drawing_reference,
                1 if rel.is_archived else 0,
                prov.source_document, prov.page_number, prov.cell_or_bbox,
                prov.extraction_method, prov.confidence, rel.notes
            ))
            conn.commit()

    def insert_conflict(self, conf: ConflictEntity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO conflicts
            (conflict_id, fact_1_id, fact_2_id, conflicting_parameter, value_1, value_2, affected_revision,
             resolution_status, explanation, source_1, source_2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conf.conflict_id, conf.fact_1_id, conf.fact_2_id, conf.conflicting_parameter,
                conf.value_1, conf.value_2, conf.affected_revision,
                conf.resolution_status.value if isinstance(conf.resolution_status, ConflictResolutionType) else str(conf.resolution_status),
                conf.explanation, conf.source_1, conf.source_2
            ))
            conn.commit()

    def get_all_documents(self, include_archived: bool = True) -> List[DocumentEntity]:
        with self.get_connection() as conn:
            query = "SELECT * FROM documents"
            if not include_archived:
                query += " WHERE is_archived = 0"
            query += " ORDER BY trust_level ASC, filename ASC"
            rows = conn.execute(query).fetchall()
            return [DocumentEntity(
                document_id=r["document_id"],
                filename=r["filename"],
                document_type=r["document_type"],
                source_category=r["source_category"],
                revision=r["revision"],
                publication_date=r["publication_date"],
                effective_date=r["effective_date"],
                trust_level=r["trust_level"],
                is_active=bool(r["is_active"]),
                is_archived=bool(r["is_archived"]),
                archived_at=r["archived_at"],
                archival_reason=r["archival_reason"],
                sha256_hash=r["sha256_hash"],
                metadata=json.loads(r["metadata_json"] or "{}")
            ) for r in rows]

    def get_active_documents(self) -> List[DocumentEntity]:
        return self.get_all_documents(include_archived=False)

    def get_archived_documents(self) -> List[DocumentEntity]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents WHERE is_archived = 1 ORDER BY filename ASC").fetchall()
            return [DocumentEntity(
                document_id=r["document_id"],
                filename=r["filename"],
                document_type=r["document_type"],
                source_category=r["source_category"],
                revision=r["revision"],
                publication_date=r["publication_date"],
                effective_date=r["effective_date"],
                trust_level=r["trust_level"],
                is_active=bool(r["is_active"]),
                is_archived=bool(r["is_archived"]),
                archived_at=r["archived_at"],
                archival_reason=r["archival_reason"],
                sha256_hash=r["sha256_hash"],
                metadata=json.loads(r["metadata_json"] or "{}")
            ) for r in rows]

    def get_all_components(self) -> List[ComponentEntity]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM components ORDER BY component_id ASC").fetchall()
            return [ComponentEntity(
                component_id=r["component_id"],
                canonical_name=r["canonical_name"],
                aliases=json.loads(r["aliases_json"] or "[]"),
                component_type=r["component_type"],
                description=r["description"],
                location=r["location"],
                status=r["status"],
                source_references=json.loads(r["source_references_json"] or "[]"),
                provenance=ProvenanceRecord(**json.loads(r["provenance_json"]))
            ) for r in rows]

    def get_all_facts(self, include_archived: bool = True) -> List[FactEntity]:
        with self.get_connection() as conn:
            query = "SELECT * FROM facts"
            if not include_archived:
                query += " WHERE is_archived = 0"
            query += " ORDER BY subject ASC, fact_id ASC"
            rows = conn.execute(query).fetchall()
            return [FactEntity(
                fact_id=r["fact_id"],
                subject=r["subject"],
                predicate=r["predicate"],
                object_value=r["object_value"],
                unit=r["unit"],
                fact_type=r["fact_type"],
                applicable_revision_start=r["applicable_revision_start"],
                applicable_revision_end=r["applicable_revision_end"],
                is_current=bool(r["is_current"]),
                is_archived=bool(r["is_archived"]),
                provenance=ProvenanceRecord(
                    source_document=r["source_document"],
                    page_number=r["page_number"],
                    section_name=r["section"],
                    cell_or_bbox=r["cell_or_bbox"],
                    extraction_method=r["extraction_method"],
                    confidence=r["confidence"]
                ),
                verification_status=VerificationStatus(r["verification_status"]),
                notes=r["notes"]
            ) for r in rows]

    def get_all_relationships(self, include_archived: bool = True) -> List[RelationshipEntity]:
        with self.get_connection() as conn:
            query = "SELECT * FROM relationships"
            if not include_archived:
                query += " WHERE is_archived = 0"
            query += " ORDER BY source_component ASC, rel_id ASC"
            rows = conn.execute(query).fetchall()
            return [RelationshipEntity(
                rel_id=r["rel_id"],
                source_component=r["source_component"],
                relationship_type=r["relationship_type"],
                target_component=r["target_component"],
                line_type=r["line_type"],
                endpoints=r["endpoints"],
                drawing_reference=r["drawing_reference"],
                is_archived=bool(r["is_archived"]),
                provenance=ProvenanceRecord(
                    source_document=r["source_document"],
                    page_number=r["page_number"],
                    cell_or_bbox=r["cell_or_bbox"],
                    extraction_method=r["extraction_method"],
                    confidence=r["confidence"]
                ),
                notes=r["notes"]
            ) for r in rows]

    def get_all_conflicts(self) -> List[ConflictEntity]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM conflicts ORDER BY conflict_id ASC").fetchall()
            return [ConflictEntity(
                conflict_id=r["conflict_id"],
                fact_1_id=r["fact_1_id"],
                fact_2_id=r["fact_2_id"],
                conflicting_parameter=r["conflicting_parameter"],
                value_1=r["value_1"],
                value_2=r["value_2"],
                affected_revision=r["affected_revision"],
                resolution_status=ConflictResolutionType(r["resolution_status"]),
                explanation=r["explanation"],
                source_1=r["source_1"],
                source_2=r["source_2"]
            ) for r in rows]

    def get_facts_by_subject(self, subject: str, include_archived: bool = False) -> List[FactEntity]:
        with self.get_connection() as conn:
            query = "SELECT * FROM facts WHERE subject = ? COLLATE NOCASE"
            if not include_archived:
                query += " AND is_archived = 0"
            rows = conn.execute(query, (subject,)).fetchall()
            return [FactEntity(
                fact_id=r["fact_id"],
                subject=r["subject"],
                predicate=r["predicate"],
                object_value=r["object_value"],
                unit=r["unit"],
                fact_type=r["fact_type"],
                applicable_revision_start=r["applicable_revision_start"],
                applicable_revision_end=r["applicable_revision_end"],
                is_current=bool(r["is_current"]),
                is_archived=bool(r["is_archived"]),
                provenance=ProvenanceRecord(
                    source_document=r["source_document"],
                    page_number=r["page_number"],
                    section_name=r["section"],
                    cell_or_bbox=r["cell_or_bbox"],
                    extraction_method=r["extraction_method"],
                    confidence=r["confidence"]
                ),
                verification_status=VerificationStatus(r["verification_status"]),
                notes=r["notes"]
            ) for r in rows]

    def get_active_facts_for_revision(self, revision: Optional[str]) -> List[FactEntity]:
        """
        Filters facts applicable to a specific software revision.
        If revision is None, returns ONLY current facts (does NOT mix historical or observations).
        """
        all_facts = self.get_all_facts(include_archived=False)
        from backend.app.conflict_detection.revision_engine import RevisionEngine
        if revision is None:
            # Query without revision: strictly current facts, no historical mixing
            return [f for f in all_facts if f.is_current and f.fact_type in ["specified_setpoint", "rule", "parameter", "topology"]]
        
        return [f for f in all_facts if RevisionEngine.is_fact_applicable(f, revision)]

    def export_ikr_to_json(self, export_path: Optional[Path] = None) -> IKRExport:
        if export_path is None:
            export_path = KNOWLEDGE_DIR / "ikr_export.json"
        
        docs = self.get_all_documents()
        comps = self.get_all_components()
        facts = self.get_all_facts()
        rels = self.get_all_relationships()
        confs = self.get_all_conflicts()

        export_obj = IKRExport(
            export_version="1.0",
            export_timestamp=datetime.now().isoformat(),
            total_documents=len(docs),
            total_components=len(comps),
            total_facts=len(facts),
            total_relationships=len(rels),
            total_conflicts=len(confs),
            documents=docs,
            components=comps,
            facts=facts,
            relationships=rels,
            conflicts=confs
        )
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_obj.model_dump(), f, indent=2, ensure_ascii=False)
        return export_obj
