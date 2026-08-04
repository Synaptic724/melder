import ast
import pathlib
from collections import defaultdict
import json
import sys


ROOT = pathlib.Path(
    r"<local-workspace>\src\melder\aether\conduit"
)
SRC_ROOT = pathlib.Path(r"<local-workspace>\src")


class ImportUsageScanner(ast.NodeVisitor):
    def __init__(self, imported_names: dict[str, str]) -> None:
        self.imported_names = imported_names
        self.type_checking_depth = 0
        self.annotation_node_ids: set[int] = set()
        self.annotation_usage = defaultdict(int)
        self.constructor_calls = defaultdict(int)
        self.isinstance_calls = defaultdict(int)
        self.base_class_usage = defaultdict(int)
        self.runtime_other = defaultdict(int)

    def in_type_checking(self) -> bool:
        return self.type_checking_depth > 0

    def visit_If(self, node: ast.If) -> None:
        is_type_checking_guard = (
            isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
        )
        if is_type_checking_guard:
            self.type_checking_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        if is_type_checking_guard:
            self.type_checking_depth -= 1
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self.imported_names:
                self.base_class_usage[base.id] += 1
        self.generic_visit(node)

    def _mark_annotation_tree(self, node: ast.AST | None) -> None:
        if node is None:
            return
        for child in ast.walk(node):
            self.annotation_node_ids.add(id(child))

    def visit_arg(self, node: ast.arg) -> None:
        self._mark_annotation_tree(node.annotation)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._mark_annotation_tree(node.annotation)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._mark_annotation_tree(node.returns)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._mark_annotation_tree(node.returns)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.imported_names:
                self.constructor_calls[func_name] += 1
            elif func_name in {"isinstance", "issubclass"} and len(node.args) > 1:
                class_arg = node.args[1]
                if isinstance(class_arg, ast.Name) and class_arg.id in self.imported_names:
                    self.isinstance_calls[class_arg.id] += 1
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if self.in_type_checking():
            return
        if not isinstance(node.ctx, ast.Load):
            return
        if node.id not in self.imported_names:
            return
        if id(node) in self.annotation_node_ids:
            self.annotation_usage[node.id] += 1
            return
        parent = getattr(node, "parent", None)
        if isinstance(parent, ast.Call):
            return
        if isinstance(parent, ast.ClassDef):
            return
        if isinstance(parent, (ast.arg, ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        self.runtime_other[node.id] += 1


def attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent


def collect_imports(tree: ast.AST) -> dict[str, dict[str, str | bool]]:
    imports: dict[str, dict[str, str | bool]] = {}

    def walk(nodes: list[ast.stmt], in_type_checking: bool) -> None:
        for node in nodes:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("melder."):
                for alias in node.names:
                    imports[alias.asname or alias.name] = {
                        "import": f"from {node.module} import {alias.name}",
                        "in_type_checking": in_type_checking,
                    }
            elif isinstance(node, ast.If):
                tc_guard = isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
                walk(node.body, in_type_checking or tc_guard)
                walk(node.orelse, in_type_checking)

    walk(list(tree.body), False)
    return imports


def _module_file_for(module_name: str) -> pathlib.Path | None:
    relative = pathlib.Path(*module_name.split("."))
    module_file = SRC_ROOT / f"{relative}.py"
    if module_file.exists():
        return module_file
    package_file = SRC_ROOT / relative / "__init__.py"
    if package_file.exists():
        return package_file
    return None


def classify_imported_symbol(module_name: str, symbol_name: str) -> str:
    module_file = _module_file_for(module_name)
    if module_file is None:
        return "unknown"
    try:
        tree = ast.parse(module_file.read_text(encoding="utf-8-sig"), filename=str(module_file))
    except SyntaxError:
        return "unknown"
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == symbol_name:
            base_names = set()
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.add(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.add(base.attr)
            if "Enum" in base_names:
                return "enum"
            if "Protocol" in base_names:
                return "protocol"
            return "class"
    return "other"


def scan_file(path: pathlib.Path) -> dict[str, dict[str, int | str]]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    attach_parents(tree)
    imports = collect_imports(tree)
    scanner = ImportUsageScanner({name: meta["import"] for name, meta in imports.items()})
    scanner.visit(tree)
    result: dict[str, dict[str, int | str]] = {}
    for name, meta in sorted(imports.items()):
        import_stmt = str(meta["import"])
        module_name = import_stmt.split()[1]
        symbol_name = import_stmt.split()[-1]
        result[name] = {
            "import": import_stmt,
            "imported_kind": classify_imported_symbol(module_name, symbol_name),
            "in_type_checking": bool(meta["in_type_checking"]),
            "annotation_usage": scanner.annotation_usage.get(name, 0),
            "constructor_calls": scanner.constructor_calls.get(name, 0),
            "isinstance_calls": scanner.isinstance_calls.get(name, 0),
            "base_class_usage": scanner.base_class_usage.get(name, 0),
            "runtime_other": scanner.runtime_other.get(name, 0),
        }
    return result


def collect_quoted_annotations(path: pathlib.Path) -> list[dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    findings: list[dict[str, object]] = []
    local_class_names = {
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }

    def check_annotation(node: ast.AST | None, owner: str) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in local_class_names:
                return
            findings.append(
                {
                    "owner": owner,
                    "line": getattr(node, "lineno", None),
                    "annotation": node.value,
                }
            )

    for item in ast.walk(tree):
        if isinstance(item, ast.FunctionDef):
            check_annotation(item.returns, f"{item.name} return")
            for arg in item.args.args + item.args.kwonlyargs:
                check_annotation(arg.annotation, f"{item.name} arg:{arg.arg}")
            if item.args.vararg is not None:
                check_annotation(item.args.vararg.annotation, f"{item.name} vararg")
            if item.args.kwarg is not None:
                check_annotation(item.args.kwarg.annotation, f"{item.name} kwarg")
        elif isinstance(item, ast.AsyncFunctionDef):
            check_annotation(item.returns, f"{item.name} return")
            for arg in item.args.args + item.args.kwonlyargs:
                check_annotation(arg.annotation, f"{item.name} arg:{arg.arg}")
            if item.args.vararg is not None:
                check_annotation(item.args.vararg.annotation, f"{item.name} vararg")
            if item.args.kwarg is not None:
                check_annotation(item.args.kwarg.annotation, f"{item.name} kwarg")
        elif isinstance(item, ast.AnnAssign):
            target_name = getattr(item.target, "id", "<annassign>")
            check_annotation(item.annotation, f"annassign:{target_name}")
    return findings


def main() -> None:
    payload = {}
    for path in sorted(ROOT.rglob("*.py")):
        payload[str(path)] = {
            "imports": scan_file(path),
            "quoted_annotations": collect_quoted_annotations(path),
        }

    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        for file, info in payload.items():
            import_findings = []
            for name, meta in info["imports"].items():
                if meta["in_type_checking"]:
                    continue
                if meta["imported_kind"] == "enum":
                    continue
                if (
                    meta["annotation_usage"] > 0
                    and meta["constructor_calls"] == 0
                    and meta["isinstance_calls"] == 0
                    and meta["base_class_usage"] == 0
                    and meta["runtime_other"] == 0
                ):
                    import_findings.append((name, meta["import"]))
            quoted_findings = info["quoted_annotations"]
            if import_findings or quoted_findings:
                print(file)
                for name, import_stmt in import_findings:
                    kind = info["imports"][name]["imported_kind"]
                    print(f"  TYPE_ONLY_IMPORT {name} [{kind}] :: {import_stmt}")
                for finding in quoted_findings:
                    print(
                        "  QUOTED_ANNOTATION "
                        f"line={finding['line']} owner={finding['owner']} "
                        f"value={finding['annotation']}"
                    )
        return

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
