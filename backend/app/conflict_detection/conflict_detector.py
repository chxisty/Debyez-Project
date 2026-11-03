"""
Conflict Detector
Identifies discrepancies, supersessions, and contradictions between facts across documents and revisions.
Preserves both conflicting facts and records explicit conflict provenance.
"""
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import uuid

from backend.app.knowledge.schema import (
    FactEntity, ConflictEntity, ConflictResolutionType, DocumentEntity
)
from backend.app.conflict_detection.revision_engine import RevisionEngine
from backend.app.config import DOCUMENT_METADATA_REGISTRY

class ConflictDetector:
    def __init__(self, documents: Optional[Dict[str, DocumentEntity]] = None):
        self.documents = documents or {}

    def get_document_trust(self, filename: str) -> int:
        """Returns the trust tier (1-6) for a document. Lower is higher authority."""
        if filename in self.documents:
            return self.documents[filename].trust_level
        if filename in DOCUMENT_METADATA_REGISTRY:
            tier = DOCUMENT_METADATA_REGISTRY[filename].get("trust_tier", 4)
            return int(tier)
        return 5
        return 5

    def detect_conflicts(self, facts: List[FactEntity]) -> List[ConflictEntity]:
        """
        Scans a list of facts for conflicting object values on identical subject+predicate pairs.
        Categorizes conflicts into:
          - RESOLVED_BY_REVISION (superseded historical value vs current)
          - RESOLVED_BY_SOURCE_TRUST (formal engineering standard vs informal field note)
          - UNRESOLVED_DISCREPANCY (direct unresolvable contradiction)
        """
        conflicts: List[ConflictEntity] = []
        
        # Group facts by (subject.upper(), predicate.lower())
        grouped: Dict[Tuple[str, str], List[FactEntity]] = defaultdict(list)
        for f in facts:
            grouped[(f.subject.upper(), f.predicate.lower())].append(f)

        for (subj, pred), fact_group in grouped.items():
            if len(fact_group) < 2:
                continue

            # Compare all pairs within the group
            for i in range(len(fact_group)):
                for j in range(i + 1, len(fact_group)):
                    f1 = fact_group[i]
                    f2 = fact_group[j]

                    # If values are identical, no conflict
                    if f1.object_value.strip().lower() == f2.object_value.strip().lower():
                        continue

                    # Evaluate conflict resolution
                    conflict = self._analyze_pair(f1, f2)
                    if conflict:
                        conflicts.append(conflict)

        return conflicts

    def _analyze_pair(self, f1: FactEntity, f2: FactEntity) -> Optional[ConflictEntity]:
        """Analyzes a pair of differing facts for conflict type and resolution."""
        # Check revision overlap
        overlap = RevisionEngine.intervals_overlap(
            f1.applicable_revision_start, f1.applicable_revision_end,
            f2.applicable_revision_start, f2.applicable_revision_end
        )

        trust1 = self.get_document_trust(f1.provenance.source_document)
        trust2 = self.get_document_trust(f2.provenance.source_document)

        conflict_id = f"CONF-{uuid.uuid4().hex[:8].upper()}"

        if not overlap:
            # Different revisions: Supersession
            older_fact = f1 if (f1.applicable_revision_end and not f2.applicable_revision_end) else f2
            newer_fact = f2 if older_fact == f1 else f1
            affected_rev = newer_fact.applicable_revision_start or "Current"

            explanation = (
                f"Historical value '{older_fact.object_value}' {older_fact.unit or ''} "
                f"(valid {older_fact.applicable_revision_start} to {older_fact.applicable_revision_end}) "
                f"was superseded by '{newer_fact.object_value}' {newer_fact.unit or ''} "
                f"starting at Revision {newer_fact.applicable_revision_start} per {newer_fact.provenance.source_document}."
            )

            return ConflictEntity(
                conflict_id=conflict_id,
                fact_1_id=f1.fact_id,
                fact_2_id=f2.fact_id,
                conflicting_parameter=f"{f1.subject}.{f1.predicate}",
                value_1=f"{f1.object_value} {f1.unit or ''}".strip(),
                value_2=f"{f2.object_value} {f2.unit or ''}".strip(),
                affected_revision=str(affected_rev),
                resolution_status=ConflictResolutionType.RESOLVED_BY_REVISION,
                explanation=explanation,
                source_1=f1.provenance.source_document,
                source_2=f2.provenance.source_document
            )

        # Overlapping revisions: Check source trust levels
        if trust1 != trust2:
            higher_trust_fact = f1 if trust1 < trust2 else f2
            lower_trust_fact = f2 if higher_trust_fact == f1 else f1

            explanation = (
                f"Discrepancy between Tier {min(trust1, trust2)} source ({higher_trust_fact.provenance.source_document}: '{higher_trust_fact.object_value}') "
                f"and Tier {max(trust1, trust2)} source ({lower_trust_fact.provenance.source_document}: '{lower_trust_fact.object_value}'). "
                f"The higher authority source governs; lower authority source represents an unverified field observation or informal claim."
            )

            return ConflictEntity(
                conflict_id=conflict_id,
                fact_1_id=f1.fact_id,
                fact_2_id=f2.fact_id,
                conflicting_parameter=f"{f1.subject}.{f1.predicate}",
                value_1=f"{f1.object_value} {f1.unit or ''}".strip(),
                value_2=f"{f2.object_value} {f2.unit or ''}".strip(),
                affected_revision=f1.applicable_revision_start or "Global",
                resolution_status=ConflictResolutionType.RESOLVED_BY_SOURCE_TRUST,
                explanation=explanation,
                source_1=f1.provenance.source_document,
                source_2=f2.provenance.source_document
            )

        # Equal trust and overlapping: Unresolved discrepancy
        explanation = (
            f"Contradictory parameter values '{f1.object_value}' vs '{f2.object_value}' "
            f"found between sources of equal authority ({f1.provenance.source_document} and {f2.provenance.source_document}). "
            f"Requires engineering review and clarification."
        )

        return ConflictEntity(
            conflict_id=conflict_id,
            fact_1_id=f1.fact_id,
            fact_2_id=f2.fact_id,
            conflicting_parameter=f"{f1.subject}.{f1.predicate}",
            value_1=f"{f1.object_value} {f1.unit or ''}".strip(),
            value_2=f"{f2.object_value} {f2.unit or ''}".strip(),
            affected_revision=f1.applicable_revision_start or "Global",
            resolution_status=ConflictResolutionType.UNRESOLVED_DISCREPANCY,
            explanation=explanation,
            source_1=f1.provenance.source_document,
            source_2=f2.provenance.source_document
        )
