"""Internal and outgoing hyperlink extractor using BeautifulSoup."""

from typing import List, Set
from bs4 import BeautifulSoup

from app.config.logging import get_logger
from app.utils.urls import extract_domain, is_valid_url, normalize_url, resolve_relative_url

logger = get_logger("discovery.links")


class LinkExtractor:
    """Extracts, normalizes, and filters hyperlinks from HTML content."""

    def extract_from_html(
        self,
        base_url: str,
        html_content: str,
        allow_external: bool = False
    ) -> List[str]:
        """Parse HTML and return list of resolved, unique, and normalized URLs."""
        if not html_content:
            return []

        try:
            soup = BeautifulSoup(html_content, "lxml")
        except Exception:
            soup = BeautifulSoup(html_content, "html.parser")

        hrefs: List[str] = []
        for tag in soup.find_all(["a", "link", "area"]):
            href = tag.get("href")
            if href:
                hrefs.append(href.strip())

        return self.extract_links(base_url, hrefs, allow_external=allow_external)

    def extract_links(
        self,
        base_url: str,
        hrefs: List[str],
        allow_external: bool = False
    ) -> List[str]:
        """Resolve and filter links from a list of href strings."""
        base_domain = extract_domain(base_url)
        discovered: Set[str] = set()

        for href in hrefs:
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                continue

            resolved = resolve_relative_url(base_url, href)
            if not is_valid_url(resolved):
                continue

            target_domain = extract_domain(resolved)
            if not allow_external and target_domain != base_domain:
                continue

            discovered.add(resolved)

        return sorted(list(discovered))
