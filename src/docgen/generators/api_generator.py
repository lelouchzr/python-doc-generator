"""API reference draft generator."""

from collections import defaultdict

from docgen.generators.common import bullet_list, heading
from docgen.integrations.rag import RepositoryRAG
from docgen.models import PythonSymbol, RepositoryAnalysis


class ApiGenerator:
    """Generate a Markdown API reference draft from AST symbols."""

    filename = "API.md"
    title = "API Reference Draft"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        del rag
        grouped: dict[str, list[PythonSymbol]] = defaultdict(list)
        for module in analysis.python_modules:
            grouped[module.module].extend(module.symbols)

        sections = [heading("API Reference Draft")]
        if not grouped:
            sections.append("No public Python API symbols were detected.")
            return "\n\n".join(sections)

        for module_name, symbols in sorted(grouped.items()):
            sections.append(heading(module_name, 2))
            if not symbols:
                sections.append("- No public classes or functions detected.")
                continue
            sections.append(bullet_list(_symbol_line(symbol) for symbol in symbols))
        return "\n\n".join(sections)


def _symbol_line(symbol: PythonSymbol) -> str:
    doc = symbol.docstring.splitlines()[0] if symbol.docstring else "No docstring."
    signature = symbol.signature or symbol.name
    return f"`{symbol.name}` - `{signature}` ({symbol.path}:{symbol.lineno}) - {doc}"
