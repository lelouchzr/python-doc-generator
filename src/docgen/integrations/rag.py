"""Integration with python-rag-framework."""

from rag import RAG

from docgen.config import DocgenConfig
from docgen.models import RepositoryFile


class RepositoryRAG:
    """Indexes repository files with the reusable RAG framework."""

    def __init__(self, config: DocgenConfig | None = None) -> None:
        self._config = config or DocgenConfig()
        self._rag = RAG()

    @property
    def backend(self) -> RAG:
        """Expose the underlying RAG object for the agent runtime integration."""
        return self._rag

    def index(self, files: tuple[RepositoryFile, ...]) -> None:
        for file in files:
            self._rag.add_text(
                file.content,
                source=file.relative_path,
                metadata={
                    "source": file.relative_path,
                    "suffix": file.suffix,
                    "path": file.relative_path,
                },
            )

    def search(self, query: str, *, limit: int | None = None) -> list[str]:
        results = self._rag.retrieve(query, limit=limit or self._config.rag_results)
        snippets: list[str] = []
        for result in results:
            source = result.chunk.metadata.get("source", "unknown")
            snippets.append(f"{source}: {result.chunk.text.strip()}")
        return snippets

