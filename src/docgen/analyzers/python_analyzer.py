"""Small Python static analyzer based on the standard-library AST."""

import ast
from pathlib import Path

from docgen.config import DocgenConfig
from docgen.models import PythonModuleSummary, PythonSymbol, RepositoryFile


class PythonAnalyzer:
    """Extract modules, imports, classes and functions from Python files."""

    def __init__(self, config: DocgenConfig | None = None) -> None:
        self._config = config or DocgenConfig()

    def analyze(self, files: tuple[RepositoryFile, ...]) -> tuple[PythonModuleSummary, ...]:
        modules: list[PythonModuleSummary] = []
        for file in files:
            if file.suffix != ".py":
                continue
            try:
                tree = ast.parse(file.content)
            except SyntaxError:
                continue
            module_name = _module_name(file.relative_path)
            symbols = tuple(self._iter_symbols(tree, module_name, file.relative_path))
            modules.append(
                PythonModuleSummary(
                    module=module_name,
                    path=file.relative_path,
                    docstring=ast.get_docstring(tree),
                    imports=tuple(sorted(_collect_imports(tree))),
                    symbols=symbols,
                )
            )
        return tuple(modules)

    def _iter_symbols(
        self,
        tree: ast.Module,
        module_name: str,
        relative_path: str,
    ) -> list[PythonSymbol]:
        symbols: list[PythonSymbol] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if self._include_name(node.name):
                    symbols.append(_class_symbol(node, module_name, relative_path))
                symbols.extend(
                    symbol
                    for symbol in _class_methods(node, module_name, relative_path)
                    if self._include_name(symbol.name.split(".")[-1])
                )
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if self._include_name(node.name):
                    symbols.append(_function_symbol(node, module_name, relative_path))
        return symbols

    def _include_name(self, name: str) -> bool:
        return self._config.include_private or not name.startswith("_")


def _module_name(relative_path: str) -> str:
    path = Path(relative_path)
    without_suffix = path.with_suffix("")
    parts = [part for part in without_suffix.parts if part != "__init__"]
    return ".".join(parts) or path.stem


def _collect_imports(tree: ast.Module) -> set[str]:
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    return imports


def _class_symbol(node: ast.ClassDef, module_name: str, relative_path: str) -> PythonSymbol:
    bases = [_node_name(base) for base in node.bases]
    signature = f"class {node.name}"
    if bases:
        signature += f"({', '.join(bases)})"
    return PythonSymbol(
        name=node.name,
        kind="class",
        module=module_name,
        path=relative_path,
        lineno=node.lineno,
        end_lineno=getattr(node, "end_lineno", None),
        signature=signature,
        docstring=ast.get_docstring(node),
        decorators=tuple(_node_name(decorator) for decorator in node.decorator_list),
    )


def _class_methods(
    node: ast.ClassDef,
    module_name: str,
    relative_path: str,
) -> list[PythonSymbol]:
    methods: list[PythonSymbol] = []
    for child in node.body:
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
            method = _function_symbol(child, module_name, relative_path)
            methods.append(method.model_copy(update={"name": f"{node.name}.{method.name}"}))
    return methods


def _function_symbol(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_name: str,
    relative_path: str,
) -> PythonSymbol:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return PythonSymbol(
        name=node.name,
        kind="function",
        module=module_name,
        path=relative_path,
        lineno=node.lineno,
        end_lineno=getattr(node, "end_lineno", None),
        signature=f"{prefix} {node.name}{_format_args(node.args)}",
        docstring=ast.get_docstring(node),
        decorators=tuple(_node_name(decorator) for decorator in node.decorator_list),
    )


def _format_args(args: ast.arguments) -> str:
    names = [arg.arg for arg in args.posonlyargs + args.args]
    if args.vararg:
        names.append(f"*{args.vararg.arg}")
    names.extend(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        names.append(f"**{args.kwarg.arg}")
    return f"({', '.join(names)})"


def _node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_node_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _node_name(node.func)
    if isinstance(node, ast.Subscript):
        return _node_name(node.value)
    return node.__class__.__name__

