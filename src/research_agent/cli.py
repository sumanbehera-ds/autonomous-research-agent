from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from research_agent.memory import ResearchMemory
from research_agent.pipeline import ResearchAgent


KNOWN_COMMANDS = {"run", "history", "show", "-h", "--help"}


def main(argv: list[str] | None = None) -> int:
    load_dotenv()

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in KNOWN_COMMANDS:
        argv = ["run", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "history":
        return command_history(args)
    if args.command == "show":
        return command_show(args)
    if args.command == "run":
        return command_run(args)

    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-agent",
        description="Autonomous Research Agent for Assessment Option 1.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run an autonomous research task.")
    run_parser.add_argument("topic", nargs="+", help="Research topic or question.")
    run_parser.add_argument("--max-queries", type=int, default=3, help="Number of LLM-generated search queries.")
    run_parser.add_argument("--max-sources", type=int, default=6, help="Maximum sources to analyze.")
    run_parser.add_argument(
        "--max-results-per-query",
        type=int,
        default=5,
        help="Search results to collect per generated query.",
    )
    run_parser.add_argument("--output-dir", default="reports", help="Folder for generated reports.")
    run_parser.add_argument(
        "--memory-db",
        default=".agent_memory/research_history.sqlite3",
        help="SQLite memory database path.",
    )
    run_parser.add_argument("--pdf", action="store_true", help="Also export a PDF report.")

    history_parser = subparsers.add_parser("history", help="Show previous research runs.")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of runs to show.")
    history_parser.add_argument(
        "--memory-db",
        default=".agent_memory/research_history.sqlite3",
        help="SQLite memory database path.",
    )

    show_parser = subparsers.add_parser("show", help="Show details for one previous run.")
    show_parser.add_argument("run_id", type=int, help="Memory run ID.")
    show_parser.add_argument(
        "--memory-db",
        default=".agent_memory/research_history.sqlite3",
        help="SQLite memory database path.",
    )

    return parser


def command_run(args: argparse.Namespace) -> int:
    topic = " ".join(args.topic)

    def print_event(stage: str, message: str) -> None:
        print(f"[{stage}] {message}")

    try:
        agent = ResearchAgent.from_environment(
            output_dir=args.output_dir,
            memory_db=args.memory_db,
            on_event=print_event,
        )
        result = agent.run(
            topic,
            max_queries=args.max_queries,
            max_sources=args.max_sources,
            max_results_per_query=args.max_results_per_query,
            export_pdf=args.pdf,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print()
    print("Research complete.")
    print(f"Memory ID: {result.memory_id}")
    print(f"Markdown: {Path(result.markdown_path).resolve()}")
    if result.pdf_path:
        print(f"PDF: {Path(result.pdf_path).resolve()}")
    print(f"Sources used: {len(result.analyzed_sources)}")
    return 0


def command_history(args: argparse.Namespace) -> int:
    memory = ResearchMemory(Path(args.memory_db))
    rows = memory.list_runs(limit=args.limit)
    if not rows:
        print("No research history found.")
        return 0

    for row in rows:
        print(f"{row['id']}. {row['topic']}")
        print(f"   Created: {row['created_at']}")
        print(f"   Report: {row['report_path']}")
        if row["pdf_path"]:
            print(f"   PDF: {row['pdf_path']}")
        print()
    return 0


def command_show(args: argparse.Namespace) -> int:
    memory = ResearchMemory(Path(args.memory_db))
    row = memory.get_run(args.run_id)
    if not row:
        print(f"No run found for ID {args.run_id}.", file=sys.stderr)
        return 1

    print(f"ID: {row['id']}")
    print(f"Topic: {row['topic']}")
    print(f"Created: {row['created_at']}")
    print(f"Report: {row['report_path']}")
    if row["pdf_path"]:
        print(f"PDF: {row['pdf_path']}")
    print()
    print("Plan:")
    print(f"  Intent: {row['plan'].get('intent')}")
    print(f"  Source strategy: {row['plan'].get('source_strategy')}")
    print("  Queries:")
    for query in row["plan"].get("search_queries", []):
        print(f"   - {query}")
    print()
    print("Sources:")
    for source in row["sources"]:
        print(f"  - {source.get('title')} ({source.get('url')})")
    return 0
