"""Repository scanner for text files that are useful for documentation."""

from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path

from docgen.config import DocgenConfig
from docgen.models import RepositoryFile
from docgen.repository import Repository

TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "generated-docs",
    "node_modules",
    "site",
}


class RepositoryScanner:
    """Collect repository files that should be indexed and analyzed."""

    def __init__(
        self,
        config: DocgenConfig | None = None,
        *,
        ignore_dirs: Iterable[str] = DEFAULT_IGNORE_DIRS,
    ) -> None:
        self._config = config or DocgenConfig()
        self._ignore_dirs = frozenset(ignore_dirs)

    def scan(self, repository: Repository) -> tuple[RepositoryFile, ...]:
        files: list[RepositoryFile] = []
        for path in sorted(repository.root.rglob("*")):
            if not path.is_file() or self._is_ignored(path, repository.root):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            size = path.stat().st_size
            if size > self._config.max_file_size:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            if not content.strip():
                continue
            files.append(
                RepositoryFile(
                    path=path,
                    relative_path=path.relative_to(repository.root).as_posix(),
                    suffix=path.suffix.lower(),
                    content=content,
                    size=size,
                )
            )
        return tuple(files)

    def _is_ignored(self, path: Path, root: Path) -> bool:
        relative_parts = path.relative_to(root).parts
        relative_path = path.relative_to(root).as_posix()
        if any(part in self._ignore_dirs for part in relative_parts):
            return True
        return any(_matches_pattern(relative_path, pattern) for pattern in self._config.exclude)


def _matches_pattern(relative_path: str, pattern: str) -> bool:
    normalized = pattern.strip().strip("/")
    if not normalized:
        return False
    parts = relative_path.split("/")
    return (
        fnmatch(relative_path, normalized)
        or any(fnmatch(part, normalized) for part in parts)
        or relative_path.startswith(f"{normalized}/")
    )
