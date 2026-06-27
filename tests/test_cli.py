from pathlib import Path

from typer.testing import CliRunner

from docgen.cli import _inject_default_command, app, parse_sections
from docgen.config import Section


def test_parse_sections() -> None:
    assert parse_sections("readme,api") == (Section.README, Section.API)


def test_default_command_injection() -> None:
    assert _inject_default_command(["docgen", "./repo"]) == ["docgen", "generate", "./repo"]
    assert _inject_default_command(["docgen", "ask", "./repo", "Question?"]) == [
        "docgen",
        "ask",
        "./repo",
        "Question?",
    ]


def test_cli_generates_docs(sample_repo: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "generated"

    result = runner.invoke(
        app,
        [
            "generate",
            str(sample_repo),
            "--output",
            str(output_dir),
            "--sections",
            "readme,diagrams",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "README.generated.md").exists()
    assert (output_dir / "DIAGRAMS.md").exists()


def test_cli_dry_run_does_not_write(sample_repo: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "generated"

    result = runner.invoke(
        app,
        [
            "generate",
            str(sample_repo),
            "--output",
            str(output_dir),
            "--sections",
            "readme",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "README.generated.md" in result.output
    assert not output_dir.exists()


def test_cli_ask(sample_repo: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["ask", str(sample_repo), "Where is the package?"])

    assert result.exit_code == 0, result.output
    assert "Package roots" in result.output
