"""Write generated Markdown documents to disk."""

from pathlib import Path

from docgen.models import GeneratedDocument


class OutputWriter:
    """Persist generated documents in a target directory."""

    def write(self, output_dir: Path, documents: tuple[GeneratedDocument, ...]) -> tuple[Path, ...]:
        output_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for document in documents:
            path = output_dir / document.filename
            path.write_text(_with_trailing_newline(document.content), encoding="utf-8")
            written.append(path)
        return tuple(written)


def _with_trailing_newline(content: str) -> str:
    stripped = content.rstrip()
    return f"{stripped}\n"

