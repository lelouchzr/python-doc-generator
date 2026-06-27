"""Formatting helpers shared by Markdown generators."""

from collections.abc import Iterable

from docgen.models import DependencyInfo, PythonModuleSummary, RepositoryAnalysis


def heading(title: str, level: int = 1) -> str:
    return f"{'#' * level} {title}"


def bullet_list(items: Iterable[str], *, empty: str = "No items detected.") -> str:
    values = [item for item in items if item]
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in values)


def numbered_list(items: Iterable[str], *, empty: str = "No items detected.") -> str:
    values = [item for item in items if item]
    if not values:
        return f"1. {empty}"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(values, start=1))


def module_lines(modules: tuple[PythonModuleSummary, ...]) -> list[str]:
    lines: list[str] = []
    for module in modules:
        summary = module.docstring.splitlines()[0] if module.docstring else "No module docstring."
        lines.append(f"`{module.module}` ({module.path}) - {summary}")
    return lines


def dependency_lines(dependencies: DependencyInfo) -> list[str]:
    lines = [f"`{dependency}`" for dependency in dependencies.runtime]
    if not lines and dependencies.imported_packages:
        lines = [f"`{dependency}`" for dependency in dependencies.imported_packages[:10]]
    return lines


def project_overview(analysis: RepositoryAnalysis) -> str:
    structure = analysis.structure
    return (
        f"`{structure.project_name}` contains {len(structure.files)} indexed text files, "
        f"{len(analysis.python_modules)} Python modules and about "
        f"{structure.total_lines} lines of scanned content."
    )

