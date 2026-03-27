"""
Commit message templates and pattern knowledge base.

Each template describes a common commit scenario with an associated
semantic description (used for embedding similarity), example messages,
and the conventional commit type.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CommitPattern:
    """A known commit pattern with its semantic signature."""

    name: str
    commit_type: str
    description: str  # semantic description for embedding matching
    keywords: List[str] = field(default_factory=list)
    example_messages: List[str] = field(default_factory=list)


# Knowledge base of commit patterns
COMMIT_PATTERNS: List[CommitPattern] = [
    CommitPattern(
        name="new_feature",
        commit_type="feat",
        description="Adding new feature, implementing new functionality, creating new capability, introducing new behavior",
        keywords=["new", "add", "create", "implement", "introduce", "feature"],
        example_messages=[
            "feat: add user authentication module",
            "feat(auth): implement JWT token validation",
            "feat: introduce dark mode toggle",
        ],
    ),
    CommitPattern(
        name="bug_fix",
        commit_type="fix",
        description="Fixing a bug, resolving an error, correcting broken behavior, patching a defect, handling edge case",
        keywords=["fix", "bug", "error", "patch", "resolve", "correct", "handle"],
        example_messages=[
            "fix: resolve null pointer in user service",
            "fix(api): handle timeout on slow connections",
            "fix: correct off-by-one error in pagination",
        ],
    ),
    CommitPattern(
        name="documentation",
        commit_type="docs",
        description="Updating documentation, writing README, adding comments, updating docstrings, API documentation",
        keywords=["doc", "readme", "comment", "docstring", "documentation", "guide"],
        example_messages=[
            "docs: update API endpoint documentation",
            "docs: add setup instructions to README",
            "docs(api): document rate limiting behavior",
        ],
    ),
    CommitPattern(
        name="code_style",
        commit_type="style",
        description="Formatting code, fixing whitespace, adjusting indentation, code style, linting fixes, no logic change",
        keywords=["format", "style", "lint", "whitespace", "indent", "prettier"],
        example_messages=[
            "style: apply black formatter to all modules",
            "style: fix indentation in config parser",
            "style: remove trailing whitespace",
        ],
    ),
    CommitPattern(
        name="refactoring",
        commit_type="refactor",
        description="Restructuring code, renaming variables, extracting functions, simplifying logic, improving code organization without changing behavior",
        keywords=["refactor", "restructure", "rename", "extract", "simplify", "reorganize", "clean"],
        example_messages=[
            "refactor: extract validation logic into helper",
            "refactor(auth): simplify token refresh flow",
            "refactor: rename user_mgr to user_service",
        ],
    ),
    CommitPattern(
        name="performance",
        commit_type="perf",
        description="Improving performance, optimizing speed, reducing memory usage, caching, making code faster",
        keywords=["perf", "optimize", "speed", "cache", "fast", "memory", "efficient"],
        example_messages=[
            "perf: add caching layer for database queries",
            "perf: optimize image processing pipeline",
            "perf(search): use inverted index for faster lookup",
        ],
    ),
    CommitPattern(
        name="testing",
        commit_type="test",
        description="Adding tests, updating test cases, fixing tests, improving test coverage, unit tests, integration tests",
        keywords=["test", "spec", "coverage", "assert", "mock", "fixture", "pytest"],
        example_messages=[
            "test: add unit tests for payment service",
            "test(auth): update login flow test fixtures",
            "test: increase coverage for utils module",
        ],
    ),
    CommitPattern(
        name="build_deps",
        commit_type="build",
        description="Updating dependencies, changing build configuration, modifying package requirements, version bumps",
        keywords=["build", "dependency", "requirements", "package", "version", "upgrade", "pip", "npm"],
        example_messages=[
            "build: upgrade transformers to 4.38.0",
            "build: add sentence-transformers to requirements",
            "build(deps): bump numpy from 1.24 to 1.26",
        ],
    ),
    CommitPattern(
        name="ci_cd",
        commit_type="ci",
        description="Modifying CI/CD pipeline, updating GitHub Actions, changing deployment configuration, workflow automation",
        keywords=["ci", "cd", "pipeline", "workflow", "deploy", "github actions", "jenkins"],
        example_messages=[
            "ci: add Python 3.12 to test matrix",
            "ci: fix deployment workflow permissions",
            "ci(docker): optimize multi-stage build",
        ],
    ),
    CommitPattern(
        name="chore",
        commit_type="chore",
        description="Maintenance tasks, updating gitignore, cleaning up files, tooling configuration, miscellaneous housekeeping",
        keywords=["chore", "cleanup", "gitignore", "config", "maintenance", "housekeeping"],
        example_messages=[
            "chore: update .gitignore for Python artifacts",
            "chore: remove deprecated utility scripts",
            "chore(config): standardize env variable names",
        ],
    ),
    CommitPattern(
        name="revert",
        commit_type="revert",
        description="Reverting a previous commit, undoing changes, rolling back modifications",
        keywords=["revert", "undo", "rollback", "back"],
        example_messages=[
            "revert: undo migration changes from abc1234",
            'revert: revert "feat: add experimental cache"',
        ],
    ),
    CommitPattern(
        name="security_fix",
        commit_type="fix",
        description="Fixing security vulnerability, patching security issue, updating insecure dependency, sanitizing input",
        keywords=["security", "vulnerability", "cve", "sanitize", "xss", "injection", "auth"],
        example_messages=[
            "fix(security): sanitize user input in search",
            "fix: patch CVE-2024-1234 in auth module",
            "fix(deps): update lodash to fix prototype pollution",
        ],
    ),
    CommitPattern(
        name="database_migration",
        commit_type="feat",
        description="Database migration, schema change, adding table columns, altering database structure, model changes",
        keywords=["migration", "schema", "database", "table", "column", "model", "migrate"],
        example_messages=[
            "feat(db): add email_verified column to users",
            "feat: create migration for order status enum",
            "feat(schema): normalize address table structure",
        ],
    ),
    CommitPattern(
        name="api_change",
        commit_type="feat",
        description="Adding API endpoint, modifying API response, changing API route, REST API modification, request handling",
        keywords=["api", "endpoint", "route", "request", "response", "rest", "handler"],
        example_messages=[
            "feat(api): add /users/search endpoint",
            "feat: implement pagination for list endpoints",
            "feat(api): add rate limiting middleware",
        ],
    ),
    CommitPattern(
        name="ui_change",
        commit_type="feat",
        description="User interface change, updating frontend, modifying HTML/CSS, component update, layout change, UI improvement",
        keywords=["ui", "frontend", "component", "layout", "css", "html", "template", "button", "form"],
        example_messages=[
            "feat(ui): redesign user profile page",
            "feat: add responsive navigation menu",
            "feat(ui): implement loading skeleton states",
        ],
    ),
    CommitPattern(
        name="config_change",
        commit_type="chore",
        description="Configuration file change, environment variable update, settings modification, config parameter adjustment",
        keywords=["config", "env", "settings", "environment", "parameter", "yaml", "toml", "json config"],
        example_messages=[
            "chore(config): add production database URL",
            "chore: update logging configuration",
            "chore(env): add SMTP settings for email service",
        ],
    ),
    CommitPattern(
        name="error_handling",
        commit_type="fix",
        description="Improving error handling, adding try-except blocks, better exception messages, error recovery, graceful degradation",
        keywords=["error", "exception", "try", "catch", "handling", "graceful", "fallback"],
        example_messages=[
            "fix: add graceful handling for network timeouts",
            "fix(parser): improve error messages for malformed input",
            "fix: add retry logic for transient API failures",
        ],
    ),
    CommitPattern(
        name="logging",
        commit_type="feat",
        description="Adding logging, improving log output, structured logging, debug logs, monitoring instrumentation",
        keywords=["log", "logging", "debug", "trace", "monitor", "instrument"],
        example_messages=[
            "feat: add structured JSON logging",
            "feat(monitor): instrument request latency metrics",
            "feat: add debug logging for auth flow",
        ],
    ),
]
