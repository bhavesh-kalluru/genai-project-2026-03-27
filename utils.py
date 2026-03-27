"""
Utility functions for formatting, display, and output.
"""

import json
import logging
import sys
from typing import List

from engine import CommitSuggestion

logger = logging.getLogger(__name__)

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "red": "\033[91m",
    "magenta": "\033[95m",
    "white": "\033[97m",
    "gray": "\033[90m",
}

# Disable colors if not a TTY (e.g., piped output)
if not sys.stdout.isatty():
    COLORS = {k: "" for k in COLORS}


def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def confidence_color(score: float) -> str:
    """Return color name based on confidence score."""
    if score >= 70:
        return "green"
    elif score >= 50:
        return "yellow"
    elif score >= 30:
        return "cyan"
    return "dim"


def format_suggestions_terminal(suggestions: List[CommitSuggestion]) -> str:
    """Format commit suggestions for terminal display with colors."""
    if not suggestions:
        return colorize("  No commit message suggestions generated.", "yellow")

    lines = []
    lines.append("")
    lines.append(colorize("═" * 60, "blue"))
    lines.append(colorize("  COMMIT MESSAGE SUGGESTIONS", "bold"))
    lines.append(colorize("═" * 60, "blue"))

    for i, s in enumerate(suggestions, 1):
        conf_color = confidence_color(s.confidence)
        conf_bar = _confidence_bar(s.confidence)

        lines.append("")
        lines.append(
            f"  {colorize(f'#{i}', 'bold')}  "
            f"{colorize(f'[{s.confidence}%]', conf_color)}  "
            f"{conf_bar}  "
            f"{colorize(f'pattern: {s.matched_pattern}', 'gray')}"
        )
        lines.append(colorize("  ─" * 28, "dim"))

        # Full commit message
        lines.append(f"  {colorize(s.full_message.split(chr(10))[0], 'green')}")

        # Body (if present)
        if s.body:
            for body_line in s.body.split("\n"):
                lines.append(f"  {colorize(body_line, 'dim')}")

    lines.append("")
    lines.append(colorize("═" * 60, "blue"))
    lines.append("")
    lines.append(
        colorize("  Tip: ", "bold")
        + colorize(
            "Copy the suggestion and run: git commit -m \"<message>\"", "gray"
        )
    )
    lines.append("")

    return "\n".join(lines)


def _confidence_bar(score: float, width: int = 15) -> str:
    """Render a visual confidence bar."""
    filled = int(score / 100 * width)
    empty = width - filled
    color = confidence_color(score)
    bar = colorize("█" * filled, color) + colorize("░" * empty, "dim")
    return f"[{bar}]"


def format_suggestions_json(suggestions: List[CommitSuggestion]) -> str:
    """Format commit suggestions as JSON for machine consumption."""
    data = [
        {
            "rank": i + 1,
            "type": s.commit_type,
            "scope": s.scope,
            "subject": s.subject,
            "body": s.body,
            "full_message": s.full_message,
            "confidence": s.confidence,
            "matched_pattern": s.matched_pattern,
        }
        for i, s in enumerate(suggestions)
    ]
    return json.dumps(data, indent=2)


def format_suggestions_plain(suggestions: List[CommitSuggestion]) -> str:
    """Format suggestions as plain text (for piping)."""
    if not suggestions:
        return "No suggestions generated."

    lines = []
    for i, s in enumerate(suggestions, 1):
        lines.append(f"--- Suggestion #{i} (confidence: {s.confidence}%) ---")
        lines.append(s.full_message)
        lines.append("")
    return "\n".join(lines)


def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """Configure logging for the application."""
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stderr)]

    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode="a")
            file_handler.setFormatter(
                logging.Formatter(log_format, datefmt=date_format)
            )
            handlers.append(file_handler)
        except OSError as e:
            print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )
