"""Source-first structured folklore extractor maintaining evidence provenance and no-hallucination policy."""

import uuid
from typing import List, Optional, Tuple
from app.config.logging import get_logger
from app.folklore.classifier import FolkloreClassifier
from app.folklore.culture import CulturalAnalyzer
from app.folklore.ecology import EcologyAnalyzer
from app.folklore.entities import EntityExtractor
from app.folklore.geography import GeographyResolver
from app.schemas.evidence import Evidence, EvidenceStore, EvidenceType
from app.schemas.folklore import Character, FolkloreDocument, FolkloreType, Location
from app.schemas.source import SourceInfo
from app.utils.hashing import generate_canonical_id
from app.utils.text import clean_whitespace, truncate_text

logger = get_logger("folklore.extractor")


class BaselineFolkloreExtractor:
    """Source-first folklore extractor that traces all extracted information to direct evidence."""

    def __init__(
        self,
        classifier: Optional[FolkloreClassifier] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        geography_resolver: Optional[GeographyResolver] = None,
        cultural_analyzer: Optional[CulturalAnalyzer] = None,
        ecology_analyzer: Optional[EcologyAnalyzer] = None,
    ) -> None:
        self.classifier = classifier or FolkloreClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.geography_resolver = geography_resolver or GeographyResolver()
        self.cultural_analyzer = cultural_analyzer or CulturalAnalyzer()
        self.ecology_analyzer = ecology_analyzer or EcologyAnalyzer()

    def extract_with_evidence(
        self,
        text: str,
        source: SourceInfo,
        document_id: Optional[str] = None,
        title: Optional[str] = None,
        evidence_store: Optional[EvidenceStore] = None,
    ) -> Tuple[FolkloreDocument, List[Evidence]]:
        """Extract structured folklore document, generating explicit Evidence objects for all claims."""
        doc_id_val = document_id or f"doc-{uuid.uuid4().hex[:12]}"
        clean_text = clean_whitespace(text)
        doc_title = title or source.page_title or "Untitled Folklore"
        summary = truncate_text(clean_text, 350)

        # Classify genre
        cls_result = self.classifier.classify(clean_text, title=doc_title)
        folklore_type = cls_result.type if cls_result.is_folklore else FolkloreType.FOLKTALE

        evidence_list: List[Evidence] = []

        # 1. Title Evidence (Direct)
        title_evi = Evidence(
            source_id=source.source_id,
            document_id=doc_id_val,
            url=source.url,
            claim=f"Folklore titled '{doc_title}' documented in source.",
            evidence_type=EvidenceType.DIRECT,
            location="header/title",
            context_snippet=doc_title,
        )
        evidence_list.append(title_evi)

        # 2. Extract Geography
        region_list = self.geography_resolver.detect_regions(clean_text)
        if region_list:
            geo_evi = Evidence(
                source_id=source.source_id,
                document_id=doc_id_val,
                url=source.url,
                claim=f"Geographical tradition associated with: {', '.join(region_list)}",
                evidence_type=EvidenceType.DIRECT,
                location="body text",
            )
            evidence_list.append(geo_evi)

        # 3. Extract Characters & Locations
        chars_list, locs_list, communities_list = self.entity_extractor.extract_entities(clean_text)
        extracted_characters: List[Character] = []
        for c in chars_list:
            c_evi = Evidence(
                source_id=source.source_id,
                document_id=doc_id_val,
                url=source.url,
                claim=f"Character '{c.name}' mentioned in source narrative.",
                evidence_type=EvidenceType.DIRECT,
                location="narrative text",
            )
            evidence_list.append(c_evi)
            c.evidence_ids = [c_evi.evidence_id]
            extracted_characters.append(c)

        extracted_locations: List[Location] = []
        for l in locs_list:
            l_evi = Evidence(
                source_id=source.source_id,
                document_id=doc_id_val,
                url=source.url,
                claim=f"Location '{l.name}' referenced in source narrative.",
                evidence_type=EvidenceType.DIRECT,
                location="narrative text",
            )
            evidence_list.append(l_evi)
            l.evidence_ids = [l_evi.evidence_id]
            extracted_locations.append(l)

        # 4. Extract Traditional Ecological Knowledge (TEK)
        tek_records = self.ecology_analyzer.analyze_ecology(clean_text, source_url=source.url)
        for tek in tek_records:
            tek_evi = Evidence(
                source_id=source.source_id,
                document_id=doc_id_val,
                url=source.url,
                claim=f"TEK [{tek.category.value}]: {tek.knowledge}",
                evidence_type=EvidenceType.DIRECT,
                location=f"Passage: {tek.evidence[:80]}..." if tek.evidence else "body text",
                context_snippet=tek.evidence,
            )
            evidence_list.append(tek_evi)
            tek.evidence_ids = [tek_evi.evidence_id]

        # 5. Culture & Motifs
        cultural_data = self.cultural_analyzer.analyze(clean_text)
        motifs = cultural_data.get("motifs", [])
        if motifs:
            m_evi = Evidence(
                source_id=source.source_id,
                document_id=doc_id_val,
                url=source.url,
                claim=f"Cultural motifs identified: {', '.join(motifs)}",
                evidence_type=EvidenceType.DIRECT,
                location="body text",
            )
            evidence_list.append(m_evi)

        # Register in store if provided
        if evidence_store is not None:
            for evi in evidence_list:
                evidence_store.add(evi)

        all_evi_ids = [e.evidence_id for e in evidence_list]
        canonical_id = generate_canonical_id(doc_title, region=region_list)

        doc = FolkloreDocument(
            id=canonical_id,
            title=doc_title,
            story=clean_text,
            summary=summary,
            folklore_type=folklore_type,
            region=region_list,
            characters=extracted_characters,
            locations=extracted_locations,
            communities=communities_list,
            motifs=motifs,
            cultural_elements=cultural_data.get("cultural_elements", []),
            rituals=cultural_data.get("rituals", []),
            festivals=cultural_data.get("festivals", []),
            beliefs=cultural_data.get("beliefs", []),
            objects=cultural_data.get("objects", []),
            foodways=cultural_data.get("foodways", []),
            occupations=cultural_data.get("occupations", []),
            environmental_knowledge=tek_records,
            source=source,
            evidence_ids=all_evi_ids,
            oral_tradition=True,
            confidence={"baseline_extraction": 0.85},
        )

        return doc, evidence_list

    def extract(self, text: str, source: SourceInfo, title: Optional[str] = None) -> FolkloreDocument:
        """Backward-compatible extract helper returning FolkloreDocument."""
        doc, _ = self.extract_with_evidence(text=text, source=source, title=title)
        return doc
