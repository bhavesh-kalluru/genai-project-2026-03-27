#!/usr/bin/env python3
"""
Semantic Commit Message Generator
==================================
Analyzes git diffs and generates meaningful conventional commit messages
using sentence-transformer embeddings and semantic pattern matching.

Usage:
    # Analyze staged changes (git add first)
    python main.py

    # Analyze a .diff or .patch file
    python main.py --file changes.diff

    # Include unstaged changes too
    python main.py --unstaged

    # Output as JSON (for CI/CD integration)
    python main.py --format json

    # Run with demo data
    python main.py --demo
"""

import argparse
import logging
import sys
from pathlib import Path

from config import config
from diff_parser import (
    DiffSummary,
    get_staged_diff,
    get_unstaged_diff,
    parse_diff,
    read_diff_from_file,
)
from engine import generate_commit_messages
from utils import (
    colorize,
    format_suggestions_json,
    format_suggestions_plain,
    format_suggestions_terminal,
    setup_logging,
)

logger = logging.getLogger(__name__)

# Path to built-in demo diff file
DEMO_DIFF_PATH = Path(__file__).parent / "data" / "demo.diff"


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="commit-gen",
        description=(
            "Semantic Commit Message Generator — analyzes git diffs and generates "
            "conventional commit messages using NLP embeddings."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s                   Analyze staged changes\n"
            "  %(prog)s --file patch.diff  Analyze a diff file\n"
            "  %(prog)s --demo             Run with demo data\n"
            "  %(prog)s --format json      Output as JSON\n"
        ),
    )

    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Path to a .diff or .patch file to analyze",
    )
    parser.add_argument(
        "--unstaged",
        action="store_true",
        help="Include unstaged changes (working directory diff)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with a built-in demo diff for testing",
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json", "plain"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    parser.add_argument(
        "--suggestions", "-n",
        type=int,
        default=config.max_suggestions,
        help=f"Number of suggestions to generate (default: {config.max_suggestions})",
    )
    parser.add_argument(
        "--no-body",
        action="store_true",
        help="Omit the commit body from suggestions",
    )
    parser.add_argument(
        "--no-scope",
        action="store_true",
        help="Omit scope from commit messages",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=config.similarity_threshold,
        help=f"Minimum similarity threshold (default: {config.similarity_threshold})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    return parser.parse_args()


def get_diff_text(args: argparse.Namespace) -> str:
    """Obtain diff text from the appropriate source."""
    # Demo mode — read from bundled demo.diff file
    if args.demo:
        logger.info("Using built-in demo diff.")
        if DEMO_DIFF_PATH.exists():
            return DEMO_DIFF_PATH.read_text(encoding="utf-8")
        else:
            print(
                colorize(
                    f"  Error: Demo diff not found at {DEMO_DIFF_PATH}", "red"
                ),
                file=sys.stderr,
            )
            sys.exit(1)

    # File mode
    if args.file:
        diff = read_diff_from_file(args.file)
        if diff:
            return diff
        print(
            colorize(f"  Error: Could not read diff file: {args.file}", "red"),
            file=sys.stderr,
        )
        sys.exit(1)

    # Git staged changes
    diff = get_staged_diff()

    # Optionally include unstaged
    if args.unstaged:
        unstaged = get_unstaged_diff()
        if unstaged:
            diff = (diff or "") + "\n" + unstaged

    if not diff:
        print(
            colorize(
                "\n  No changes detected.\n\n"
                "  Stage your changes first:  git add <files>\n"
                "  Or use --file to analyze a .diff file\n"
                "  Or use --demo to try with sample data\n",
                "yellow",
            ),
            file=sys.stderr,
        )
        sys.exit(0)

    return diff


def main():
    """Main entry point."""
    args = parse_arguments()

    # Configure
    log_level = "DEBUG" if args.verbose else config.log_level
    setup_logging(level=log_level, log_file=config.log_file)

    config.max_suggestions = args.suggestions
    config.similarity_threshold = args.threshold
    if args.no_body:
        config.include_body = False
    if args.no_scope:
        config.include_scope = False

    logger.info("Semantic Commit Message Generator starting...")

    # Get diff
    diff_text = get_diff_text(args)

    # Parse
    summary: DiffSummary = parse_diff(diff_text)
    logger.info(
        f"Parsed: {summary.total_files_changed} files, "
        f"+{summary.total_additions}/-{summary.total_deletions}"
    )

    if summary.total_files_changed == 0:
        print(colorize("  No meaningful changes found in diff.", "yellow"))
        sys.exit(0)

    # Generate suggestions
    suggestions = generate_commit_messages(summary)

    # Output
    if args.format == "json":
        print(format_suggestions_json(suggestions))
    elif args.format == "plain":
        print(format_suggestions_plain(suggestions))
    else:
        print(format_suggestions_terminal(suggestions))


if __name__ == "__main__":
    main()
