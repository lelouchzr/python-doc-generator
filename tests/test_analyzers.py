from pathlib import Path

from docgen.analyzers import DependencyAnalyzer, PythonAnalyzer, StructureAnalyzer
from docgen.repository import Repository
from docgen.scanner import RepositoryScanner


def test_analyzers_extract_structure_symbols_and_dependencies(sample_repo: Path) -> None:
    repository = Repository(sample_repo)
    files = RepositoryScanner().scan(repository)
    modules = PythonAnalyzer().analyze(files)
    structure = StructureAnalyzer().analyze(repository, files)
    dependencies = DependencyAnalyzer().analyze(files, modules)

    symbol_names = {symbol.name for module in modules for symbol in module.symbols}

    assert structure.project_name == "sample"
    assert structure.has_tests is True
    assert "sample" in structure.package_roots
    assert "Service" in symbol_names
    assert "Service.run" in symbol_names
    assert dependencies.runtime == ("pydantic>=2",)
    assert dependencies.development == ("pytest>=8",)
    assert dependencies.scripts == {}
