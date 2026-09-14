"""Tests for JSON repository and storage utilities."""

import tempfile
from app.schemas.folklore import FolkloreDocument, FolkloreType
from app.schemas.source import SourceInfo
from app.storage.repository import JSONFolkloreRepository


def test_json_folklore_repository():
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo = JSONFolkloreRepository(base_dir=tmp_dir)

        doc = FolkloreDocument(
            id="folk-rajasthan-pabu-ji",
            title="The Epic of Pabuji Rathore",
            folklore_type=FolkloreType.HEROIC_TALE,
            region=["Rajasthan"],
            language=["hi"],
            story="Pabuji was a folk-deity of Rajasthan worshipped by the Rebari community.",
            source=SourceInfo(url="https://example.org/pabuji", domain="example.org"),
        )

        # Test Save
        saved_path = repo.save(doc)
        assert saved_path.is_file()

        # Test Get by ID
        retrieved = repo.get_by_id("folk-rajasthan-pabu-ji")
        assert retrieved is not None
        assert retrieved.title == "The Epic of Pabuji Rathore"
        assert retrieved.id == doc.id

        # Test List All
        all_docs = repo.list_all()
        assert len(all_docs) == 1
        assert all_docs[0].id == "folk-rajasthan-pabu-ji"

        # Non-existent
        assert repo.get_by_id("non-existent-id") is None
