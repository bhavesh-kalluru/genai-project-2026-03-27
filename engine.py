"""
Semantic Commit Engine.

Core intelligence module that:
1. Converts diff changes into natural language descriptions
2. Embeds descriptions using sentence-transformers
3. Matches against known commit patterns via cosine similarity
4. Generates conventional commit messages with type, scope, subject, and body
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from config import config
from diff_parser import DiffSummary, FileChange
from templates import COMMIT_PATTERNS, CommitPattern

logger = logging.getLogger(__name__)

# Lazy-loaded model reference
_model = None
_pattern_embeddings = None


@dataclass
class CommitSuggestion:
    """A generated commit message suggestion."""

    commit_type: str
    scope: Optional[str]
    subject: str
    body: Optional[str]
    confidence: float
    matched_pattern: str
    full_message: str = ""

    def __post_init__(self):
        self.full_message = self._format_message()

    def _format_message(self) -> str:
        """Format as conventional commit string."""
        prefix = self.commit_type
        if self.scope:
            prefix = f"{self.commit_type}({self.scope})"
        msg = f"{prefix}: {self.subject}"
        if self.body:
            msg += f"\n\n{self.body}"
        return msg


def _load_model():
    """Load the sentence-transformer model with fallback handling."""
    global _model
    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading embedding model: {config.embedding_model}")
        _model = SentenceTransformer(config.embedding_model)
        logger.info("Model loaded successfully.")
        return _model
    except Exception as e:
        logger.warning(f"Failed to load sentence-transformers model: {e}")
        if config.use_fallback_on_model_failure:
            logger.info("Falling back to keyword-based matching.")
            return None
        raise


def _get_pattern_embeddings() -> Optional[np.ndarray]:
    """Compute and cache embeddings for all commit patterns."""
    global _pattern_embeddings
    if _pattern_embeddings is not None:
        return _pattern_embeddings

    model = _load_model()
    if model is None:
        return None

    descriptions = [p.description for p in COMMIT_PATTERNS]
    _pattern_embeddings = model.encode(descriptions, normalize_embeddings=True)
    logger.info(f"Computed embeddings for {len(COMMIT_PATTERNS)} commit patterns.")
    return _pattern_embeddings


def _describe_changes(summary: DiffSummary) -> str:
    """
    Convert a DiffSummary into a natural language description
    that captures the semantic intent of the changes.
    """
    parts = []

    # File-level descriptions
    for fc in summary.files[: config.max_file_context]:
        desc = _describe_file_change(fc)
        if desc:
            parts.append(desc)

    # Aggregate stats
    ext_counts = Counter(f.file_extension for f in summary.files if f.file_extension)
    if ext_counts:
        top_exts = ", ".join(f"{ext}({n})" for ext, n in ext_counts.most_common(3))
        parts.append(f"File types changed: {top_exts}")

    parts.append(
        f"Total: {summary.total_files_changed} files, "
        f"+{summary.total_additions}/-{summary.total_deletions} lines"
    )

    return ". ".join(parts)


def _describe_file_change(fc: FileChange) -> str:
    """Generate a natural language description for a single file change."""
    filepath = fc.filepath
    basename = Path(filepath).name

    if fc.is_binary:
        return f"Binary file {fc.change_type}: {basename}"

    # Detect special files
    special = _detect_special_file(filepath, basename)
    if special:
        return f"{fc.change_type.capitalize()} {special}"

    # Build description from content
    desc_parts = [f"{fc.change_type.capitalize()} {basename}"]

    # Analyze added lines for intent signals
    signals = _extract_content_signals(fc.added_lines + fc.deleted_lines)
    if signals:
        desc_parts.append(f"({', '.join(signals)})")

    desc_parts.append(f"+{fc.additions}/-{fc.deletions}")

    return " ".join(desc_parts)


def _detect_special_file(filepath: str, basename: str) -> Optional[str]:
    """Detect well-known file types by name/path patterns."""
    lower = basename.lower()
    lower_path = filepath.lower()

    mappings = {
        "readme": "README documentation",
        "changelog": "changelog",
        "license": "license file",
        ".gitignore": "gitignore rules",
        "dockerfile": "Docker configuration",
        "docker-compose": "Docker Compose configuration",
        "makefile": "Makefile build configuration",
        "requirements.txt": "Python dependencies",
        "setup.py": "Python package setup",
        "setup.cfg": "Python package configuration",
        "pyproject.toml": "Python project configuration",
        "package.json": "Node.js package configuration",
        "tsconfig": "TypeScript configuration",
        ".env": "environment variables",
        "pytest.ini": "pytest configuration",
        "tox.ini": "tox test configuration",
    }

    for pattern, desc in mappings.items():
        if pattern in lower:
            return desc

    # CI/CD paths
    ci_patterns = [".github/workflows", ".gitlab-ci", "jenkinsfile", ".circleci"]
    for pat in ci_patterns:
        if pat in lower_path:
            return "CI/CD pipeline configuration"

    # Test files
    if lower.startswith("test_") or lower.endswith("_test.py") or "/tests/" in lower_path:
        return f"test file: {basename}"

    # Migration files
    if "migration" in lower_path or "alembic" in lower_path:
        return f"database migration: {basename}"

    return None


def _extract_content_signals(lines: List[str]) -> List[str]:
    """Extract semantic signals from code line content."""
    signals = []

    joined = " ".join(lines[:50]).lower()  # sample first 50 lines

    signal_patterns = [
        (r"\bclass\s+\w+", "class definition"),
        (r"\bdef\s+\w+", "function changes"),
        (r"\bimport\s+", "import changes"),
        (r"\btry\s*:", "error handling"),
        (r"\braise\s+", "exception raising"),
        (r"\blogging\b|\blogger\b", "logging"),
        (r"\breturn\b.*\bNone\b", "null return handling"),
        (r"\bassert\b", "assertions"),
        (r"#\s*TODO|#\s*FIXME|#\s*HACK", "code annotations"),
        (r"\bprint\s*\(", "print statements"),
        (r"if\s+__name__\s*==", "entry point"),
    ]

    for pattern, label in signal_patterns:
        if re.search(pattern, joined):
            signals.append(label)

    return signals[:4]  # limit signals


def _keyword_fallback_match(description: str) -> List[Tuple[CommitPattern, float]]:
    """
    Fallback matching using keyword overlap when model is unavailable.
    Returns patterns sorted by match score.
    """
    description_lower = description.lower()
    scored = []

    for pattern in COMMIT_PATTERNS:
        score = 0.0
        total_keywords = len(pattern.keywords)
        if total_keywords == 0:
            continue

        matched = sum(1 for kw in pattern.keywords if kw in description_lower)
        score = matched / total_keywords

        # Boost if description words appear in pattern description
        desc_words = set(description_lower.split())
        pattern_words = set(pattern.description.lower().split())
        overlap = len(desc_words & pattern_words)
        if overlap > 0:
            score += min(overlap / 10, 0.3)

        if score > 0.1:
            scored.append((pattern, min(score, 1.0)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def _semantic_match(description: str) -> List[Tuple[CommitPattern, float]]:
    """
    Match a change description against commit patterns using embeddings.
    Returns patterns sorted by cosine similarity score.
    """
    model = _load_model()
    pattern_embeds = _get_pattern_embeddings()

    if model is None or pattern_embeds is None:
        logger.info("Model unavailable, using keyword fallback.")
        return _keyword_fallback_match(description)

    # Embed the change description
    desc_embedding = model.encode([description], normalize_embeddings=True)

    # Cosine similarity (already normalized, so dot product = cosine sim)
    similarities = np.dot(pattern_embeds, desc_embedding.T).flatten()

    # Pair patterns with scores and sort
    scored = [
        (COMMIT_PATTERNS[i], float(similarities[i]))
        for i in range(len(COMMIT_PATTERNS))
        if similarities[i] >= config.similarity_threshold
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored


def _infer_scope(summary: DiffSummary) -> Optional[str]:
    """Infer a commit scope from the changed files."""
    if not config.include_scope:
        return None

    if summary.total_files_changed == 1:
        # Use the module/directory name
        filepath = summary.files[0].filepath
        parts = Path(filepath).parts
        if len(parts) > 1:
            return parts[-2]  # parent directory
        return Path(filepath).stem

    # Find common directory
    if summary.total_files_changed <= 5:
        dirs = [str(Path(f.filepath).parent) for f in summary.files]
        if len(set(dirs)) == 1 and dirs[0] != ".":
            return Path(dirs[0]).name

    # Use dominant file extension as scope hint
    ext_counts = Counter(f.file_extension for f in summary.files if f.file_extension)
    if ext_counts:
        top_ext = ext_counts.most_common(1)[0][0].lstrip(".")
        ext_scope_map = {
            "py": "python",
            "js": "js",
            "ts": "ts",
            "css": "styles",
            "html": "ui",
            "sql": "db",
            "yml": "config",
            "yaml": "config",
            "toml": "config",
            "json": "config",
            "md": "docs",
        }
        return ext_scope_map.get(top_ext)

    return None


def _generate_subject(
    pattern: CommitPattern, summary: DiffSummary, description: str
) -> str:
    """Generate a concise commit subject line."""
    # Pick the most meaningful changed file
    primary_file = summary.files[0] if summary.files else None
    primary_name = Path(primary_file.filepath).stem if primary_file else "module"

    # Build subject based on pattern type and changes
    if pattern.commit_type == "feat":
        if primary_file and primary_file.change_type == "added":
            subject = f"add {primary_name} module"
        else:
            subject = f"implement changes in {primary_name}"
    elif pattern.commit_type == "fix":
        subject = f"resolve issue in {primary_name}"
    elif pattern.commit_type == "docs":
        subject = f"update {primary_name} documentation"
    elif pattern.commit_type == "style":
        subject = f"apply formatting to {primary_name}"
    elif pattern.commit_type == "refactor":
        subject = f"restructure {primary_name} logic"
    elif pattern.commit_type == "perf":
        subject = f"optimize {primary_name} performance"
    elif pattern.commit_type == "test":
        subject = f"update tests for {primary_name}"
    elif pattern.commit_type == "build":
        subject = f"update build configuration"
    elif pattern.commit_type == "ci":
        subject = f"update CI/CD pipeline"
    elif pattern.commit_type == "chore":
        subject = f"update {primary_name} configuration"
    else:
        subject = f"update {primary_name}"

    # Enhance with content signals
    if primary_file:
        signals = _extract_content_signals(primary_file.added_lines)
        if signals and len(subject) < config.max_subject_length - 30:
            subject += f" with {signals[0]}"

    # Truncate if needed
    if len(subject) > config.max_subject_length:
        subject = subject[: config.max_subject_length - 3] + "..."

    return subject


def _generate_body(summary: DiffSummary, description: str) -> Optional[str]:
    """Generate an optional commit body with change details."""
    if not config.include_body:
        return None

    body_parts = []

    # List changed files
    if summary.total_files_changed <= 8:
        file_list = "\n".join(
            f"  - {f.filepath} (+{f.additions}/-{f.deletions})" for f in summary.files
        )
        body_parts.append(f"Changed files:\n{file_list}")
    else:
        body_parts.append(f"Modified {summary.total_files_changed} files")

    # Stats
    body_parts.append(
        f"Lines: +{summary.total_additions}/-{summary.total_deletions}"
    )

    body = "\n\n".join(body_parts)
    if len(body) > config.max_body_length:
        body = body[: config.max_body_length - 3] + "..."

    return body


def generate_commit_messages(summary: DiffSummary) -> List[CommitSuggestion]:
    """
    Main entry point: analyze a diff summary and generate commit message suggestions.

    Returns a list of CommitSuggestion objects sorted by confidence.
    """
    if summary.total_files_changed == 0:
        logger.warning("No file changes detected.")
        return []

    # Step 1: Describe changes in natural language
    description = _describe_changes(summary)
    logger.info(f"Change description: {description}")

    # Step 2: Semantic matching against patterns
    matches = _semantic_match(description)
    if not matches:
        logger.warning("No patterns matched. Generating generic commit message.")
        matches = [(COMMIT_PATTERNS[0], 0.2)]  # default to 'feat'

    # Step 3: Generate suggestions from top matches
    suggestions = []
    scope = _infer_scope(summary)

    for pattern, score in matches[: config.max_suggestions]:
        subject = _generate_subject(pattern, summary, description)
        body = _generate_body(summary, description)

        suggestion = CommitSuggestion(
            commit_type=pattern.commit_type,
            scope=scope,
            subject=subject,
            body=body,
            confidence=round(score * 100, 1),
            matched_pattern=pattern.name,
        )
        suggestions.append(suggestion)

    return suggestions
