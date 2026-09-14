"""Entity extraction module for characters, locations, and tribal communities."""

from typing import List
from app.schemas.folklore import Character, Location


class EntityExtractor:
    """Extracts characters, locations, and community mentions from folklore text."""

    def extract_entities(self, text: str) -> tuple[List[Character], List[Location], List[str]]:
        """Extract baseline entities from text."""
        # Advanced NER / LLM extraction in Phase 7
        return [], [], []
