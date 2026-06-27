"""Typed data models shared across scanner, analyzers and generators."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class RepositoryFile(BaseModel):
    """A text file discovered in a repository."""

    model_config = ConfigDict(frozen=True)

    path: Path
    relative_path: str
    suffix: str
    content: str
    size: int = Field(ge=0)

    @property
    def line_count(self) -> int:
        return len(self.content.splitlines())


class PythonSymbol(BaseModel):
    """A class or function discovered in a Python source file."""

    model_config = ConfigDict(frozen=True)

    name: str
    kind: str
    module: str
    path: str
    lineno: int
    end_lineno: int | None = None
    signature: str | None = None
    docstring: str | None = None
    decorators: tuple[str, ...] = ()


class PythonModuleSummary(BaseModel):
    """Static summary for one Python module."""

    model_config = ConfigDict(frozen=True)

    module: str
    path: str
    docstring: str | None = None
    imports: tuple[str, ...] = ()
    symbols: tuple[PythonSymbol, ...] = ()


class DependencyInfo(BaseModel):
    """Dependencies detected from project metadata files."""

    model_config = ConfigDict(frozen=True)

    runtime: tuple[str, ...] = ()
    optional: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    development: tuple[str, ...] = ()
    imported_packages: tuple[str, ...] = ()
    scripts: dict[str, str] = Field(default_factory=dict)


class ProjectStructure(BaseModel):
    """Repository structure facts used by documentation generators."""

    model_config = ConfigDict(frozen=True)

    root: Path
    project_name: str
    files: tuple[RepositoryFile, ...]
    top_level_entries: tuple[str, ...]
    file_counts_by_suffix: dict[str, int] = Field(default_factory=dict)
    total_lines: int = 0
    has_tests: bool = False
    has_docs: bool = False
    has_ci: bool = False
    package_roots: tuple[str, ...] = ()


class RepositoryAnalysis(BaseModel):
    """Complete deterministic analysis of a repository."""

    model_config = ConfigDict(frozen=True)

    structure: ProjectStructure
    python_modules: tuple[PythonModuleSummary, ...]
    dependencies: DependencyInfo


class GeneratedDocument(BaseModel):
    """A generated Markdown document ready to write to disk."""

    model_config = ConfigDict(frozen=True)

    filename: str
    title: str
    content: str
