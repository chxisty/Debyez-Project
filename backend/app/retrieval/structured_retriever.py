"""
Structured SQL Retriever
Direct relational lookups for canonical components, verified facts, diagram topologies, and revision intervals.
"""
import re
from typing import List, Optional, Dict, Any

from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.entity_resolution.normalizer import IdentifierNormalizer
from backend.app.entity_resolution.resolver import EntityResolver
from backend.app.retrieval.models import RetrievalChunk, ScoredChunk

class StructuredRetriever:
    def __init__(self, db: Optional[KnowledgeDatabase] = None):
        self.db = db or KnowledgeDatabase()
        components = self.db.get_all_components()
        self.resolver = EntityResolver(components)

    def search_entities(self, query: str) -> List[str]:
        """Detects mentioned components in the query and returns canonical IDs."""
        tokens = query.replace(",", " ").replace("?", " ").replace(";", " ").split()
        found = set()
        
        # Check whole query and sub-phrases
        resolved = self.resolver.resolve_mention(query)
        if resolved:
            found.add(resolved.component_id)

        for tok in tokens:
            canon = IdentifierNormalizer.to_canonical_id(tok)
            if self.resolver.get_component(canon):
                found.add(canon)
            else:
                res = self.resolver.resolve_mention(tok)
                if res:
                    found.add(res.component_id)

        # Multi-word alias checks
        for alias in ["HYDRAULIC POWER UNIT", "HYDRAULIC POWER PACK", "THE UNIT", "PRESSURE XDCR", "ISOLATION VALVE", "AUXILIARY RESERVOIR", "MAIN RESERVOIR"]:
            if alias in query.upper():
                res = self.resolver.resolve_mention(alias)
                if res:
                    found.add(res.component_id)

        return sorted(list(found))

    def retrieve_structured_data(
        self,
        entity_ids: List[str],
        target_revision: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieves structured components, applicable facts, relationships, and conflicts."""
        facts_list = []
        rels_list = []
        conflicts_list = []

        all_facts = self.db.get_active_facts_for_revision(target_revision)
        all_rels = self.db.get_all_relationships(include_archived=False)
        all_confs = self.db.get_all_conflicts()

        for eid in entity_ids:
            # Facts for this entity
            entity_facts = [f for f in all_facts if f.subject.upper() == eid.upper()]
            facts_list.extend(entity_facts)

            # Topological connections where component is source or target
            entity_rels = [
                r for r in all_rels 
                if r.source_component.upper() == eid.upper() or r.target_component.upper() == eid.upper()
            ]
            rels_list.extend(entity_rels)

            # Conflicts touching this entity
            entity_confs = [
                c for c in all_confs 
                if eid.upper() in c.conflicting_parameter.upper()
            ]
            conflicts_list.extend(entity_confs)

        return {
            "facts": facts_list,
            "relationships": rels_list,
            "conflicts": conflicts_list
        }

    def search_as_chunks(
        self,
        entity_ids: List[str],
        target_revision: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[ScoredChunk]:
        """Converts matched structured facts into high-ranking ScoredChunks."""
        structured = self.retrieve_structured_data(entity_ids, target_revision)
        chunks: List[ScoredChunk] = []

        # Prioritize facts relevant to the query if query provided
        facts = structured["facts"]
        if query:
            q_tokens = set(re.findall(r"\w+", query.lower()))
            def fact_relevance(f) -> int:
                f_tokens = set(re.findall(r"\w+", f"{f.predicate} {f.notes} {f.object_value}".lower()))
                return len(q_tokens.intersection(f_tokens))
            facts.sort(key=fact_relevance, reverse=True)
            # Retain top 5 most relevant facts
            facts = facts[:5]

        rank = 1

        for f in facts:
            txt = (
                f"[STRUCTURED IKR FACT] Component: {f.subject} | Parameter: {f.predicate} | "
                f"Value: {f.object_value} {f.unit or ''} | Type: {f.fact_type} | "
                f"Revision: [{f.applicable_revision_start or 'Any'}, {f.applicable_revision_end or 'Inf'}) | "
                f"Notes: {f.notes or ''}"
            )
            r_chunk = RetrievalChunk(
                chunk_id=f"FACT-CHK-{f.fact_id}",
                text=txt,
                document_id=f.provenance.source_document,
                filename=f.provenance.source_document,
                page_number=f.provenance.page_number,
                section_name=f.provenance.section_name,
                cell_or_bbox=f.provenance.cell_or_bbox,
                trust_tier=1,
                applicable_revision_start=f.applicable_revision_start,
                applicable_revision_end=f.applicable_revision_end,
                is_current=f.is_current,
                extraction_method=f.provenance.extraction_method,
                verification_status=f.verification_status.value if hasattr(f.verification_status, "value") else str(f.verification_status),
                entity_references=[f.subject],
                metadata={"fact_id": f.fact_id, "predicate": f.predicate, "fact_type": f.fact_type}
            )
            chunks.append(ScoredChunk(
                chunk=r_chunk,
                score=1.0,
                rank=rank,
                channel="structured_sql"
            ))
            rank += 1

        for r in structured["relationships"]:
            txt = (
                f"[STRUCTURED TOPOLOGY] {r.source_component} --[{r.relationship_type} / {r.line_type}]--> {r.target_component} | "
                f"Drawing: {r.drawing_reference} | Endpoints: {r.endpoints or 'N/A'} | Notes: {r.notes or ''}"
            )
            r_chunk = RetrievalChunk(
                chunk_id=f"REL-CHK-{r.rel_id}",
                text=txt,
                document_id=r.provenance.source_document,
                filename=r.provenance.source_document,
                page_number=r.provenance.page_number,
                section_name=r.drawing_reference,
                cell_or_bbox=r.endpoints,
                trust_tier=2,
                is_current=True,
                extraction_method="vector_geometry",
                verification_status="VERIFIED",
                entity_references=[r.source_component, r.target_component],
                metadata={"rel_id": r.rel_id, "line_type": r.line_type}
            )
            chunks.append(ScoredChunk(
                chunk=r_chunk,
                score=0.95,
                rank=rank,
                channel="structured_sql"
            ))
            rank += 1

        return chunks

