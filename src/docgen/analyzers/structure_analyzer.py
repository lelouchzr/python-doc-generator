"""Repository structure analyzer."""

from collections import Counter
from pathlib import Path

from docgen.models import ProjectStructure, RepositoryFile
from docgen.repository import Repository


class StructureAnalyzer:
    """Summarize project layout and documentation health signals."""

    def analyze(
        self,
        repository: Repository,
        files: tuple[RepositoryFile, ...],
    ) -> ProjectStructure:
        top_level_entries = tuple(sorted(path.name for path in repository.root.iterdir()))
        counts = Counter(file.suffix or "<none>" for file in files)
        relative_paths = {file.relative_path for file in files}
        return ProjectStructure(
            root=repository.root,
            project_name=repository.name,
            files=files,
            top_level_entries=top_level_entries,
            file_counts_by_suffix=dict(sorted(counts.items())),
            total_lines=sum(file.line_count for file in files),
            has_tests=_has_path_prefix(relative_paths, "tests") or any(
                path.startswith("test_") for path in relative_paths
            ),
            has_docs=_has_path_prefix(relative_paths, "docs") or "mkdocs.yml" in relative_paths,
            has_ci=_has_path_prefix(relative_paths, ".github/workflows"),
            package_roots=_detect_package_roots(files),
        )


def _has_path_prefix(paths: set[str], prefix: str) -> bool:
    normalized = prefix.rstrip("/") + "/"
    return any(path == prefix or path.startswith(normalized) for path in paths)


def _detect_package_roots(files: tuple[RepositoryFile, ...]) -> tuple[str, ...]:
    roots: set[str] = set()
    for file in files:
        if file.suffix != ".py":
            continue
        path = Path(file.relative_path)
        if path.name == "__init__.py":
            parent = path.parent.as_posix()
            if parent == ".":
                continue
            roots.add(parent)
    return tuple(sorted(roots))
