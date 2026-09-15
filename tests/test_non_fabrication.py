"""Automated Non-Fabrication and Source Provenance Test Suite (Prompt Section 23).

Verifies the 10 core non-negotiable principles:
1. Missing source information remains null.
2. AI cannot create a source URL.
3. Extracted claims retain evidence.
4. Original content is never overwritten.
5. Generated summaries are stored separately.
6. Source attribution exists in every result.
7. Duplicate pages retain provenance.
8. Folklore variants are preserved.
9. Unsupported claims are rejected.
10. Every completed task produces a source manifest.
"""

import json
import pytest
from pathlib import Path

from app.discovery.registry import SourceRegistry
from app.extraction.document import ParsedWebDocument
from app.folklore.ecology import EcologyAnalyzer
from app.folklore.extractor import BaselineFolkloreExtractor
from app.folklore.validator import FolkloreValidator
from app.folklore.variant_preserver import VariantPreserver
from app.schemas.document import PreservedDocument
from app.schemas.evidence import Evidence, EvidenceStore, EvidenceType
from app.schemas.folklore import (
    Character,
    EnvironmentalCategory,
    EnvironmentalKnowledge,
    FolkloreDocument,
    FolkloreType,
    Location,
    Variant,
)
from app.schemas.source import SourceInfo, SourceType
from app.storage.repository import JSONFolkloreRepository
from app.storage.task_output import TaskOutputManager


class TestNonFabricationAndProvenance:
    """10 Automated Verification Test Cases enforcing Source Authority and No-Hallucination."""

    # 1. Missing source information remains null.
    def test_missing_source_info_remains_null(self):
        source = SourceInfo(
            url="https://sahapedia.org/article/mumal-mahendra",
            domain="sahapedia.org",
            platform_name="Sahapedia",
            # author and published_at intentionally omitted
        )
        assert source.author is None
        assert source.published_at is None

        file_meta = source.to_file_metadata()["source_information"]
        assert file_meta["author"] is None
        assert file_meta["published_at"] is None
        assert file_meta["url"] == "https://sahapedia.org/article/mumal-mahendra"

    # 2. AI cannot create a source URL (synthetic URL validation).
    def test_ai_cannot_create_source_url(self):
        validator = FolkloreValidator()

        # Valid public URLs
        assert validator.is_valid_source_url("https://en.wikipedia.org/wiki/Rajasthani_folklore") is True
        assert validator.is_valid_source_url("https://ignca.gov.in/divisions/janapada-sampada") is True

        # Reject synthetic / fake / invalid URLs
        assert validator.is_valid_source_url("https://fakeurl.com/story") is False
        assert validator.is_valid_source_url("http://synthetic-source.ai/tales") is False
        assert validator.is_valid_source_url("not_a_valid_url") is False
        assert validator.is_valid_source_url("") is False
        assert validator.is_valid_source_url(None) is False

        # Validate document with fake URL fails validation
        fake_source = SourceInfo(url="https://fakeurl.com/story", domain="fakeurl.com")
        doc = FolkloreDocument(
            title="Invented Tale",
            story="Once upon a time...",
            source=fake_source,
        )
        is_valid, errors = validator.validate(doc)
        assert is_valid is False
        assert any("Invalid or synthetic source URL" in e for e in errors)

    # 3. Extracted claims retain evidence.
    def test_extracted_claims_retain_evidence(self):
        extractor = BaselineFolkloreExtractor()
        evidence_store = EvidenceStore()
        source = SourceInfo(
            url="https://en.wikipedia.org/wiki/Pabuji",
            domain="en.wikipedia.org",
            platform_name="Wikipedia",
            page_title="Epic of Pabuji",
        )
        sample_story = (
            "The Epic of Pabuji is an oral epic from Rajasthan. Pabuji was a folk deity revered in Marwar. "
            "He protected cows and pastoral camels using the holy black mare Kesar Kalami. "
            "Villagers built traditional johad water harvesting reservoirs and maintained sacred khejri protection groves."
        )

        doc, evidence_list = extractor.extract_with_evidence(
            text=sample_story,
            source=source,
            evidence_store=evidence_store,
        )

        assert len(evidence_list) > 0
        assert len(doc.evidence_ids) == len(evidence_list)
        # All evidence must be DIRECT
        assert all(e.evidence_type == EvidenceType.DIRECT for e in evidence_list)
        # Source ID and URL must match
        assert all(e.source_id == source.source_id for e in evidence_list)
        assert all(e.url == source.url for e in evidence_list)

    # 4. Original content is never overwritten (Layers preserved).
    def test_original_content_is_never_overwritten(self):
        raw_html = "<html><body><nav>Menu</nav><article><p>Story of Mumal</p></article></body></html>"
        original_text = "Story of Mumal and Prince Mahendra of Sodha."
        cleaned_text = "Story of Mumal and Prince Mahendra of Sodha."

        pdoc = PreservedDocument(
            source_id="src-001",
            url="https://sahapedia.org/mumal",
            raw_content=raw_html,
            original_text=original_text,
            cleaned_text=cleaned_text,
            generated_summary="AI generated summary here",
        )

        assert pdoc.raw_content == raw_html
        assert pdoc.original_text == original_text
        assert pdoc.cleaned_text == cleaned_text
        # Original text has not been contaminated by AI summary
        assert pdoc.generated_summary not in pdoc.original_text
        assert pdoc.generated_summary not in pdoc.cleaned_text

    # 5. Generated summaries are stored separately.
    def test_generated_summaries_stored_separately(self):
        source = SourceInfo(
            url="https://ignca.gov.in/tales/pabuji",
            domain="ignca.gov.in",
            platform_name="IGNCA",
            page_title="Pabuji Katha",
        )
        original_story_text = "Pabuji was a heroic deity who protected cows."

        doc = FolkloreDocument(
            title="Pabuji Katha",
            story=original_story_text,
            generated_summary="AI-synthesized concise summary: 14th century Rathore prince deity.",
            ai_analysis="Structuralist analysis of pastoral cattle raiding themes.",
            source=source,
        )

        # The core story field strictly preserves original text
        assert doc.story == original_story_text
        assert "AI-synthesized" not in doc.story
        assert doc.generated_summary is not None
        assert doc.ai_analysis is not None

    # 6. Source attribution exists in every result.
    def test_source_attribution_exists_in_every_result(self, tmp_path):
        repo = JSONFolkloreRepository(base_dir=str(tmp_path))
        source = SourceInfo(
            url="https://ruralindiaonline.org/articles/khejri-tree-sacrifice/",
            domain="ruralindiaonline.org",
            platform_name="PARI",
            page_title="The Khejri Sacrifice",
            author="Rural Reporter",
            published_at="2024-03-15",
            source_type=SourceType.COMMUNITY_ARCHIVE,
        )
        doc = FolkloreDocument(
            id="folk-khejri-001",
            title="The Khejri Tree Sacrifice",
            story="Amrita Devi and Bishnois protected the khejri trees.",
            source=source,
        )

        saved_path = repo.save(doc)
        with open(saved_path, "r", encoding="utf-8") as f:
            saved_json = json.load(f)

        assert "source_information" in saved_json
        s_info = saved_json["source_information"]
        assert s_info["platform"] == "PARI"
        assert s_info["website"] == "ruralindiaonline.org"
        assert s_info["url"] == "https://ruralindiaonline.org/articles/khejri-tree-sacrifice/"
        assert s_info["author"] == "Rural Reporter"
        assert s_info["published_at"] == "2024-03-15"
        assert s_info["source_type"] == "COMMUNITY_ARCHIVE"
        assert "retrieved_at" in s_info

    # 7. Duplicate pages retain provenance.
    def test_duplicate_pages_retain_provenance(self):
        source1 = SourceInfo(
            url="https://site-a.org/story/bonbibi",
            domain="site-a.org",
            platform_name="Site A",
            retrieval_timestamp="2026-09-10T10:00:00Z",
        )
        source2 = SourceInfo(
            url="https://site-b.org/archives/bonbibi",
            domain="site-b.org",
            platform_name="Site B",
            retrieval_timestamp="2026-09-12T14:00:00Z",
        )

        doc1 = FolkloreDocument(
            title="Bonbibi Tale",
            story="Guardian deity of Sundarbans mangroves.",
            source=source1,
        )
        doc2 = FolkloreDocument(
            title="Bonbibi Tale",
            story="Guardian deity of Sundarbans mangroves.",
            source=source2,
        )

        # Both records have distinct provenance and timestamps
        assert doc1.source.url != doc2.source.url
        assert doc1.source.source_id != doc2.source.source_id
        assert doc1.source.retrieval_timestamp != doc2.source.retrieval_timestamp

    # 8. Folklore variants are preserved.
    def test_folklore_variants_are_preserved(self):
        preserver = VariantPreserver()
        tradition = preserver.register_canonical(
            title="The Legend of Mumal and Mahendra",
            tradition_name="Rajasthani Romances",
            summary="A classic tragic love story of the Thar desert.",
        )

        source_a = SourceInfo(
            url="https://sahapedia.org/mumal-lodrawa",
            domain="sahapedia.org",
            platform_name="Sahapedia",
            page_title="Mumal of Lodrawa",
        )
        source_b = SourceInfo(
            url="https://archive.org/details/annals-rajasthan-vol2",
            domain="archive.org",
            platform_name="Internet Archive",
            page_title="Tod's Annals of Rajasthan",
        )

        var_a = preserver.add_source_variant(
            canonical_id=tradition.canonical_id,
            variant_title="Mumal of Lodrawa (Oral Ballad Version)",
            source=source_a,
            story_text="In this version, Prince Mahendra rides the swift camel Cheetal every night...",
            region="Jaisalmer",
            differences=["Focuses on the Kak palace labyrinth and nocturnal camel rides"],
        )

        var_b = preserver.add_source_variant(
            canonical_id=tradition.canonical_id,
            variant_title="Mahendra and Mumal (Colonial Survey Record)",
            source=source_b,
            story_text="Recorded by James Tod in early 19th-century Marwar...",
            region="Marwar",
            differences=["Emphasizes feudal political alliances between Umerkot and Lodrawa"],
        )

        saved_tradition = preserver.get_tradition(tradition.canonical_id)
        assert saved_tradition is not None
        assert len(saved_tradition.variants) == 2
        assert saved_tradition.variants[0].variant_title == "Mumal of Lodrawa (Oral Ballad Version)"
        assert saved_tradition.variants[1].variant_title == "Mahendra and Mumal (Colonial Survey Record)"
        assert saved_tradition.variants[0].source.url == "https://sahapedia.org/mumal-lodrawa"
        assert saved_tradition.variants[1].source.url == "https://archive.org/details/annals-rajasthan-vol2"

    # 9. Unsupported claims are rejected.
    def test_unsupported_claims_rejected(self):
        validator = FolkloreValidator()
        source = SourceInfo(url="https://ignca.gov.in/tales/desert", domain="ignca.gov.in")

        # Generated TEK with no passage evidence and inflated confidence must be rejected
        unsupported_tek = EnvironmentalKnowledge(
            knowledge="Invented water secret",
            category=EnvironmentalCategory.WATER_MANAGEMENT,
            description="No evidence provided in source text",
            evidence="",  # Empty evidence
            evidence_type=EvidenceType.GENERATED,
            confidence=0.99,  # Unwarranted high confidence on generated
        )

        doc = FolkloreDocument(
            title="Desert Tale",
            story="A simple story about a traveler in the desert.",
            environmental_knowledge=[unsupported_tek],
            source=source,
        )

        is_valid, errors = validator.validate(doc)
        assert is_valid is False
        assert any("requires explicit source passage evidence" in e for e in errors)
        assert any("cannot have confidence > 0.8" in e for e in errors)

    # 10. Every completed task produces a source manifest.
    def test_completed_task_produces_source_manifest(self, tmp_path):
        output_mgr = TaskOutputManager(base_tasks_dir=str(tmp_path))
        task_id = "test-task-101"

        source_1 = SourceInfo(
            url="https://en.wikipedia.org/wiki/Panchatantra",
            domain="en.wikipedia.org",
            platform_name="Wikipedia",
            source_type=SourceType.WIKI,
        )
        source_2 = SourceInfo(
            url="https://archive.org/details/panchatantra-text",
            domain="archive.org",
            platform_name="Internet Archive",
            source_type=SourceType.ARCHIVE,
        )

        pdoc_1 = PreservedDocument(
            document_id="doc-001",
            source_id=source_1.source_id,
            url=source_1.url,
            original_text="The Panchatantra is an ancient Indian collection of interrelated animal fables.",
            cleaned_text="The Panchatantra is an ancient Indian collection of interrelated animal fables.",
        )
        pdoc_2 = PreservedDocument(
            document_id="doc-002",
            source_id=source_2.source_id,
            url=source_2.url,
            original_text="Mitra-bheda (The Separation of Friends) book 1 translation.",
            cleaned_text="Mitra-bheda (The Separation of Friends) book 1 translation.",
        )

        evidence_1 = Evidence(
            source_id=source_1.source_id,
            document_id="doc-001",
            url=source_1.url,
            claim="Panchatantra animal fables origin",
            evidence_type=EvidenceType.DIRECT,
        )

        fdoc = FolkloreDocument(
            title="The Monkey and the Crocodile",
            story="A tale of quick thinking from the Panchatantra.",
            source=source_1,
            evidence_ids=[evidence_1.evidence_id],
        )

        task_dir = output_mgr.generate_task_bundle(
            task_id=task_id,
            task_name="Panchatantra Fables Collection",
            start_time="2026-09-15T00:00:00Z",
            folklore_docs=[fdoc],
            preserved_docs=[pdoc_1, pdoc_2],
            evidence_list=[evidence_1],
        )

        assert (task_dir / "sources.json").is_file()
        assert (task_dir / "evidence.json").is_file()
        assert (task_dir / "result.json").is_file()
        assert (task_dir / "result.md").is_file()
        assert (task_dir / "metadata.json").is_file()
        assert (task_dir / "original" / "doc-001.txt").is_file()
        assert (task_dir / "cleaned" / "doc-001.txt").is_file()

        with open(task_dir / "sources.json", "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            assert manifest_data["task_id"] == task_id
            assert manifest_data["total_sources"] >= 1
            assert len(manifest_data["sources"]) >= 1
            assert "platform" in manifest_data["sources"][0]
            assert "url" in manifest_data["sources"][0]
