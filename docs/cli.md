# CLI

## Generate

```bash
docgen ./repo
docgen ./repo --output ./generated-docs
docgen ./repo --sections readme,architecture,api
docgen ./repo --dry-run
docgen ./repo --config docgen.toml
docgen ./repo --exclude .venv,dist,*.sqlite
```

Supported sections:

- `readme`
- `architecture`
- `api`
- `diagrams`
- `questions`
- `roadmap`
- `summary`

## Ask

```bash
docgen ask ./repo "How does configuration work?"
```

## Inspect

```bash
docgen inspect ./repo
docgen inspect ./repo --sections readme,api
docgen inspect ./repo --exclude .venv,dist,*.sqlite
```

`inspect` prints repository analysis without generating documentation. It reports scanned files,
Python modules, public symbols, package roots, dependencies, CLI scripts, enabled sections and
generated path previews.

## Diagram

```bash
docgen diagram ./repo
```

## Hosted Providers

```bash
docgen ./repo --llm openai --model gpt-5.5
docgen ./repo --llm anthropic --model claude-opus-4-8
docgen ./repo --llm gemini --model gemini-3.5-flash
```

The default provider is `local`, which is deterministic and does not require an API key.
