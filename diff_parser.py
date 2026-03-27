"""
Git diff parser module.
Parses unified diff format into structured change objects for analysis.
"""

import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config import config

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents changes in a single file."""

    filepath: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0
    added_lines: List[str] = field(default_factory=list)
    deleted_lines: List[str] = field(default_factory=list)
    file_extension: str = ""
    is_binary: bool = False

    def __post_init__(self):
        self.file_extension = Path(self.filepath).suffix.lower()


@dataclass
class DiffSummary:
    """Aggregated summary of all changes in a diff."""

    files: List[FileChange] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    total_files_changed: int = 0

    @property
    def file_extensions(self) -> List[str]:
        return list({f.file_extension for f in self.files if f.file_extension})

    @property
    def change_types(self) -> List[str]:
        return list({f.change_type for f in self.files})


def get_staged_diff() -> Optional[str]:
    """Get the staged diff from git (files added with `git add`)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=3"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        logger.info("No staged changes found.")
        return None
    except FileNotFoundError:
        logger.error("Git is not installed or not in PATH.")
        return None
    except subprocess.TimeoutExpired:
        logger.error("Git diff command timed out.")
        return None


def get_unstaged_diff() -> Optional[str]:
    """Get the unstaged diff from git working directory."""
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=3"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def read_diff_from_file(filepath: str) -> Optional[str]:
    """Read a diff from a .diff or .patch file."""
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error(f"Diff file not found: {filepath}")
            return None
        content = path.read_text(encoding="utf-8", errors="replace")
        if content.strip():
            return content
        logger.warning("Diff file is empty.")
        return None
    except Exception as e:
        logger.error(f"Error reading diff file: {e}")
        return None


def parse_diff(diff_text: str) -> DiffSummary:
    """
    Parse a unified diff string into a structured DiffSummary.

    Handles standard unified diff format with ---/+++ file headers,
    @@ hunk headers, and +/- change lines.
    """
    summary = DiffSummary()
    current_file: Optional[FileChange] = None
    lines = diff_text.splitlines()

    # Limit total lines to prevent memory issues with huge diffs
    if len(lines) > config.max_diff_lines:
        logger.warning(
            f"Diff has {len(lines)} lines, truncating to {config.max_diff_lines}."
        )
        lines = lines[: config.max_diff_lines]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect new file diff header
        if line.startswith("diff --git"):
            # Save previous file if exists
            if current_file:
                _classify_change_type(current_file)
                summary.files.append(current_file)

            # Extract file path from diff header
            match = re.search(r"diff --git a/(.+?) b/(.+)", line)
            if match:
                filepath = match.group(2)
            else:
                filepath = "unknown"

            current_file = FileChange(filepath=filepath, change_type="modified")
            i += 1
            continue

        # Detect binary file
        if line.startswith("Binary files"):
            if current_file:
                current_file.is_binary = True
            i += 1
            continue

        # Detect new/deleted file mode
        if line.startswith("new file mode"):
            if current_file:
                current_file.change_type = "added"
            i += 1
            continue

        if line.startswith("deleted file mode"):
            if current_file:
                current_file.change_type = "deleted"
            i += 1
            continue

        # Detect renamed file
        if line.startswith("rename from") or line.startswith("rename to"):
            if current_file:
                current_file.change_type = "renamed"
            i += 1
            continue

        # Parse added/deleted lines
        if line.startswith("+") and not line.startswith("+++"):
            if current_file:
                content = line[1:].strip()
                if content:  # skip blank added lines
                    current_file.added_lines.append(content)
                current_file.additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            if current_file:
                content = line[1:].strip()
                if content:
                    current_file.deleted_lines.append(content)
                current_file.deletions += 1

        i += 1

    # Don't forget the last file
    if current_file:
        _classify_change_type(current_file)
        summary.files.append(current_file)

    # Compute totals
    summary.total_files_changed = len(summary.files)
    summary.total_additions = sum(f.additions for f in summary.files)
    summary.total_deletions = sum(f.deletions for f in summary.files)

    logger.info(
        f"Parsed diff: {summary.total_files_changed} files, "
        f"+{summary.total_additions}/-{summary.total_deletions} lines"
    )
    return summary


def _classify_change_type(fc: FileChange) -> None:
    """Refine change type based on line counts if not already set by mode."""
    if fc.change_type != "modified":
        return
    if fc.additions > 0 and fc.deletions == 0:
        fc.change_type = "added"
    elif fc.deletions > 0 and fc.additions == 0:
        fc.change_type = "deleted"
