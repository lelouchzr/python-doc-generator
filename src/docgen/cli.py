"""Typer CLI for Python Doc Generator."""

import sys
from pathlib import Path
from typing import Annotated

import typer

from docgen.config import (
    DocgenConfig,
    LLMProvider,
    Section,
    load_config,
    merge_config,
    parse_exclude,
)
from docgen.config import (
    parse_sections as parse_config_sections,
)
from docgen.exceptions import DocgenError
from docgen.generator import DocumentationGenerator

app = typer.Typer(
    name="docgen",
    help="Generate useful Markdown documentation from a local Python repository.",
    no_args_is_help=True,
)

_COMMANDS = {"ask", "diagram", "generate"}


@app.command(name="generate")
def generate(
    repository: Annotated[Path, typer.Argument(help="Local repository to analyze.")],
    config: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to docgen.toml."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Directory for generated Markdown files."),
    ] = None,
    sections: Annotated[
        str | None,
        typer.Option("--sections", help="Comma-separated sections to generate."),
    ] = None,
    exclude: Annotated[
        str | None,
        typer.Option("--exclude", help="Comma-separated exclude patterns."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show generated file paths without writing files."),
    ] = False,
    llm: Annotated[
        LLMProvider | None,
        typer.Option("--llm", help="LLM provider: local, openai, anthropic or gemini."),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", help="Hosted model name for the selected LLM provider."),
    ] = None,
    max_tokens: Annotated[
        int | None,
        typer.Option("--max-tokens", help="Max output tokens for hosted providers."),
    ] = None,
) -> None:
    """Generate documentation for a local repository."""
    resolved = _resolve_config(
        config,
        output=output,
        sections=sections,
        exclude=exclude,
        llm=llm,
        model=model,
        max_tokens=max_tokens,
    )
    generator = DocumentationGenerator(resolved)
    paths = generator.preview_paths() if dry_run else generator.write(repository)
    for path in paths:
        typer.echo(path)


@app.command()
def ask(
    repository: Annotated[Path, typer.Argument(help="Local repository to analyze.")],
    question: Annotated[str, typer.Argument(help="Question to answer from repository context.")],
    config: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to docgen.toml."),
    ] = None,
    exclude: Annotated[
        str | None,
        typer.Option("--exclude", help="Comma-separated exclude patterns."),
    ] = None,
    rag_results: Annotated[
        int | None,
        typer.Option("--rag-results", help="Number of retrieval results to use."),
    ] = None,
    llm: Annotated[
        LLMProvider | None,
        typer.Option("--llm", help="LLM provider: local, openai, anthropic or gemini."),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", help="Hosted model name for the selected LLM provider."),
    ] = None,
    max_tokens: Annotated[
        int | None,
        typer.Option("--max-tokens", help="Max output tokens for hosted providers."),
    ] = None,
) -> None:
    """Ask a question about the repository using RAG context."""
    resolved = _resolve_config(
        config,
        exclude=exclude,
        rag_results=rag_results,
        llm=llm,
        model=model,
        max_tokens=max_tokens,
    )
    typer.echo(DocumentationGenerator(resolved).ask(repository, question))


@app.command()
def diagram(
    repository: Annotated[Path, typer.Argument(help="Local repository to analyze.")],
    config: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to docgen.toml."),
    ] = None,
    exclude: Annotated[
        str | None,
        typer.Option("--exclude", help="Comma-separated exclude patterns."),
    ] = None,
) -> None:
    """Print Mermaid diagrams for a repository."""
    resolved = _resolve_config(config, exclude=exclude)
    typer.echo(DocumentationGenerator(resolved).diagram(repository))


def parse_sections(raw: str) -> tuple[Section, ...]:
    """Parse a comma-separated section list."""
    try:
        return parse_config_sections(raw)
    except DocgenError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _resolve_config(
    config_path: Path | None,
    *,
    output: Path | None = None,
    sections: str | None = None,
    exclude: str | None = None,
    rag_results: int | None = None,
    llm: LLMProvider | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
) -> DocgenConfig:
    base = load_config(config_path)
    return merge_config(
        base,
        output_dir=output,
        sections=parse_sections(sections) if sections is not None else None,
        exclude=parse_exclude(exclude) if exclude is not None else None,
        rag_results=rag_results,
        llm_provider=llm,
        llm_model=model,
        max_tokens=max_tokens,
    )


def _inject_default_command(argv: list[str]) -> list[str]:
    if len(argv) <= 1:
        return argv
    first = argv[1]
    if first in _COMMANDS or first in {"--help", "-h"}:
        return argv
    return [argv[0], "generate", *argv[1:]]


def main() -> None:
    """Run the Typer app."""
    sys.argv = _inject_default_command(sys.argv)
    try:
        app()
    except DocgenError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    main()
