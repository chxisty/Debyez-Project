"""
Entity Disambiguator & Negative Disambiguation Rules
Enforces strict boundaries between look-alike industrial components.
"""
from typing import Tuple, Optional, List
from pydantic import BaseModel

class DisambiguationResult(BaseModel):
    is_same_component: bool
    canonical_id: Optional[str]
    confidence: float
    explanation: str
    evidence_document: str
    requires_human_review: bool = False

class EntityDisambiguator:
    # Explicit false-friend pairs that must never be merged
    FALSE_FRIEND_PAIRS = {
        ("PS-04", "PS-40"): (
            "PS-04 was the superseded HPU discharge line pressure sensor. "
            "PS-40 is on the Coolant Loop, Skid B, and is completely unrelated to the HPU discharge circuit. "
            "Source: component_register.xlsx Row 6 & configuration_export.json sensor_ps40_note."
        ),
        ("PS-04", "PS-04A"): (
            "PS-04 was superseded by PS-04A effective Software Revision 3.2 per ECN-1042. "
            "PS-04A uses updated signal conditioning to resolve 18-month drift issues and requires controller firmware >= 3.2. "
            "ECN-1042 explicitly notes PS-04A is NOT a form-fit-function replacement for PS-04."
        ),
        ("PS-40", "PS-04A"): (
            "PS-40 is located on Coolant Loop, Skid B. PS-04A is located on the HPU discharge line. "
            "They serve different functional loops."
        )
    }

    # Known drawing and operational alias mappings
    ALIAS_MAP = {
        "P.S.04-A": ("PS-04A", "Physical unit label formatting on Screen 03 Diagnostics", 0.99),
        "P04A": ("PS-04A", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "PS04A": ("PS-04A", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "P04": ("PS-04", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "PS04": ("PS-04", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "PRESSURE SENSOR 04": ("PS-04", "Common name in Component Register", 0.99),
        "PRESSURE SENSOR 04A": ("PS-04A", "Common name in Component Register", 0.99),
        "P40": ("PS-40", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "PS40": ("PS-40", "Known alias listed in Component Register AEG-CR-700", 0.98),
        "PRESSURE XDCR": ("PS-04A", "Wiring Diagram AEG-DWG-W03 Note 1 identifies field device at J-14/TB-7 as PS-04A", 0.95),
        "HYDRAULIC POWER PACK": ("HPU", "Informal alias in Maintenance Manual and Component Register", 0.99),
        "HYDRAULIC UNIT": ("HPU", "Informal alias in Terminology Glossary AEG-GL-700", 0.99),
        "HP UNIT": ("HPU", "Informal alias in Training Deck and Operator Manual", 0.99),
        "THE UNIT": ("HPU", "Informal alias in Training Deck Slide 2", 0.95),
        "ISOLATION VALVE 21": ("IV-21", "Common name in Component Register AEG-CR-700", 0.99),
        "IV21": ("IV-21", "Known alias in Component Register AEG-CR-700", 0.98),
        "HCS CONTROLLER": ("PLC-03", "Common name in Component Register AEG-CR-700", 0.99),
        "AEGIS CONTROLLER": ("PLC-03", "Known alias in Component Register AEG-CR-700", 0.98),
        "CONTROLLER": ("PLC-03", "Known alias in Component Register AEG-CR-700", 0.95)
    }

    @classmethod
    def check_identity(cls, id1: str, id2: str) -> DisambiguationResult:
        """
        Determines whether two identifiers refer to the same physical component.
        Strictly enforces negative disambiguation rules.
        """
        from backend.app.entity_resolution.normalizer import IdentifierNormalizer
        norm1 = IdentifierNormalizer.to_canonical_id(id1)
        norm2 = IdentifierNormalizer.to_canonical_id(id2)

        # 1. Exact match
        if norm1 == norm2:
            return DisambiguationResult(
                is_same_component=True,
                canonical_id=norm1,
                confidence=1.0,
                explanation=f"'{id1}' and '{id2}' normalize to identical canonical ID '{norm1}'.",
                evidence_document="Deterministic Normalization Rule"
            )

        # 2. Check false-friend pairs
        pair_key = (norm1, norm2)
        rev_pair_key = (norm2, norm1)
        if pair_key in cls.FALSE_FRIEND_PAIRS:
            return DisambiguationResult(
                is_same_component=False,
                canonical_id=None,
                confidence=1.0,
                explanation=cls.FALSE_FRIEND_PAIRS[pair_key],
                evidence_document="component_register.xlsx / ECN-1042.pdf"
            )
        if rev_pair_key in cls.FALSE_FRIEND_PAIRS:
            return DisambiguationResult(
                is_same_component=False,
                canonical_id=None,
                confidence=1.0,
                explanation=cls.FALSE_FRIEND_PAIRS[rev_pair_key],
                evidence_document="component_register.xlsx / ECN-1042.pdf"
            )

        # 3. Alias check
        target1 = cls.ALIAS_MAP.get(id1.strip().upper())
        target2 = cls.ALIAS_MAP.get(id2.strip().upper())
        
        canon1 = target1[0] if target1 else norm1
        canon2 = target2[0] if target2 else norm2
        
        if canon1 == canon2 and canon1:
            conf = 1.0
            if target1:
                conf = min(conf, target1[2])
            if target2:
                conf = min(conf, target2[2])
            return DisambiguationResult(
                is_same_component=True,
                canonical_id=canon1,
                confidence=conf,
                explanation=f"Both '{id1}' and '{id2}' map to canonical component '{canon1}'.",
                evidence_document="component_register.xlsx"
            )

        # 4. Unknown / Ambiguous match -> flag for human review
        return DisambiguationResult(
            is_same_component=False,
            canonical_id=None,
            confidence=0.5,
            explanation=f"No confirmed alias or identity link between '{id1}' and '{id2}'. Flagged for human review.",
            evidence_document="Unverified",
            requires_human_review=True
        )
