"""
Revision Engine
Parses version numbers, validates revision intervals, and checks fact applicability across software releases.
"""
import re
from typing import Optional, Tuple, Union
from backend.app.knowledge.schema import FactEntity

class RevisionEngine:
    @staticmethod
    def parse_version(version_str: Optional[str]) -> Optional[Tuple[int, ...]]:
        """
        Parses version strings like '3.0', 'Rev 3.2', 'v3.2.1', 'SW 3.0' into numeric tuples like (3, 2).
        Returns None if parsing fails.
        """
        if not version_str:
            return None
        # Extract digits separated by dots
        m = re.search(r"(\d+(?:\.\d+)+|\d+)", str(version_str))
        if not m:
            return None
        parts = m.group(1).split(".")
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return None

    @classmethod
    def compare_versions(cls, v1: str, v2: str) -> int:
        """
        Compares two version strings.
        Returns:
            -1 if v1 < v2
             0 if v1 == v2
             1 if v1 > v2
        """
        t1 = cls.parse_version(v1)
        t2 = cls.parse_version(v2)
        if t1 is None and t2 is None:
            return 0
        if t1 is None:
            return -1
        if t2 is None:
            return 1
        
        # Pad with zeros to equal length
        max_len = max(len(t1), len(t2))
        pad1 = t1 + (0,) * (max_len - len(t1))
        pad2 = t2 + (0,) * (max_len - len(t2))

        if pad1 < pad2:
            return -1
        elif pad1 > pad2:
            return 1
        return 0

    @classmethod
    def intervals_overlap(
        cls,
        start1: Optional[str],
        end1: Optional[str],
        start2: Optional[str],
        end2: Optional[str]
    ) -> bool:
        """
        Evaluates whether two revision intervals [start1, end1) and [start2, end2) overlap.
        If an interval has no start, it defaults to (-inf).
        If an interval has no end, it defaults to (+inf).
        Intervals are treated as half-open: [start, end), so [3.0, 3.2) and [3.2, inf) do NOT overlap.
        """
        # If interval 1 is strictly after interval 2: start1 >= end2
        if end2 is not None and start1 is not None:
            if cls.compare_versions(start1, end2) >= 0:
                return False

        # If interval 2 is strictly after interval 1: start2 >= end1
        if end1 is not None and start2 is not None:
            if cls.compare_versions(start2, end1) >= 0:
                return False

        return True

    @classmethod
    def is_fact_applicable(cls, fact: FactEntity, target_revision: Optional[str]) -> bool:
        """
        Determines whether a fact is valid/active for a target software revision.
        If target_revision is None, returns fact.is_current.
        """
        if target_revision is None:
            return fact.is_current

        t_rev = cls.parse_version(target_revision)
        if t_rev is None:
            # Cannot parse requested revision; fallback to current flag
            return fact.is_current

        # Check lower bound [start, ...)
        if fact.applicable_revision_start:
            s_rev = cls.parse_version(fact.applicable_revision_start)
            if s_rev and cls.compare_versions(target_revision, fact.applicable_revision_start) < 0:
                return False

        # Check upper bound (... , end) - half-open upper boundary
        if fact.applicable_revision_end:
            e_rev = cls.parse_version(fact.applicable_revision_end)
            if e_rev and cls.compare_versions(target_revision, fact.applicable_revision_end) >= 0:
                return False

        return True
