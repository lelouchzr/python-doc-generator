# Python Doc Generator

Python Doc Generator is a small CLI that analyzes a local Python repository and writes useful
Markdown documentation drafts.

It is intentionally portfolio-sized: it does repository scanning, light static analysis, RAG-backed
repository Q&A and agent-driven documentation generation without becoming a replacement for Sphinx
or MkDocs.

## Why This Exists

This project is the first real consumer of two reusable portfolio libraries:

- `python-rag-framework` indexes repository files and retrieves relevant source context.
- `python-agent-runtime` executes documentation prompts with history, tool and RAG plumbing.

The project-specific code focuses on documentation generation only.

## Install

```bash
uv sync
```

The package declares the reusable libraries as real dependencies:

```bash
uv add "python-rag-framework @ git+https://github.com/lelouchzr/python-rag-framework.git@4b4368a11c8d6ccf05c6ebeba3242f22199868d0"
uv add "python-agent-runtime @ git+https://github.com/lelouchzr/python-agent-runtime.git@cdbf8932c7867af1af0dfbde873430008db6cf5a"
```

## Usage

Generate all documentation:

```bash
docgen ./my-project
```

Choose an output folder:

```bash
docgen ./my-project --output ./generated-docs
```

Generate selected sections:

```bash
docgen ./my-project --sections readme,architecture,api
```

Preview generated paths without writing files:

```bash
docgen ./my-project --dry-run
```

Use a config file and exclude custom paths:

```bash
docgen ./my-project --config docgen.toml --exclude .venv,dist,*.sqlite
```

Ask a repository question:

```bash
docgen ask ./my-project "How does authentication work?"
```

Print Mermaid diagrams:

```bash
docgen diagram ./my-project
```

## Configuration

Create `docgen.toml`:

```toml
[docgen]
output_dir = "generated-docs"
sections = ["readme", "architecture", "api"]
exclude = [".venv", "dist", "*.sqlite"]
rag_results = 5
llm = "local"
```

CLI flags override config values.

## Optional Hosted LLMs

Local deterministic generation is the default and needs no API key.

For hosted generation, install the matching extra and pass `--llm`:

```bash
uv sync --extra openai
docgen ./my-project --llm openai --model gpt-5.5

uv sync --extra anthropic
docgen ./my-project --llm anthropic --model claude-opus-4-8

uv sync --extra gemini
docgen ./my-project --llm gemini --model gemini-3.5-flash
```

Expected environment variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

## Generated Files

- `README.generated.md`
- `ARCHITECTURE.md`
- `API.md`
- `DIAGRAMS.md`
- `QUESTIONS.md`
- `ROADMAP.md`
- `PROJECT_SUMMARY.md`

## Development

```bash
uv run ruff check .
uv run mypy
uv run pytest
uv run python -m build
```

Tests use deterministic local callables, so no API key is required.

See `examples/generated-docs/` for a checked-in output snapshot.

## Documentation Site

Build the MkDocs site locally:

```bash
uv run mkdocs build --strict
```

GitHub Pages is deployed by `.github/workflows/pages.yml` on pushes to `main`.

## Private Dependency Repositories

If `python-rag-framework` or `python-agent-runtime` are private, create a fine-grained GitHub token
with read-only `Contents` access to both repositories, then add it to this repository as an Actions
secret:

```text
DEPENDENCY_REPO_TOKEN
```

The CI workflow uses this secret to install the Git dependencies during `uv sync --all-extras`.
