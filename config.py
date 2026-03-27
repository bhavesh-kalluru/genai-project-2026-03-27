"""
Centralized configuration for Semantic Commit Message Generator.
All tunable parameters live here for easy adjustment.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Application-wide configuration."""

    # --- Model Settings ---
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.25

    # --- Commit Convention ---
    # Conventional Commits types with descriptions
    commit_types: dict = field(default_factory=lambda: {
        "feat": "A new feature or functionality",
        "fix": "A bug fix",
        "docs": "Documentation only changes",
        "style": "Code style changes (formatting, semicolons, whitespace)",
        "refactor": "Code restructuring without changing behavior",
        "perf": "Performance improvements",
        "test": "Adding or updating tests",
        "build": "Build system or dependency changes",
        "ci": "CI/CD configuration changes",
        "chore": "Maintenance tasks, tooling, or config",
        "revert": "Reverting a previous commit",
    })

    # --- Diff Analysis ---
    max_diff_lines: int = 500
    max_file_context: int = 10  # max files to analyze in detail
    context_lines: int = 3  # lines of context around changes

    # --- Output ---
    max_suggestions: int = 3
    include_body: bool = True
    include_scope: bool = True
    max_subject_length: int = 72
    max_body_length: int = 500

    # --- Logging ---
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str = "commit_gen.log"

    # --- Fallback ---
    use_fallback_on_model_failure: bool = True


# Singleton config instance
config = Config()
