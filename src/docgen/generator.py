"""High-level documentation generation workflow."""

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol

from agent.messages import Message

from docgen.analyzers import DependencyAnalyzer, PythonAnalyzer, StructureAnalyzer
from docgen.config import DocgenConfig, Section
from docgen.exceptions import UnknownSectionError
from docgen.generators import (
    ApiGenerator,
    ArchitectureGenerator,
    MermaidGenerator,
    QaGenerator,
    ReadmeGenerator,
    RoadmapGenerator,
    SummaryGenerator,
)
from docgen.integrations import DocumentationAgent, RepositoryRAG
from docgen.models import GeneratedDocument, RepositoryAnalysis
from docgen.output import OutputWriter
from docgen.prompts import section_prompt
from docgen.repository import Repository
from docgen.scanner import RepositoryScanner


class MarkdownGenerator(Protocol):
    filename: str
    title: str

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        """Render a Markdown document."""


GENERATOR_BY_SECTION: dict[Section, MarkdownGenerator] = {
    Section.README: ReadmeGenerator(),
    Section.ARCHITECTURE: ArchitectureGenerator(),
    Section.API: ApiGenerator(),
    Section.DIAGRAMS: MermaidGenerator(),
    Section.QUESTIONS: QaGenerator(),
    Section.ROADMAP: RoadmapGenerator(),
    Section.SUMMARY: SummaryGenerator(),
}


class DocumentationGenerator:
    """Coordinates scanning, analysis, RAG indexing, agent execution and writing."""

    def __init__(self, config: DocgenConfig | None = None) -> None:
        self._config = config or DocgenConfig()
        self._scanner = RepositoryScanner(self._config)
        self._python_analyzer = PythonAnalyzer(self._config)
        self._structure_analyzer = StructureAnalyzer()
        self._dependency_analyzer = DependencyAnalyzer()
        self._agent = DocumentationAgent(self._config)
        self._writer = OutputWriter()

    def analyze(self, repository_path: str | Path) -> tuple[RepositoryAnalysis, RepositoryRAG]:
        repository = Repository(repository_path)
        files = self._scanner.scan(repository)
        modules = self._python_analyzer.analyze(files)
        structure = self._structure_analyzer.analyze(repository, files)
        dependencies = self._dependency_analyzer.analyze(files, modules)
        analysis = RepositoryAnalysis(
            structure=structure,
            python_modules=modules,
            dependencies=dependencies,
        )
        rag = RepositoryRAG(self._config)
        rag.index(files)
        return analysis, rag

    def generate(self, repository_path: str | Path) -> tuple[GeneratedDocument, ...]:
        analysis, rag = self.analyze(repository_path)
        documents: list[GeneratedDocument] = []
        for section in self._config.sections:
            generator = _generator_for_section(section)
            content = self._agent.generate(
                prompt=section_prompt(section.value, analysis.structure.project_name),
                renderer=_renderer(generator, analysis, rag),
                rag_backend=rag.backend,
                rag_results=self._config.rag_results,
            )
            documents.append(
                GeneratedDocument(
                    filename=generator.filename,
                    title=generator.title,
                    content=content,
                )
            )
        return tuple(documents)

    def write(self, repository_path: str | Path) -> tuple[Path, ...]:
        documents = self.generate(repository_path)
        return self._writer.write(self._config.output_dir, documents)

    def preview_paths(self) -> tuple[Path, ...]:
        """Return the files that would be generated without writing them."""
        return tuple(
            self._config.output_dir / _generator_for_section(section).filename
            for section in self._config.sections
        )

    def ask(self, repository_path: str | Path, question: str) -> str:
        analysis, rag = self.analyze(repository_path)

        def render(messages: Sequence[Message]) -> str:
            del messages
            snippets = rag.search(question, limit=self._config.rag_results)
            package_roots = ", ".join(analysis.structure.package_roots) or "none"
            context = "\n".join(f"- {snippet}" for snippet in snippets) or "- No context found."
            return "\n\n".join(
                [
                    f"# Answer: {question}",
                    f"Project: `{analysis.structure.project_name}`",
                    f"Package roots: {package_roots}",
                    "Relevant context:",
                    context,
                ]
            )

        return self._agent.generate(
            prompt=question,
            renderer=render,
            rag_backend=rag.backend,
            rag_results=self._config.rag_results,
        )

    def diagram(self, repository_path: str | Path) -> str:
        analysis, rag = self.analyze(repository_path)
        return MermaidGenerator().render(analysis, rag)


def _generator_for_section(section: Section) -> MarkdownGenerator:
    try:
        return GENERATOR_BY_SECTION[section]
    except KeyError as exc:
        msg = f"Unsupported section: {section}"
        raise UnknownSectionError(msg) from exc


def _renderer(
    generator: MarkdownGenerator,
    analysis: RepositoryAnalysis,
    rag: RepositoryRAG,
) -> Callable[[Sequence[Message]], str]:
    def render(messages: Sequence[Message]) -> str:
        del messages
        return generator.render(analysis, rag)

    return render
