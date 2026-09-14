"""Tests for content extraction, boilerplate removal, and language detection."""

from bs4 import BeautifulSoup
from app.extraction.article import ArticleExtractor
from app.extraction.boilerplate import BoilerplateCleaner
from app.extraction.language import LanguageDetector
from app.extraction.metadata import MetadataExtractor


def test_language_detector_indic_scripts():
    detector = LanguageDetector()

    # Hindi Devanagari text
    hindi_text = "एक समय की बात है, राजस्थान के रेगिस्तान में एक राजा राज्य करता था।"
    assert detector.detect(hindi_text) == "hi"

    # Bengali text
    bengali_text = "এক দেশে এক রাজা ছিল, তার ছিল সাত রানী এবং এক রাজপুত্র।"
    assert detector.detect(bengali_text) == "bn"

    # Tamil text
    tamil_text = "ஒரு ஊரில் ஒரு ராஜா இருந்தார், அவர் மக்களுக்கு பல நன்மைகளை செய்தார்."
    assert detector.detect(tamil_text) == "ta"

    # English text
    english_text = "Long ago in the Thar desert of Rajasthan, there lived a legendary storyteller."
    assert detector.detect(english_text) == "en"

    # Empty text
    assert detector.detect("") is None


def test_article_extractor_html_parsing():
    extractor = ArticleExtractor()
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>The Legend of Princess Mumal</title></head>
    <body>
        <nav><a href="/">Home</a></nav>
        <article>
            <h1>The Tale of Mumal and Mahendra</h1>
            <p>Mumal was a legendary Rajput princess of Lodrawa near Jaisalmer.</p>
            <p>Mahendra, the prince of Umerkot, fell deeply in love with her across the deserts.</p>
        </article>
        <script>console.log("analytics");</script>
        <footer>Copyright 2026 Lokkatha</footer>
    </body>
    </html>
    """
    doc = extractor.extract(sample_html, url="https://example.org/folktales/mumal")

    assert doc.url == "https://example.org/folktales/mumal"
    assert "Mumal" in doc.title
    assert "Mumal was a legendary Rajput princess" in doc.main_text
    assert len(doc.paragraphs) >= 1
    assert "analytics" not in doc.main_text


def test_boilerplate_cleaner():
    cleaner = BoilerplateCleaner()
    dirty_html = "<div><nav>Menu</nav><article><p>Once upon a time in Kutch.</p></article><footer>Copyright</footer></div>"
    soup = BeautifulSoup(dirty_html, "lxml")
    cleaned_soup = cleaner.clean(soup)
    assert cleaned_soup.find("nav") is None
    assert cleaned_soup.find("footer") is None
    assert "Once upon a time in Kutch." in cleaned_soup.get_text()


def test_metadata_extractor():
    extractor = MetadataExtractor()
    sample_html = """
    <html>
    <head>
        <meta name="author" content="Dr. Komal Kothari">
        <meta name="description" content="Desert folklore and music of western Rajasthan">
        <meta property="og:title" content="Arna Jharna Folklore Archive">
    </head>
    <body>Content</body>
    </html>
    """
    soup = BeautifulSoup(sample_html, "lxml")
    meta = extractor.extract_metadata(soup)
    assert meta.get("author") == "Dr. Komal Kothari"
    assert meta.get("description") == "Desert folklore and music of western Rajasthan"
    author = extractor.extract_author(meta, soup)
    assert author == "Dr. Komal Kothari"
