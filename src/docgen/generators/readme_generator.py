"""README draft generator."""

from docgen.generators.common import bullet_list, dependency_lines, heading, project_overview
from docgen.integrations.rag import RepositoryRAG
from docgen.models import RepositoryAnalysis


class ReadmeGenerator:
    """Generate a practical README draft."""

    filename = "README.generated.md"
    title = "README Draft"

    def render(self, analysis: RepositoryAnalysis, rag: RepositoryRAG) -> str:
        structure = analysis.structure
        package_roots = structure.package_roots or ("No package roots detected",)
        snippets = rag.search("project purpose quick start usage", limit=3)
        return "\n\n".join(
            [
                heading(structure.project_name),
                project_overview(analysis),
                heading("What It Does", 2),
                _purpose_text(snippets),
                heading("Install", 2),
                _install_block(analysis),
                heading("Usage", 2),
                _usage_block(analysis),
                heading("Project Layout", 2),
                bullet_list(package_roots),
                heading("Examples", 2),
                bullet_list(_example_lines(analysis)),
                heading("Detected Dependencies", 2),
                bullet_list(dependency_lines(analysis.dependencies)),
                heading("Generated Documentation", 2),
                bullet_list(
                    [
                        "`README.generated.md` - README draft",
                        "`ARCHITECTURE.md` - architecture overview",
                        "`API.md` - API reference draft",
                        "`DIAGRAMS.md` - Mermaid diagrams",
                        "`QUESTIONS.md` - repository Q&A",
                        "`ROADMAP.md` - roadmap suggestions",
                        "`PROJECT_SUMMARY.md` - concise project summary",
                    ]
                ),
            ]
        )


def _purpose_text(snippets: list[str]) -> str:
    if not snippets:
        return "This project is a Python codebase with generated documentation support."
    first = snippets[0].splitlines()[0]
    return f"This draft was generated from repository content. Most relevant source: {first}"


def _install_block(analysis: RepositoryAnalysis) -> str:
    if any(file.relative_path == "uv.lock" for file in analysis.structure.files):
        return "```bash\nuv sync\n```"
    if any(file.relative_path == "pyproject.toml" for file in analysis.structure.files):
        return "```bash\npip install -e .\n```"
    if any(file.relative_path.startswith("requirements") for file in analysis.structure.files):
        return "```bash\npip install -r requirements.txt\n```"
    return "```bash\n# Add installation instructions here.\n```"


def _usage_block(analysis: RepositoryAnalysis) -> str:
    scripts = analysis.dependencies.scripts
    if scripts:
        commands = "\n".join(f"{name} --help" for name in sorted(scripts))
        return f"```bash\n{commands}\n```"
    packages = analysis.structure.package_roots
    if packages:
        first = packages[0].replace("/", ".")
        return f"```bash\npython -m {first}\n```"
    return "```bash\n# Add usage instructions here.\n```"


def _example_lines(analysis: RepositoryAnalysis) -> list[str]:
    examples = [
        file.relative_path
        for file in analysis.structure.files
        if file.relative_path.startswith("examples/")
    ]
    return [f"`{path}`" for path in examples[:10]]
