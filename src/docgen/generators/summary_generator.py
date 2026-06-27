"""Project summary generator."""

from docgen.generators.common import bullet_list, heading, project_overview
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis


class SummaryGenerator:
    """Generate a concise project summary."""

    filename = "PROJECT_SUMMARY.md"
    title = "Project Summary"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        snippets = rag.search("project summary overview", limit=2)
        return "\n\n".join(
            [
                heading("Project Summary"),
                project_overview(analysis),
                heading("Key Signals", 2),
                bullet_list(
                    [
                        f"Package roots: {', '.join(analysis.structure.package_roots) or 'none'}",
                        f"Python modules: {len(analysis.python_modules)}",
                        f"Runtime dependencies: {len(analysis.dependencies.runtime)}",
                        f"Tests: {'detected' if analysis.structure.has_tests else 'not detected'}",
                        "Documentation: "
                        f"{'detected' if analysis.structure.has_docs else 'not detected'}",
                    ]
                ),
                heading("Retrieved Context", 2),
                bullet_list(snippets, empty="No repository context retrieved."),
            ]
        )
