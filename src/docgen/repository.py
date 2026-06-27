"""Repository path validation."""

from pathlib import Path

from docgen.exceptions import RepositoryNotFoundError


class Repository:
    """Validated local repository path."""

    def __init__(self, path: str | Path) -> None:
        root = Path(path).expanduser().resolve()
        if not root.exists():
            msg = f"Repository path does not exist: {root}"
            raise RepositoryNotFoundError(msg)
        if not root.is_dir():
            msg = f"Repository path is not a directory: {root}"
            raise RepositoryNotFoundError(msg)
        self.root = root

    @property
    def name(self) -> str:
        return self.root.name

