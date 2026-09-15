"""Variant preservation and multi-source tradition comparison engine."""

from typing import Dict, List, Optional
from app.config.logging import get_logger
from app.schemas.folklore import CanonicalTradition, FolkloreDocument, Variant
from app.schemas.source import SourceInfo
from app.utils.hashing import generate_canonical_id

logger = get_logger("folklore.variant_preserver")


class VariantPreserver:
    """Manages multi-source traditions without destructively merging differing accounts.

    Preserves:
    Canonical tradition
    ├── Source A version
    ├── Source B version
    ├── Source C version
    └── Source D version
    """

    def __init__(self) -> None:
        self._traditions: Dict[str, CanonicalTradition] = {}

    def register_canonical(self, title: str, tradition_name: str = "", summary: str = "") -> CanonicalTradition:
        """Create or get a canonical folklore tradition."""
        canonical_id = generate_canonical_id(title, region=[tradition_name] if tradition_name else [])
        if canonical_id not in self._traditions:
            self._traditions[canonical_id] = CanonicalTradition(
                canonical_id=canonical_id,
                title=title,
                tradition_name=tradition_name,
                summary=summary,
                variants=[],
            )
        return self._traditions[canonical_id]

    def add_source_variant(
        self,
        canonical_id: str,
        variant_title: str,
        source: SourceInfo,
        story_text: str,
        region: Optional[str] = None,
        language: Optional[str] = None,
        differences: Optional[List[str]] = None,
        evidence_ids: Optional[List[str]] = None,
    ) -> Variant:
        """Attach a distinct source version to a canonical tradition with provenance intact."""
        tradition = self._traditions.get(canonical_id)
        if not tradition:
            tradition = self.register_canonical(title=variant_title, tradition_name=region or "")

        variant = Variant(
            canonical_id=canonical_id,
            variant_title=variant_title,
            region=region or (source.domain if source else None),
            language=language,
            differences=differences or [],
            source=source,
            evidence_ids=evidence_ids or [],
        )

        tradition.variants.append(variant)
        tradition.source_count = len(set(v.source.source_id for v in tradition.variants if v.source))
        logger.info(
            "variant_registered",
            canonical_id=canonical_id,
            variant_title=variant_title,
            source=source.url if source else None,
        )
        return variant

    def get_tradition(self, canonical_id: str) -> Optional[CanonicalTradition]:
        """Retrieve canonical tradition with all variants."""
        return self._traditions.get(canonical_id)

    def list_all_traditions(self) -> List[CanonicalTradition]:
        """List all canonical traditions."""
        return list(self._traditions.values())
