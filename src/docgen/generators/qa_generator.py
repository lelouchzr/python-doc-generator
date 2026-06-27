"""Repository Q&A generator."""

from docgen.generators.common import heading
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis

QUESTIONS = (
    "What is the project purpose?",
    "Where is the main Python package?",
    "How is the project tested?",
    "What are the primary dependencies?",
    "Where should a new contributor start?",
)


class QaGenerator:
    """Generate a small Q&A knowledge base from analysis and RAG retrieval."""

    filename = "QUESTIONS.md"
    title = "Q&A Knowledge Base"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        sections = [heading("Q&A Knowledge Base")]
        for question in QUESTIONS:
            sections.append(heading(question, 2))
            sections.append(_answer(question, analysis, rag))
        return "\n\n".join(sections)


def _answer(question: str, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
    snippets = rag.search(question, limit=2)
    if question == "Where is the main Python package?":
        roots = analysis.structure.package_roots
        return "Detected package roots: " + (", ".join(f"`{root}`" for root in roots) or "none")
    if question == "How is the project tested?":
        return "Tests were detected." if analysis.structure.has_tests else "No tests were detected."
    if question == "What are the primary dependencies?":
        dependencies = analysis.dependencies.runtime[:8]
        return (
            ", ".join(f"`{dependency}`" for dependency in dependencies)
            or "No dependencies found."
        )
    if snippets:
        return f"Relevant repository context: {snippets[0]}"
    return "No direct answer was found in the indexed repository content."
