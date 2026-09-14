"""Tests for domain policy filtering and allow/deny rules."""

from app.config.settings import DomainPolicySettings
from app.crawler.domain_filter import DomainFilter


def test_domain_filter_default_deny():
    """Test standard denylist blocks social media domains."""
    filter_engine = DomainFilter()
    allowed, reason = filter_engine.is_allowed("https://facebook.com/story")
    assert allowed is False
    assert "denied_by_rule" in reason

    allowed, reason = filter_engine.is_allowed("https://sub.instagram.com/p/123")
    assert allowed is False


def test_domain_filter_allowlist_wildcard():
    """Test wildcard matching on government and academic domains (*.gov.in, *.ac.in)."""
    policy = DomainPolicySettings(
        allow=["*.gov.in", "*.ac.in", "sahapedia.org"],
        deny=["blocked.gov.in"]
    )
    filter_engine = DomainFilter(policy=policy)

    # Allowed by wildcard
    allowed, _ = filter_engine.is_allowed("https://ignca.gov.in/stories")
    assert allowed is True

    allowed, _ = filter_engine.is_allowed("https://tribal.ac.in/folklore")
    assert allowed is True

    allowed, _ = filter_engine.is_allowed("https://sahapedia.org/article")
    assert allowed is True

    # Denied by explicit deny list even though matching wildcard
    allowed, reason = filter_engine.is_allowed("https://blocked.gov.in/page")
    assert allowed is False
    assert "denied_by_rule" in reason

    # Denied because not in allow list
    allowed, reason = filter_engine.is_allowed("https://random-commercial-site.com/tale")
    assert allowed is False
    assert reason == "not_in_allowlist"


def test_domain_filter_invalid_urls():
    """Test invalid or empty URLs."""
    filter_engine = DomainFilter()
    assert filter_engine.is_allowed("")[0] is False
    assert filter_engine.is_allowed("not_a_valid_url")[0] is False
