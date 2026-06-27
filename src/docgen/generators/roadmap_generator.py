"""Roadmap suggestion generator."""

from docgen.generators.common import bullet_list, heading
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis


class RoadmapGenerator:
    """Generate small, practical roadmap suggestions."""

    filename = "ROADMAP.md"
    title = "Roadmap Suggestions"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        del rag
        suggestions = [
            "Keep generated documents reviewed by a human before publishing.",
            "Add examples that exercise the most common CLI workflows.",
            "Add release notes once the CLI behavior stabilizes.",
        ]
        if not analysis.structure.has_tests:
            suggestions.insert(0, "Add pytest coverage for the public CLI and generators.")
        if not analysis.structure.has_docs:
            suggestions.insert(0, "Add user-facing documentation under `docs/`.")
        if not analysis.structure.has_ci:
            suggestions.insert(
                0,
                "Add GitHub Actions for linting, typing, tests and package build.",
            )
        if not analysis.dependencies.runtime:
            suggestions.append("Declare runtime dependencies in `pyproject.toml`.")

        return "\n\n".join(
            [
                heading("Roadmap Suggestions"),
                "Prioritized suggestions based on the scanned repository:",
                bullet_list(suggestions),
            ]
        )
