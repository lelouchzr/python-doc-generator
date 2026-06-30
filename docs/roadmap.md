# Roadmap

This roadmap keeps the project intentionally small. Each item should be useful on its own, easy to
test, and avoid turning Python Doc Generator into a large documentation platform.

## Completed

### `docgen inspect`

Added a command that prints deterministic repository analysis without generating documentation:

```bash
docgen inspect ./repo
```

It should report:

- scanned files
- detected Python modules
- public classes and functions
- package roots
- runtime and development dependencies
- CLI scripts from `pyproject.toml`
- enabled documentation sections

## Next

### `--exclude-tests`

Add a first-class option to exclude tests from API documentation and repository summaries:

```bash
docgen ./repo --exclude-tests
```

This keeps generated API docs focused on public project code instead of test helpers.

### `docgen init`

Add a command that creates a starter `docgen.toml` in the current repository:

```bash
docgen init
```

It should write conservative defaults and refuse to overwrite an existing config unless the user
passes `--force`.

## Small Follow-Ups

### JSON Output

Add a machine-readable output mode:

```bash
docgen inspect ./repo --format json
```

This should expose the existing typed analysis models without adding a new analysis engine.

### Verbose Mode

Add progress output for local debugging:

```bash
docgen ./repo --verbose
```

Expected stages:

- scan
- analyze
- index
- generate
- write

### Repository Quality Report

Add `REPORT.md` as an optional generated section with simple repository health signals:

- tests detected
- docs detected
- CI detected
- package metadata detected
- dependency summary
- obvious documentation gaps

### Better API Reference

Improve `API.md` formatting:

- group classes and functions separately
- nest methods under their class
- omit tests by default when `--exclude-tests` is enabled
- show module docstrings before symbols

### Template Preferences

Support small tone and audience preferences in `docgen.toml`:

```toml
[docgen]
tone = "concise"
audience = "developers"
```

These options should influence prompts and deterministic drafts without introducing a template
engine.

### Documentation Diff

Add a lightweight comparison command:

```bash
docgen diff ./repo
```

It should identify missing generated files and obvious stale docs. Keep this text-based and simple.
