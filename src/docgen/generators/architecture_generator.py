"""Architecture overview generator."""

from docgen.generators.common import bullet_list, heading, module_lines, project_overview
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis


class ArchitectureGenerator:
    """Generate a concise architecture overview."""

    filename = "ARCHITECTURE.md"
    title = "Architecture Overview"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        structure = analysis.structure
        modules = module_lines(analysis.python_modules)
        source_snippets = rag.search("architecture modules data flow responsibilities", limit=3)
        return "\n\n".join(
            [
                heading("Architecture Overview"),
                project_overview(analysis),
                heading("Repository Shape", 2),
                bullet_list(
                    [
                        f"Project root: `{structure.root}`",
                        f"Top-level entries: {', '.join(structure.top_level_entries[:12])}",
                        f"Tests detected: {_yes_no(structure.has_tests)}",
                        f"Docs detected: {_yes_no(structure.has_docs)}",
                        f"CI detected: {_yes_no(structure.has_ci)}",
                    ]
                ),
                heading("Core Modules", 2),
                bullet_list(modules),
                heading("Dependency Boundaries", 2),
                bullet_list(
                    [
                        "Repository scanning and static analysis stay local and deterministic.",
                        "Semantic indexing and retrieval are delegated to `python-rag-framework`.",
                        "Documentation prompts run through `python-agent-runtime`.",
                        "Markdown writing is isolated behind the output writer.",
                    ]
                ),
                heading("Relevant Source Context", 2),
                bullet_list(source_snippets, empty="No retrieval context available."),
            ]
        )


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"

