"""
Entity Resolver
Orchestrates deterministic normalization, alias registry lookup, and negative disambiguation.
"""
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

from backend.app.knowledge.schema import ComponentEntity, ProvenanceRecord
from backend.app.entity_resolution.normalizer import IdentifierNormalizer
from backend.app.entity_resolution.disambiguator import EntityDisambiguator, DisambiguationResult

class EntityResolver:
    def __init__(self, components: Optional[List[ComponentEntity]] = None):
        self.components: Dict[str, ComponentEntity] = {}
        self.alias_to_canonical: Dict[str, str] = {}
        
        if components:
            for comp in components:
                self.register_component(comp)

    def register_component(self, comp: ComponentEntity):
        """Registers a canonical component and its aliases into the in-memory lookup index."""
        self.components[comp.component_id] = comp
        norm_canonical = IdentifierNormalizer.normalize_token(comp.component_id)
        self.alias_to_canonical[norm_canonical] = comp.component_id
        
        norm_name = IdentifierNormalizer.normalize_token(comp.canonical_name)
        self.alias_to_canonical[norm_name] = comp.component_id

        for alias in comp.aliases:
            norm_alias = IdentifierNormalizer.normalize_token(alias)
            self.alias_to_canonical[norm_alias] = comp.component_id

    def resolve_mention(self, raw_mention: str) -> Optional[ComponentEntity]:
        """
        Resolves a raw text mention or abbreviation to a canonical ComponentEntity.
        Returns None if no canonical component matches.
        """
        if not raw_mention or not raw_mention.strip():
            return None

        # 1. First check if it directly normalizes to a canonical ID pattern
        canonical_id_guess = IdentifierNormalizer.to_canonical_id(raw_mention)
        if canonical_id_guess in self.components:
            return self.components[canonical_id_guess]

        # 2. Check token normalized lookup
        norm_token = IdentifierNormalizer.normalize_token(raw_mention)
        if norm_token in self.alias_to_canonical:
            canonical_id = self.alias_to_canonical[norm_token]
            return self.components.get(canonical_id)

        # 3. Check Disambiguator known alias map
        alias_upper = raw_mention.strip().upper()
        if alias_upper in EntityDisambiguator.ALIAS_MAP:
            target_id, _, _ = EntityDisambiguator.ALIAS_MAP[alias_upper]
            return self.components.get(target_id)

        return None

    def disambiguate_pair(self, id1: str, id2: str) -> DisambiguationResult:
        """
        Evaluates whether two identifiers represent the same component or a false-friend.
        """
        return EntityDisambiguator.check_identity(id1, id2)

    def is_false_friend(self, id1: str, id2: str) -> bool:
        """Helper to quickly check if two tokens form a known prohibited merger."""
        res = self.disambiguate_pair(id1, id2)
        return not res.is_same_component and not res.requires_human_review

    def get_component(self, component_id: str) -> Optional[ComponentEntity]:
        """Retrieves a component by its exact canonical ID."""
        return self.components.get(component_id)
