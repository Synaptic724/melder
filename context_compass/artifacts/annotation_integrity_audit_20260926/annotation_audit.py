"""
Annotation integrity audit: find annotations that raise when evaluated on Python 3.14.

Two passes over a package tree:

- STATIC (AST, nothing imported). Every annotation site - parameters, returns, module/class
  variables, nested functions and classes, `type` aliases, and the text of string annotations - is
  checked for:
    STRING_IN_UNION  a string literal used as an operand of `|` (`"Conduit" | None`). Evaluating it
                     raises TypeError against None, str, classes, builtin generics, Optional/Union
                     and Any on 3.14.
    UNDEFINED_NAME   a name no enclosing scope binds (module, TYPE_CHECKING imports included; class
                     bodies; enclosing functions; type parameters; builtins). It raises NameError even
                     for a type checker.
- DYNAMIC (imports every module in a throwaway process). Each module's `if TYPE_CHECKING:` imports are
  bound into the module first, so an evaluation failure is a real defect and not the expected
  TYPE_CHECKING-only NameError. Then every annotation owner reachable from the module (module
  variables, classes and nested classes, functions, methods, static/class methods, property
  accessors) is evaluated in VALUE format. Any exception is reported as EVAL_ERROR.

Policy counts (not findings): PEP 604 unions and quoted annotations per file.

Usage:
    python -X gil=0 annotation_audit.py <src_root> <package> [--json <out.json>] [--static-only]
"""
import argparse
import ast
import builtins
import importlib
import inspect
import json
import pathlib
import sys
import traceback
from annotationlib import Format, get_annotations
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple


#region Finding


class Finding:
    """
    One located annotation defect.

    Contract:
        - `kind` is STRING_IN_UNION, UNDEFINED_NAME, EVAL_ERROR or IMPORT_ERROR.
        - `path` is relative to the scanned source root; `line` is 1-based.
        - `detail` is the offending expression text or exception message.
    """
    __slots__ = ("kind", "path", "line", "owner", "detail")

    def __init__(self, kind: str, path: str, line: int, owner: str, detail: str) -> None:
        """Store the finding fields verbatim."""
        self.kind: str = kind
        self.path: str = path
        self.line: int = line
        self.owner: str = owner
        self.detail: str = detail

    def as_dict(self) -> Dict[str, Any]:
        """Return the finding as a JSON-serialisable mapping."""
        return {"kind": self.kind, "path": self.path, "line": self.line, "owner": self.owner, "detail": self.detail}

    def render(self) -> str:
        """Return one report line: `KIND path:line owner -- detail`."""
        return f"{self.kind:15} {self.path}:{self.line} {self.owner} -- {self.detail}"
#endregion


#region StaticAnnotationAudit


class StaticAnnotationAudit(ast.NodeVisitor):
    """
    Walk one module's AST and check every annotation site without importing anything.

    Contract:
        - Tracks the enclosing scopes (module, classes, functions) and the names each binds, so a name
          is UNDEFINED only when no enclosing scope, type parameter or builtin provides it.
        - Annotations of local variables inside function bodies are never evaluated by Python and
          are skipped.
        - A module with a wildcard import skips UNDEFINED_NAME checks (its names are unknowable).
    """

    def __init__(self, source: str, rel_path: str) -> None:
        """Parse `source`; findings accumulate on `self.findings`."""
        self.rel_path: str = rel_path
        self.source: str = source
        self.tree: ast.Module = ast.parse(source)
        self.findings: List[Finding] = []
        self.pep604_unions: int = 0
        self.quoted_annotations: int = 0
        self.builtin_names: Set[str] = set(dir(builtins)) | {
            "__name__", "__file__", "__doc__", "__spec__", "__loader__", "__package__",
            "__builtins__", "__annotations__", "__dict__", "__module__", "__qualname__",
        }
        self.has_wildcard_import: bool = any(
            isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names)
            for node in ast.walk(self.tree)
        )
        # Each scope is (kind, name, bound names); kind is module, class or function.
        self.scopes: List[Tuple[str, str, Set[str]]] = [("module", "<module>", self._bound_names(self.tree.body))]

    def run(self) -> "StaticAnnotationAudit":
        """Visit the module and return self."""
        self.visit(self.tree)
        return self

    # --- scope bookkeeping -------------------------------------------------------------------

    def _bound_names(self, body: Iterable[ast.stmt]) -> Set[str]:
        """
        Return every name a statement block binds at its own level (recursing into if/try/with/for).

        Contract:
            Imports (including those under `if TYPE_CHECKING:`), def/class names, assignment,
            annotated-assignment, augmented-assignment, for/with targets, `type` aliases, walrus
            targets and `global`/`nonlocal` declarations all count as bindings.
        """
        names: Set[str] = set()
        stack: List[ast.AST] = list(body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name != "*":
                        names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.TypeAlias):
                names.update(self._target_names(node.name))
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    names.update(self._target_names(target))
                stack.extend(n for n in ast.walk(node) if isinstance(n, ast.NamedExpr))
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                names.update(self._target_names(node.target))
                stack.extend(node.body)
                stack.extend(node.orelse)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        names.update(self._target_names(item.optional_vars))
                stack.extend(node.body)
            elif isinstance(node, (ast.If, ast.While)):
                stack.extend(node.body)
                stack.extend(node.orelse)
            elif isinstance(node, (ast.Try, ast.TryStar)):
                stack.extend(node.body)
                stack.extend(node.orelse)
                stack.extend(node.finalbody)
                for handler in node.handlers:
                    if handler.name:
                        names.add(handler.name)
                    stack.extend(handler.body)
            elif isinstance(node, ast.Match):
                for case in node.cases:
                    stack.extend(case.body)
                    names.update(n.name for n in ast.walk(case.pattern) if isinstance(n, ast.MatchAs) and n.name)
            elif isinstance(node, (ast.Global, ast.Nonlocal)):
                names.update(node.names)
            elif isinstance(node, ast.NamedExpr):
                names.update(self._target_names(node.target))
            elif isinstance(node, ast.Expr):
                stack.extend(n for n in ast.walk(node) if isinstance(n, ast.NamedExpr))
        return names

    @staticmethod
    def _target_names(target: ast.AST) -> Set[str]:
        """Return the plain names an assignment target binds (tuples/lists/starred included)."""
        return {node.id for node in ast.walk(target) if isinstance(node, ast.Name)}

    def _function_bindings(self, node: ast.AST) -> Set[str]:
        """Return a function's parameters, type parameters and body-level bindings."""
        args = node.args
        names = {a.arg for a in args.posonlyargs + args.args + args.kwonlyargs}
        if args.vararg is not None:
            names.add(args.vararg.arg)
        if args.kwarg is not None:
            names.add(args.kwarg.arg)
        names.update(self._type_param_names(node))
        return names | self._bound_names(node.body)

    @staticmethod
    def _type_param_names(node: ast.AST) -> Set[str]:
        """Return PEP 695 type parameter names declared on a def/class/type statement."""
        return {param.name for param in (node.type_params or [])}

    def _owner(self, leaf: str) -> str:
        """Return the dotted owner path for a finding (enclosing classes/functions, then leaf)."""
        parts = [name for kind, name, _ in self.scopes if kind != "module"]
        return ".".join(parts + [leaf]) if leaf else ".".join(parts) or "<module>"

    def _visible_names(self, extra: Optional[Set[str]] = None) -> Set[str]:
        """Return names visible to an annotation evaluated in the current scope chain."""
        names: Set[str] = set(self.builtin_names)
        for _, _, bound in self.scopes:
            names |= bound
        if extra:
            names |= extra
        return names

    # --- visitors ------------------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Enter a class scope; check its bases' annotations are not needed, only its body."""
        bound = self._bound_names(node.body) | self._type_param_names(node)
        self.scopes.append(("class", node.name, bound))
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check a function's parameter and return annotations, then its body."""
        self._check_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check an async function exactly like a function."""
        self._check_function(node)

    def _check_function(self, node: ast.AST) -> None:
        """Check parameter/return annotations (visible: enclosing scopes plus type params)."""
        type_params = self._type_param_names(node)
        args = node.args
        for arg in args.posonlyargs + args.args + args.kwonlyargs + [args.vararg, args.kwarg]:
            if arg is not None and arg.annotation is not None:
                self._check_annotation(arg.annotation, self._owner(f"{node.name}({arg.arg})"), type_params)
        if node.returns is not None:
            self._check_annotation(node.returns, self._owner(f"{node.name}(return)"), type_params)
        self.scopes.append(("function", node.name, self._function_bindings(node)))
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Check module- and class-level variable annotations; function-local ones never evaluate."""
        if self.scopes[-1][0] != "function":
            target = ast.unparse(node.target)
            self._check_annotation(node.annotation, self._owner(target), set())
        if node.value is not None:
            self.visit(node.value)

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        """Check a `type X = ...` alias value (evaluated lazily on `__value__`)."""
        self._check_annotation(node.value, self._owner(ast.unparse(node.name)), self._type_param_names(node))

    # --- checks ------------------------------------------------------------------------------

    def _check_annotation(self, annotation: ast.expr, owner: str, extra_names: Set[str]) -> None:
        """Apply every check to one annotation expression (and to the text of a string annotation)."""
        self._check_expression(annotation, owner, extra_names, in_string=False)
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            self.quoted_annotations += 1
            try:
                inner = ast.parse(annotation.value, mode="eval").body
            except SyntaxError:
                self._add("UNPARSEABLE_STRING", annotation, owner, repr(annotation.value))
                return
            ast.fix_missing_locations(inner)
            self._check_expression(inner, owner, extra_names, in_string=True, anchor=annotation)
        elif any(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(annotation)):
            self.quoted_annotations += 1

    def _check_expression(
            self,
            expression: ast.expr,
            owner: str,
            extra_names: Set[str],
            *,
            in_string: bool,
            anchor: Optional[ast.AST] = None,
    ) -> None:
        """Find string operands of `|` and undefined names inside one expression."""
        where = anchor if anchor is not None else expression
        suffix = " (inside a string annotation)" if in_string else ""
        literal_ranges = self._literal_subtrees(expression)
        # Only the outermost `|` of a chain is examined (its operands are flattened), so one
        # `a | b | c` annotation yields one finding and counts as one union.
        inner_unions = {
            id(child)
            for node in ast.walk(expression)
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr)
            for child in (node.left, node.right)
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.BitOr)
        }
        for node in ast.walk(expression):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr) and id(node) not in inner_unions:
                if not in_string:
                    self.pep604_unions += 1
                if any(isinstance(op, ast.Constant) and isinstance(op.value, str) for op in self._union_operands(node)):
                    self._add("STRING_IN_UNION", where if in_string else node, owner, ast.unparse(node) + suffix)
        if self.has_wildcard_import:
            return
        visible = self._visible_names(extra_names)
        for node in ast.walk(expression):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and id(node) not in literal_ranges:
                if node.id not in visible:
                    self._add("UNDEFINED_NAME", where if in_string else node, owner, node.id + suffix)

    @staticmethod
    def _union_operands(node: ast.BinOp) -> List[ast.expr]:
        """Return the direct operands of one `|` chain (flattening nested `|` on either side)."""
        operands: List[ast.expr] = []
        stack: List[ast.expr] = [node]
        while stack:
            current = stack.pop()
            if isinstance(current, ast.BinOp) and isinstance(current.op, ast.BitOr):
                stack.append(current.left)
                stack.append(current.right)
            else:
                operands.append(current)
        return operands

    @staticmethod
    def _literal_subtrees(expression: ast.expr) -> Set[int]:
        """Return ids of nodes inside `Literal[...]` subscripts (their names are not references)."""
        ids: Set[int] = set()
        for node in ast.walk(expression):
            if isinstance(node, ast.Subscript):
                base = node.value
                base_name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", None)
                if base_name == "Literal":
                    ids.update(id(inner) for inner in ast.walk(node.slice))
        return ids

    def _add(self, kind: str, node: ast.AST, owner: str, detail: str) -> None:
        """Record one finding at the node's line."""
        self.findings.append(Finding(kind, self.rel_path, getattr(node, "lineno", 0), owner, detail))
#endregion


#region DynamicAnnotationAudit


class DynamicAnnotationAudit:
    """
    Import every module of a package, bind its TYPE_CHECKING imports, and evaluate every annotation.

    Contract:
        - Runs in the calling process and mutates the imported modules' globals (adds TYPE_CHECKING
          names); run it in a throwaway process only.
        - An owner whose VALUE-format annotation read raises is reported as EVAL_ERROR with the
          exception type and message; the TYPE_CHECKING binding step means a NameError here is a name
          that is undefined even for a type checker.
    """

    def __init__(self, src_root: pathlib.Path, package: str) -> None:
        """Remember the tree to import."""
        self.src_root: pathlib.Path = src_root
        self.package: str = package
        self.findings: List[Finding] = []
        self.modules: List[Any] = []
        self.owners_checked: int = 0
        self.type_checking_names_bound: int = 0

    def run(self) -> "DynamicAnnotationAudit":
        """Import, bind TYPE_CHECKING imports, then evaluate every owner."""
        sys.path.insert(0, str(self.src_root))
        for path, name in self._module_paths():
            try:
                self.modules.append((path, importlib.import_module(name)))
            except Exception as exc:
                self.findings.append(Finding("IMPORT_ERROR", self._rel(path), 1, name, f"{type(exc).__name__}: {exc}"))
        for path, module in self.modules:
            self._bind_type_checking_imports(path, module)
        for path, module in self.modules:
            for owner, qualname, line in self._owners(module):
                self._evaluate(owner, qualname, path, line)
        return self

    def _module_paths(self) -> Iterator[Tuple[pathlib.Path, str]]:
        """Yield (file, dotted module name) for every .py file under the package."""
        for path in sorted((self.src_root / self.package).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            parts = list(path.relative_to(self.src_root).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            yield path, ".".join(parts)

    def _rel(self, path: pathlib.Path) -> str:
        """Return `path` relative to the source root's parent (so it reads src/...)."""
        return str(path.relative_to(self.src_root.parent))

    def _bind_type_checking_imports(self, path: pathlib.Path, module: Any) -> None:
        """Execute the module's own `if TYPE_CHECKING:` imports into its globals (missing names only)."""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.If) or ast.unparse(node.test) not in ("TYPE_CHECKING", "typing.TYPE_CHECKING"):
                continue
            for stmt in node.body:
                if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    continue
                namespace: Dict[str, Any] = {}
                try:
                    exec(compile(ast.Module(body=[stmt], type_ignores=[]), str(path), "exec"), module.__dict__.copy(), namespace)
                except Exception as exc:
                    self.findings.append(Finding(
                        "TC_IMPORT_ERROR", self._rel(path), stmt.lineno, module.__name__,
                        f"{ast.unparse(stmt)} -> {type(exc).__name__}: {exc}",
                    ))
                    continue
                for key, value in namespace.items():
                    if key not in module.__dict__:
                        module.__dict__[key] = value
                        self.type_checking_names_bound += 1

    def _owners(self, module: Any) -> Iterator[Tuple[Any, str, int]]:
        """Yield (owner, qualname, line) for the module, its classes (recursively) and functions."""
        yield module, module.__name__, 1
        seen: Set[int] = set()
        for value in list(vars(module).values()):
            if getattr(value, "__module__", None) != module.__name__:
                continue
            if inspect.isclass(value):
                yield from self._class_owners(value, seen)
            elif inspect.isfunction(value):
                yield value, f"{module.__name__}.{value.__qualname__}", value.__code__.co_firstlineno

    def _class_owners(self, cls: type, seen: Set[int]) -> Iterator[Tuple[Any, str, int]]:
        """Yield a class, its nested classes and every function-like member defined on it."""
        if id(cls) in seen:
            return
        seen.add(id(cls))
        line = getattr(cls, "__firstlineno__", 1)
        yield cls, f"{cls.__module__}.{cls.__qualname__}", line
        for member in list(vars(cls).values()):
            candidates: List[Any] = []
            if isinstance(member, (staticmethod, classmethod)):
                candidates.append(member.__func__)
            elif isinstance(member, property):
                candidates.extend(f for f in (member.fget, member.fset, member.fdel) if f is not None)
            elif inspect.isfunction(member):
                candidates.append(member)
            elif inspect.isclass(member) and member.__module__ == cls.__module__:
                yield from self._class_owners(member, seen)
            for fn in candidates:
                if inspect.isfunction(fn):
                    yield fn, f"{fn.__module__}.{fn.__qualname__}", fn.__code__.co_firstlineno

    def _evaluate(self, owner: Any, qualname: str, path: pathlib.Path, line: int) -> None:
        """Read one owner's annotations in VALUE format and record any exception."""
        self.owners_checked += 1
        try:
            get_annotations(owner, format=Format.VALUE)
        except Exception as exc:
            source_file = inspect.getsourcefile(owner) if not inspect.ismodule(owner) else str(path)
            rel = self._rel(pathlib.Path(source_file)) if source_file else self._rel(path)
            self.findings.append(Finding("EVAL_ERROR", rel, line, qualname, f"{type(exc).__name__}: {exc}"))
#endregion


#region AnnotationAudit


class AnnotationAudit:
    """
    Run both passes over `<src_root>/<package>` and render a report.

    Contract:
        - Static findings are always produced; the dynamic pass runs unless `static_only`.
        - `report()` lists findings grouped by kind, then the policy counts.
    """

    def __init__(self, src_root: pathlib.Path, package: str, static_only: bool) -> None:
        """Remember the target and pass selection."""
        self.src_root: pathlib.Path = src_root
        self.package: str = package
        self.static_only: bool = static_only
        self.static: List[StaticAnnotationAudit] = []
        self.dynamic: Optional[DynamicAnnotationAudit] = None

    def run(self) -> "AnnotationAudit":
        """Run the static pass over every file, then the dynamic pass."""
        for path in sorted((self.src_root / self.package).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = str(path.relative_to(self.src_root.parent))
            self.static.append(StaticAnnotationAudit(path.read_text(encoding="utf-8"), rel).run())
        if not self.static_only:
            self.dynamic = DynamicAnnotationAudit(self.src_root, self.package).run()
        return self

    def findings(self) -> List[Finding]:
        """Return all findings, static first."""
        found = [f for audit in self.static for f in audit.findings]
        if self.dynamic is not None:
            found.extend(self.dynamic.findings)
        return found

    def report(self) -> str:
        """Render the human-readable report."""
        found = self.findings()
        lines = [
            f"files scanned: {len(self.static)}",
            f"findings: {len(found)}",
        ]
        if self.dynamic is not None:
            lines.append(
                f"dynamic: modules imported {len(self.dynamic.modules)}, TYPE_CHECKING names bound "
                f"{self.dynamic.type_checking_names_bound}, annotation owners evaluated {self.dynamic.owners_checked}"
            )
        for kind in ("STRING_IN_UNION", "UNDEFINED_NAME", "UNPARSEABLE_STRING", "EVAL_ERROR", "TC_IMPORT_ERROR", "IMPORT_ERROR"):
            group = [f for f in found if f.kind == kind]
            lines.append(f"\n== {kind}: {len(group)}")
            lines.extend("  " + f.render() for f in sorted(group, key=lambda f: (f.path, f.line)))
        unions = sum(a.pep604_unions for a in self.static)
        quoted = sum(a.quoted_annotations for a in self.static)
        lines.append(f"\npolicy counts (not defects): PEP 604 unions {unions}, quoted annotations {quoted}")
        return "\n".join(lines)
#endregion


def main() -> int:
    """Command-line entry point; exit status 1 when any finding exists."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("src_root")
    parser.add_argument("package")
    parser.add_argument("--json")
    parser.add_argument("--static-only", action="store_true")
    options = parser.parse_args()
    audit = AnnotationAudit(pathlib.Path(options.src_root).resolve(), options.package, options.static_only).run()
    print(audit.report())
    if options.json:
        pathlib.Path(options.json).write_text(json.dumps([f.as_dict() for f in audit.findings()], indent=1), encoding="utf-8")
    return 1 if audit.findings() else 0


if __name__ == "__main__":
    sys.exit(main())
