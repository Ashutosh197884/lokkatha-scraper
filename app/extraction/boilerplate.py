"""Boilerplate, navigation, advertising, and footer cleaner."""

from bs4 import BeautifulSoup

BOILERPLATE_SELECTORS = [
    "nav",
    "footer",
    "header",
    "aside",
    ".nav",
    ".menu",
    ".footer",
    ".sidebar",
    ".advertisement",
    ".ad-container",
    ".cookie-banner",
    ".social-share",
    "#comments",
    ".comments-area",
]


class BoilerplateCleaner:
    """Removes navigation menus, sidebars, advertisement units, and comments."""

    def clean(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Strip boilerplate DOM elements in-place."""
        for selector in BOILERPLATE_SELECTORS:
            for match in soup.select(selector):
                match.decompose()
        return soup
