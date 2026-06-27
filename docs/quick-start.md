# Quick Start

Install dependencies:

```bash
uv sync
```

Generate documentation:

```bash
uv run docgen ./examples/sample_project --output ./generated-docs
```

Preview without writing:

```bash
uv run docgen ./examples/sample_project --dry-run
```

Ask a question:

```bash
uv run docgen ask ./examples/sample_project "What does the package expose?"
```

Print diagrams:

```bash
uv run docgen diagram ./examples/sample_project
```

Use a hosted provider:

```bash
uv sync --extra openai
uv run docgen ./examples/sample_project --llm openai --model gpt-5.5
```

Build the documentation site:

```bash
uv run mkdocs build --strict
```
