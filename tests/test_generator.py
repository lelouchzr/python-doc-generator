from pathlib import Path

from docgen.config import DocgenConfig, Section
from docgen.generator import DocumentationGenerator


def test_generator_writes_selected_sections(sample_repo: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "docs"
    generator = DocumentationGenerator(
        DocgenConfig(output_dir=output_dir, sections=(Section.README, Section.API))
    )

    written = generator.write(sample_repo)

    assert [path.name for path in written] == ["README.generated.md", "API.md"]
    assert (output_dir / "README.generated.md").exists()
    assert "sample" in (output_dir / "README.generated.md").read_text(encoding="utf-8")
    assert "Service.run" in (output_dir / "API.md").read_text(encoding="utf-8")


def test_generator_answers_questions(sample_repo: Path) -> None:
    answer = DocumentationGenerator().ask(sample_repo, "What does the service do?")

    assert "# Answer:" in answer
    assert "Relevant context" in answer


def test_generator_respects_exclude_patterns(sample_repo: Path) -> None:
    generator = DocumentationGenerator(DocgenConfig(exclude=("sample",)))

    analysis, _rag = generator.analyze(sample_repo)

    assert all(not module.path.startswith("sample/") for module in analysis.python_modules)


def test_generator_inspects_repository(sample_repo: Path) -> None:
    report = DocumentationGenerator().inspect(sample_repo)

    assert "# Repository Inspection" in report
    assert "Python modules" in report
    assert "Service.run" in report
