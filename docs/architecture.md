# Architecture

The project keeps a small pipeline:

1. `RepositoryScanner` reads useful text files from a local repository.
2. `PythonAnalyzer`, `StructureAnalyzer` and `DependencyAnalyzer` produce typed facts.
3. `RepositoryRAG` delegates indexing and retrieval to `python-rag-framework`.
4. `DocumentationAgent` delegates prompt execution to `python-agent-runtime`.
5. Markdown generators build focused documentation files.
6. `OutputWriter` writes generated files to disk.

The default generation path is deterministic so tests and examples run without paid LLM APIs.

Hosted OpenAI, Anthropic and Gemini adapters are optional. They receive a deterministic draft as
grounding, then rewrite it through the selected provider.
