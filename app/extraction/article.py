"""Main article content extractor using BeautifulSoup and lxml heuristics."""

from bs4 import BeautifulSoup
from app.config.logging import get_logger
from app.extraction.document import ParsedWebDocument
from app.utils.text import clean_whitespace, extract_paragraphs

logger = get_logger("extraction.article")


class ArticleExtractor:
    """Extracts primary body text and headlines from HTML documents."""

    def extract(self, html: str, url: str) -> ParsedWebDocument:
        """Parse HTML and extract cleaned article text."""
        if not html:
            return ParsedWebDocument(url=url)

        soup = BeautifulSoup(html, "lxml")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else ""

        # Remove script and style tags
        for el in soup(["script", "style", "noscript", "svg"]):
            el.decompose()

        # Extract main text
        body = soup.find("article") or soup.find("main") or soup.body or soup
        text = body.get_text() if body else ""
        cleaned = clean_whitespace(text)
        paragraphs = extract_paragraphs(cleaned)

        return ParsedWebDocument(
            url=url,
            title=title,
            main_text=cleaned,
            paragraphs=paragraphs,
        )
