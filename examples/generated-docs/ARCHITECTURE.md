# Architecture Overview

The sample project is intentionally small:

- `sample_project/__init__.py` exposes the public package API.
- `sample_project/service.py` contains the greeting service.
- `pyproject.toml` declares package metadata.
- `README.md` gives a short project description.

The documentation generator indexes these files with `python-rag-framework`, extracts symbols with
the AST analyzer, and sends generation prompts through `python-agent-runtime`.

