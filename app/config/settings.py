"""Configuration management for Lokkatha Scraper using pydantic-settings and PyYAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional
import os
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectSettings(BaseModel):
    name: str = "lokkatha-scraper"
    version: str = "0.1.0"
    description: str = "Web Intelligence and Folklore Scraping System"


class CrawlerSettings(BaseModel):
    max_pages: int = Field(default=1000, ge=1)
    max_depth: int = Field(default=4, ge=0)
    concurrency: int = Field(default=5, ge=1)
    request_timeout: float = Field(default=20.0, ge=1.0)
    delay_seconds: float = Field(default=1.0, ge=0.0)
    follow_external_links: bool = False
    respect_robots_txt: bool = True
    save_raw_html: bool = True
    max_content_size_mb: float = Field(default=10.0, ge=0.1)
    user_agent: str = "LokkathaBot/0.1 (+https://lokkatha.org/bot; cultural-research-crawler)"


class RobotsSettings(BaseModel):
    enabled: bool = True
    cache_ttl_seconds: int = 86400


class BrowserSettings(BaseModel):
    enabled: bool = True
    headless: bool = True
    timeout_seconds: float = 30.0


class StorageSettings(BaseModel):
    raw_dir: str = "data/raw"
    cleaned_dir: str = "data/cleaned"
    structured_dir: str = "data/structured"
    rejected_dir: str = "data/rejected"
    save_raw: bool = True
    save_cleaned: bool = True
    save_structured: bool = True


class DeduplicationSettings(BaseModel):
    exact: bool = True
    semantic: bool = True
    similarity_threshold: float = Field(default=0.90, ge=0.0, le=1.0)


class AISettings(BaseModel):
    enabled: bool = False
    extraction: bool = True
    environmental_analysis: bool = True
    provider: str = "none"
    model: str = "none"


class DomainPolicySettings(BaseModel):
    allow: List[str] = Field(default_factory=list)
    deny: List[str] = Field(default_factory=lambda: [
        "facebook.com",
        "instagram.com",
        "youtube.com",
        "twitter.com",
        "x.com",
        "pinterest.com",
        "tiktok.com"
    ])


class DatabaseSettings(BaseModel):
    enabled: bool = False
    host: str = "localhost"
    port: int = 5432
    name: str = "lokkatha"
    user: str = "postgres"
    password: str = ""

    @property
    def connection_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    """Global Application Settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )

    env: str = Field(default="development", alias="LOKKATHA_ENV")
    log_level: str = Field(default="INFO", alias="LOKKATHA_LOG_LEVEL")

    project: ProjectSettings = Field(default_factory=ProjectSettings)
    crawler: CrawlerSettings = Field(default_factory=CrawlerSettings)
    robots: RobotsSettings = Field(default_factory=RobotsSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    deduplication: DeduplicationSettings = Field(default_factory=DeduplicationSettings)
    ai: AISettings = Field(default_factory=AISettings)
    domains: DomainPolicySettings = Field(default_factory=DomainPolicySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


def load_yaml_config(config_path: Path | str = "config.yaml") -> dict[str, Any]:
    """Load configuration from a YAML file if present."""
    path = Path(config_path)
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


@lru_cache(maxsize=1)
def get_settings(config_path: str = "config.yaml") -> Settings:
    """Get initialized and cached Application Settings."""
    yaml_data = load_yaml_config(config_path)
    return Settings(**yaml_data)
