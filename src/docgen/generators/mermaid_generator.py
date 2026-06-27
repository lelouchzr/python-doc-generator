"""Mermaid diagram generator."""

from docgen.generators.common import heading
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis


class MermaidGenerator:
    """Generate Mermaid diagrams for the repository."""

    filename = "DIAGRAMS.md"
    title = "Mermaid Diagrams"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        del rag
        return "\n\n".join(
            [
                heading("Mermaid Diagrams"),
                heading("Documentation Pipeline", 2),
                _pipeline_diagram(),
                heading("Module Map", 2),
                _module_diagram(analysis),
            ]
        )


def _pipeline_diagram() -> str:
    return """```mermaid
flowchart TD
    cli["Typer CLI"] --> scanner["Repository scanner"]
    scanner --> analyzers["Static analyzers"]
    scanner --> rag["python-rag-framework index"]
    analyzers --> agent["python-agent-runtime"]
    rag --> agent
    agent --> markdown["Markdown generators"]
    markdown --> output["generated-docs"]
```"""


def _module_diagram(analysis: RepositoryAnalysis) -> str:
    modules = analysis.python_modules[:12]
    if not modules:
        return """```mermaid
flowchart TD
    repo["Repository"] --> docs["Generated docs"]
```"""

    lines = ["```mermaid", "flowchart LR", '    repo["Repository"]']
    for index, module in enumerate(modules, start=1):
        node = f"m{index}"
        label = module.module.replace('"', "'")
        lines.append(f'    repo --> {node}["{label}"]')
    lines.append("```")
    return "\n".join(lines)

