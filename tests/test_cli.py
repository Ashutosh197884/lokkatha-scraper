"""Tests for CLI parsing and dispatching."""

import pytest
from app import __version__
from app.main import build_cli_parser, handle_analyze, handle_export


def test_cli_parser_version():
    """Test version argument definition."""
    parser = build_cli_parser()
    assert parser.prog == "lokkatha"


def test_cli_parser_crawl_command():
    """Test parsing crawl command arguments."""
    parser = build_cli_parser()
    args = parser.parse_args(["crawl", "https://example.org", "--max-pages", "50", "--depth", "2"])
    assert args.command == "crawl"
    assert args.url == "https://example.org"
    assert args.max_pages == 50
    assert args.depth == 2


def test_cli_parser_analyze_command():
    """Test parsing analyze command arguments."""
    parser = build_cli_parser()
    args = parser.parse_args(["analyze", "data/structured"])
    assert args.command == "analyze"
    assert args.dir == "data/structured"


def test_cli_parser_export_command():
    """Test parsing export command arguments."""
    parser = build_cli_parser()
    args = parser.parse_args(["export", "--format", "jsonl", "--output", "data/out.jsonl"])
    assert args.command == "export"
    assert args.format == "jsonl"
    assert args.output == "data/out.jsonl"


def test_handle_analyze_empty_dir(tmp_path):
    """Test analyze handler executes cleanly on empty directory."""
    parser = build_cli_parser()
    args = parser.parse_args(["analyze", str(tmp_path)])
    exit_code = handle_analyze(args)
    assert exit_code == 0
