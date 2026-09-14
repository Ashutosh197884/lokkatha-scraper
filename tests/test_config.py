"""Tests for settings and configuration loading."""

import os
from app.config.settings import Settings, get_settings, load_yaml_config


def test_load_yaml_config_existing():
    """Test loading configuration from config.yaml."""
    config_dict = load_yaml_config("config.yaml")
    assert isinstance(config_dict, dict)
    assert "crawler" in config_dict
    assert config_dict["crawler"]["max_depth"] == 4


def test_load_yaml_config_missing():
    """Test missing configuration file returns empty dict."""
    config_dict = load_yaml_config("nonexistent_config.yaml")
    assert config_dict == {}


def test_get_settings_defaults():
    """Test Settings object instantiation with defaults."""
    settings = get_settings()
    assert settings.project.name == "lokkatha-scraper"
    assert settings.crawler.max_depth == 4
    assert settings.crawler.concurrency == 5
    assert settings.crawler.delay_seconds == 1.0
    assert settings.deduplication.similarity_threshold == 0.90
    assert "facebook.com" in settings.domains.deny


def test_settings_env_override(monkeypatch):
    """Test environment variable overriding settings."""
    monkeypatch.setenv("LOKKATHA_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOKKATHA_ENV", "testing")
    settings = Settings()
    assert settings.log_level == "DEBUG"
    assert settings.env == "testing"
