"""Domain policy filtering with exact match, wildcard matching, and allow/deny precedence."""

import fnmatch
from typing import List, Optional, Tuple
from app.config.logging import get_logger
from app.config.settings import DomainPolicySettings
from app.utils.urls import extract_domain, extract_hostname

logger = get_logger("crawler.domain_filter")


class DomainFilter:
    """Evaluates whether a URL or domain is permitted for crawling based on configured policy."""

    def __init__(self, policy: Optional[DomainPolicySettings] = None) -> None:
        self.policy = policy or DomainPolicySettings()

    def _matches_pattern(self, host_or_domain: str, pattern: str) -> bool:
        """Check if domain or host matches an exact string or wildcard pattern (e.g. '*.gov.in')."""
        host_or_domain = host_or_domain.lower().strip()
        pattern = pattern.lower().strip()

        if host_or_domain == pattern:
            return True

        if pattern.startswith("*."):
            suffix = pattern[2:]
            if host_or_domain == suffix or host_or_domain.endswith("." + suffix):
                return True

        return fnmatch.fnmatch(host_or_domain, pattern)

    def is_allowed(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if URL's domain is allowed.
        Returns (is_allowed, rejection_reason).
        """
        if not url:
            return False, "empty_url"

        domain = extract_domain(url)
        hostname = extract_hostname(url)

        if not domain and not hostname:
            return False, "invalid_domain"

        # Check deny rules first (Deny takes precedence)
        for deny_pattern in self.policy.deny:
            if self._matches_pattern(domain, deny_pattern) or (hostname and self._matches_pattern(hostname, deny_pattern)):
                logger.debug("domain_denied", url=url, pattern=deny_pattern)
                return False, f"denied_by_rule:{deny_pattern}"

        # If allow list is configured, domain MUST match an allow rule
        if self.policy.allow:
            for allow_pattern in self.policy.allow:
                if self._matches_pattern(domain, allow_pattern) or (hostname and self._matches_pattern(hostname, allow_pattern)):
                    return True, None
            logger.debug("domain_not_in_allowlist", url=url, domain=domain)
            return False, "not_in_allowlist"

        # If no allowlist is specified, default to allowed unless in denylist
        return True, None
