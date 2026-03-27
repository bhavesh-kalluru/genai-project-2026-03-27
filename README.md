# Semantic Commit Message Generator

An AI-powered CLI tool that analyzes git diffs and generates meaningful **Conventional Commit** messages using sentence-transformer embeddings and semantic pattern matching.

100% local — no API keys, no cloud services, CPU-only.

---

## How It Works

1. **Parses** your git diff (staged, unstaged, or from a `.diff` file) into structured change objects
2. **Describes** the changes in natural language (file types, code signals, content patterns)
3. **Embeds** the description using `all-MiniLM-L6-v2` (384-dim sentence embeddings)
4. **Matches** against an 18-pattern knowledge base of conventional commit types via cosine similarity
5. **Generates** ranked commit message suggestions with type, scope, subject, body, and confidence scores

Falls back to keyword-based matching automatically if the model fails to download.

---

## Features

- **Conventional Commits** format (`feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`)
- **18 semantic patterns** covering features, bug fixes, docs, style, refactoring, performance, tests, dependencies, CI/CD, config, security, DB migrations, API changes, UI, error handling, logging, and more
- **Auto-scope detection** from directory structure and file types
- **Confidence scoring** with color-coded terminal output
- **Multiple output formats**: terminal (colored), JSON (for CI/CD), plain text
- **Zero config** — works out of the box with sensible defaults
- **Graceful fallback** to keyword matching if model download fails
- **Lightweight** — runs on CPU, ~2 GB RAM, no GPU required

---

## Installation

```bash
# Clone the repo
git clone https://github.com/bhavesh-kalluru/genai-project-2026-03-27.git
cd genai-project-2026-03-27

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

The embedding model (`all-MiniLM-L6-v2`, ~80MB) downloads automatically on first run.

---

## Usage

### Analyze Staged Changes
```bash
# Stage your files first
git add .

# Generate commit messages
python main.py
```

### Analyze a Diff File
```bash
python main.py --file data/sample.diff
```

### Run Demo (No Git Repo Needed)
```bash
python main.py --demo
```

### Output as JSON (for CI/CD Pipelines)
```bash
python main.py --demo --format json
```

### Include Unstaged Changes
```bash
python main.py --unstaged
```

### Customize Output
```bash
# More suggestions, no body, no scope
python main.py --demo --suggestions 5 --no-body --no-scope

# Lower similarity threshold for more matches
python main.py --demo --threshold 0.2

# Verbose logging
python main.py --demo -v
```

---

## Example Output

Running `python main.py --demo` produces:

```
══════════════════════════════════════════════════════════════
  COMMIT MESSAGE SUGGESTIONS
══════════════════════════════════════════════════════════════

  #1  [32.3%]  [████░░░░░░░░░░░]  pattern: logging
  ────────────────────────────────────────────────────────
  feat(python): add login module with class definition

  Changed files:
    - auth/login.py (+41/-0)
    - tests/test_auth.py (+22/-0)
    - requirements.txt (+2/-0)

  Lines: +65/-0

  #2  [25.4%]  [███░░░░░░░░░░░░]  pattern: config_change
  ────────────────────────────────────────────────────────
  chore(python): update login configuration with class definition

  ...

══════════════════════════════════════════════════════════════

  Tip: Copy the suggestion and run: git commit -m "<message>"
```

### JSON Output
```json
[
  {
    "rank": 1,
    "type": "feat",
    "scope": "python",
    "subject": "add login module with class definition",
    "body": "Changed files:\n  - auth/login.py (+41/-0)\n  ...",
    "full_message": "feat(python): add login module with class definition\n\n...",
    "confidence": 32.3,
    "matched_pattern": "logging"
  }
]
```

---

## Project Structure

```
genai-project-2026-03-27/
├── main.py            # CLI entry point (argparse)
├── engine.py          # Semantic matching engine
├── diff_parser.py     # Git diff parser
├── templates.py       # 18-pattern commit knowledge base
├── config.py          # Centralized configuration
├── utils.py           # Terminal formatting & output
├── data/
│   └── sample.diff    # Sample diff for testing
├── requirements.txt   # Minimal dependencies
├── .gitignore
└── README.md
```

---

## Configuration

All settings are in `config.py`. Key parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `embedding_model` | `all-MiniLM-L6-v2` | Sentence-transformer model |
| `similarity_threshold` | `0.25` | Minimum cosine similarity to match |
| `max_suggestions` | `3` | Number of suggestions to generate |
| `max_diff_lines` | `500` | Truncate diffs beyond this |
| `include_body` | `True` | Include detailed body in messages |
| `include_scope` | `True` | Auto-detect and add scope |

Override via CLI flags or environment variables:
```bash
LOG_LEVEL=DEBUG python main.py --demo --threshold 0.25 --suggestions 5
```

---

## Tech Stack

- **[sentence-transformers](https://www.sbert.net/)** — `all-MiniLM-L6-v2` for semantic embeddings
- **NumPy** — cosine similarity computation
- **Python stdlib** — `argparse`, `subprocess`, `re`, `ast`, `logging`, `json`

---

## Requirements

- Python 3.8+
- ~2 GB RAM (model + embeddings)
- No GPU needed
- No API keys needed

---

## Tags

`generative-ai` `nlp` `git` `commit-messages` `conventional-commits` `sentence-transformers` `embeddings` `semantic-search` `developer-tools` `python` `cli` `devops` `productivity`

---

## License

MIT
