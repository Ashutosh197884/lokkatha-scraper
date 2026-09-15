"""Post-crawl extraction pipeline: converts fetched pages into structured folklore records.

Wires the previously disconnected extraction/folklore/storage modules into the crawl
output so that `crawl` produces structured, deduplicated, evidence-backed documents.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.deduplication.exact import ExactContentDeduplicator
from app.extraction.article import ArticleExtractor
from app.extraction.boilerplate import BoilerplateCleaner
from app.extraction.language import LanguageDetector
from app.folklore.classifier import FolkloreClassifier
from app.folklore.extractor import BaselineFolkloreExtractor
from app.discovery.registry import SourceRegistry
from app.schemas.crawl import CrawlResult
from app.schemas.evidence import Evidence
from app.schemas.folklore import FolkloreDocument
from app.utils.hashing import compute_sha256
from app.utils.text import count_words

logger = get_logger("pipeline")

# Pages with fewer words than this are considered navigation/boilerplate noise.
MIN_STORY_WORDS = 60


def process_crawl_results(
    results: List[CrawlResult],
    settings: Optional[Settings] = None,
) -> Tuple[List[FolkloreDocument], List[Evidence], int]:
    """Convert successful crawl results into structured folklore documents + evidence.

    Applies: boilerplate removal → article extraction → length gate → folklore
    classification → exact content deduplication → evidence-backed extraction.

    Returns (documents, evidence_records, duplicate_count).
    """
    settings = settings or get_settings()
    article_extractor = ArticleExtractor()
    boilerplate_cleaner = BoilerplateCleaner()
    language_detector = LanguageDetector()
    classifier = FolkloreClassifier()
    extractor = BaselineFolkloreExtractor()
    content_dedup = ExactContentDeduplicator()

    docs: List[FolkloreDocument] = []
    evidence: List[Evidence] = []
    duplicates = 0

    for result in results:
        if not result.is_success or not result.raw_html_path:
            continue

        try:
            html = Path(result.raw_html_path).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("pipeline_raw_html_unreadable", path=result.raw_html_path, error=str(exc))
            continue

        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")
        soup = boilerplate_cleaner.clean(soup)
        parsed = article_extractor.extract(str(soup), url=result.url)

        text = parsed.main_text
        if count_words(text) < MIN_STORY_WORDS:
            logger.debug("pipeline_page_too_short", url=result.url, words=count_words(text))
            continue

        if not parsed.title or not parsed.title.strip():
            # Untitled pages would all collapse onto the same canonical id.
            logger.debug("pipeline_page_untitled_skipped", url=result.url)
            continue

        cls_result = classifier.classify(text, title=parsed.title)
        if not cls_result.is_folklore:
            logger.debug("pipeline_page_not_folklore", url=result.url, title=parsed.title)
            continue

        content_hash = result.content_hash or compute_sha256(html)
        is_new, _ = content_dedup.add(content_hash)
        if not is_new:
            duplicates += 1
            logger.debug("pipeline_duplicate_content", url=result.url, content_hash=content_hash)
            continue

        source = SourceRegistry.create_source_info(url=result.url, page_title=parsed.title)
        source.content_hash = content_hash
        source.http_status = result.status_code
        source.content_type = result.content_type

        doc, doc_evidence = extractor.extract_with_evidence(
            text=text,
            source=source,
            title=parsed.title,
        )

        language = language_detector.detect(text)
        if language and language != "unknown":
            doc.language = [language]
        doc.folklore_type = cls_result.type if cls_result.is_folklore else doc.folklore_type

        docs.append(doc)
        evidence.extend(doc_evidence)

    logger.info(
        "pipeline_processing_completed",
        pages_input=len(results),
        folklore_extracted=len(docs),
        duplicates_skipped=duplicates,
        evidence_records=len(evidence),
    )
    return docs, evidence, duplicates
