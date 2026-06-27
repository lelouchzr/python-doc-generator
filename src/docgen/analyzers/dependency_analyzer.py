"""Dependency analyzer for Python project metadata."""

import tomllib

from docgen.models import DependencyInfo, PythonModuleSummary, RepositoryFile


class DependencyAnalyzer:
    """Extract dependency hints from pyproject and requirements files."""

    def analyze(
        self,
        files: tuple[RepositoryFile, ...],
        modules: tuple[PythonModuleSummary, ...],
    ) -> DependencyInfo:
        runtime: list[str] = []
        optional: dict[str, tuple[str, ...]] = {}
        development: list[str] = []
        scripts: dict[str, str] = {}

        for file in files:
            if file.relative_path == "pyproject.toml":
                pyproject_runtime, pyproject_optional, pyproject_scripts = _parse_pyproject(
                    file.content
                )
                runtime.extend(pyproject_runtime)
                optional.update(pyproject_optional)
                scripts.update(pyproject_scripts)
                development.extend(_development_dependencies(pyproject_optional))
            elif file.relative_path.startswith("requirements") and file.suffix == ".txt":
                runtime.extend(_parse_requirements(file.content))

        imports = sorted({item for module in modules for item in module.imports})
        return DependencyInfo(
            runtime=tuple(_unique(runtime)),
            optional={key: tuple(_unique(value)) for key, value in sorted(optional.items())},
            development=tuple(_unique(development)),
            imported_packages=tuple(imports),
            scripts=scripts,
        )


def _parse_pyproject(
    content: str,
) -> tuple[list[str], dict[str, tuple[str, ...]], dict[str, str]]:
    parsed = tomllib.loads(content)
    project = parsed.get("project", {})
    dependencies = [str(item) for item in project.get("dependencies", [])]
    optional_raw = project.get("optional-dependencies", {})
    optional = {
        str(name): tuple(str(item) for item in values)
        for name, values in optional_raw.items()
        if isinstance(values, list)
    }
    scripts_raw = project.get("scripts", {})
    scripts = {
        str(name): str(target)
        for name, target in scripts_raw.items()
        if isinstance(name, str) and isinstance(target, str)
    }
    return dependencies, optional, scripts


def _parse_requirements(content: str) -> list[str]:
    dependencies: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        dependencies.append(line)
    return dependencies


def _development_dependencies(optional: dict[str, tuple[str, ...]]) -> list[str]:
    names = {"dev", "docs", "test", "tests", "lint"}
    dependencies: list[str] = []
    for group, values in optional.items():
        if group.lower() in names:
            dependencies.extend(values)
    return dependencies


def _unique(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
