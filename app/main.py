"""Lokkatha Web Intelligence & Scraping System CLI."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app import __version__
from app.config.logging import configure_logging, get_logger
from app.config.settings import get_settings
from app.crawler.manager import CrawlManager
from app.storage.repository import JSONFolkloreRepository

console = Console()
logger = get_logger("cli")


def print_banner() -> None:
    """Display the Lokkatha startup banner."""
    console.print(
        Panel(
            f"[bold green]Lokkatha Web Intelligence & Folklore Scraping System[/bold green]\n"
            f"[dim]Version {__version__} | Cultural Research & Traditional Knowledge Preservation[/dim]",
            border_style="cyan",
        )
    )


async def handle_crawl(args: argparse.Namespace) -> int:
    """Handler for the `crawl` subcommand."""
    settings = get_settings()
    seeds: List[str] = []

    if args.url:
        seeds.append(args.url)

    if args.seeds:
        seed_path = Path(args.seeds)
        if seed_path.is_file():
            with open(seed_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        seeds.append(line)
        else:
            console.print(f"[bold red]Error:[/bold red] Seed file '{args.seeds}' not found.")
            return 1

    if not seeds:
        console.print("[bold yellow]Warning:[/bold yellow] No seed URLs provided. Provide a URL or --seeds file.")
        return 1

    max_pages = args.max_pages or settings.crawler.max_pages
    depth = args.depth if args.depth is not None else settings.crawler.max_depth

    table = Table(title="Lokkatha Crawl Configuration", border_style="cyan")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="bold green")
    table.add_row("Seed URLs", str(len(seeds)))
    table.add_row("Max Pages", str(max_pages))
    table.add_row("Max Depth", str(depth))
    table.add_row("Concurrency", str(settings.crawler.concurrency))
    table.add_row("Respect Robots.txt", str(settings.crawler.respect_robots_txt))
    table.add_row("Delay (s)", str(settings.crawler.delay_seconds))
    console.print(table)

    manager = CrawlManager(settings)
    results = await manager.crawl(seeds=seeds, max_pages=max_pages, max_depth=depth)

    console.print(
        Panel(
            f"[bold green]Crawl Completed[/bold green]\n"
            f"Seeds: {len(seeds)} | Results processed: {len(results)}\n"
            f"Output Directory: [cyan]{settings.storage.structured_dir}[/cyan]",
            border_style="green",
        )
    )
    return 0


def handle_analyze(args: argparse.Namespace) -> int:
    """Handler for the `analyze` subcommand."""
    settings = get_settings()
    target_dir = args.dir or settings.storage.structured_dir
    repo = JSONFolkloreRepository(base_dir=target_dir)
    docs = repo.list_all()

    regions = set()
    languages = set()
    characters = 0
    locations = 0
    environmental_items = 0

    for doc in docs:
        regions.update(doc.region)
        languages.update(doc.language)
        characters += len(doc.characters)
        locations += len(doc.locations)
        environmental_items += len(doc.environmental_knowledge)

    table = Table(title="Folklore Knowledge Repository Analysis", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="bold green")
    table.add_row("Structured Stories", str(len(docs)))
    table.add_row("Distinct Regions", str(len(regions)))
    table.add_row("Distinct Languages", str(len(languages)))
    table.add_row("Characters Extracted", str(characters))
    table.add_row("Locations Extracted", str(locations))
    table.add_row("Environmental Knowledge Items", str(environmental_items))
    console.print(table)
    return 0


def handle_export(args: argparse.Namespace) -> int:
    """Handler for the `export` subcommand."""
    settings = get_settings()
    repo = JSONFolkloreRepository(base_dir=settings.storage.structured_dir)
    docs = repo.list_all()

    output_path = Path(args.output or "data/export.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = args.format.lower()
    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in docs], f, indent=2)
    elif fmt == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for d in docs:
                f.write(d.model_dump_json() + "\n")
    else:
        console.print(f"[bold red]Unsupported format:[/bold red] {fmt}")
        return 1

    console.print(f"[bold green]Exported {len(docs)} documents to {output_path}[/bold green]")
    return 0


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="lokkatha",
        description="Lokkatha Web Intelligence & Folklore Scraping System",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # crawl subcommand
    crawl_parser = subparsers.add_parser("crawl", help="Start web crawler")
    crawl_parser.add_argument("url", nargs="?", help="Direct single target URL to crawl")
    crawl_parser.add_argument("--seeds", type=str, help="Path to seed URLs text file")
    crawl_parser.add_argument("--max-pages", type=int, help="Maximum number of pages to crawl")
    crawl_parser.add_argument("--depth", type=int, help="Maximum crawl depth from seeds")

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze structured folklore data")
    analyze_parser.add_argument("dir", nargs="?", help="Target structured data directory")

    # export subcommand
    export_parser = subparsers.add_parser("export", help="Export structured folklore data")
    export_parser.add_argument("--format", choices=["json", "jsonl"], default="json", help="Export format")
    export_parser.add_argument("--output", type=str, help="Destination file path")

    return parser


def main() -> int:
    """CLI application entrypoint."""
    parser = build_cli_parser()
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(log_level=settings.log_level)

    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    if args.command == "crawl":
        return asyncio.run(handle_crawl(args))
    elif args.command == "analyze":
        return handle_analyze(args)
    elif args.command == "export":
        return handle_export(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
