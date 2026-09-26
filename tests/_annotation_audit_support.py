"""
Annotation integrity audit: locate annotations that raise when Python 3.14 evaluates them.

Python 3.14 evaluates annotations lazily, when something reads them (`inspect.signature`,
`typing.get_type_hints`, `annotationlib.get_annotations`, documentation and DI tooling). A defect in an
annotation therefore stays silent at import and fails only for the tool that reads it. Two defect kinds
exist, and this module finds both:

- STRING_IN_UNION: a string literal used as an operand of `|`, e.g. `"Conduit" | None`. Evaluating it
  raises TypeError when the other operand is None, a str, a class, a builtin generic or Any. A
  `typing.Union` operand (`Optional[X] | "Y"`), a `typing.List[...]`-style alias or a TypeVar wraps the
  string in a ForwardRef instead on 3.14.7 (3.14.0rc2 still raised for Union operands). Those shapes are
  reported too: the repository forbids both `|` unions and quoted type names, and whether they raise
  depends on the interpreter build.
- UNDEFINED_NAME / EVAL_ERROR: an annotation naming something no scope binds - not imported, not even
  under `TYPE_CHECKING` - which raises NameError for every reader, type checkers included.

Two passes:

- `StaticAnnotationAudit` parses source (nothing is imported) and checks every annotation site:
  parameters, returns, module and class variables, nested functions and classes, `type` aliases, and
  the text of string annotations. Local-variable annotations inside function bodies are never
  evaluated by Python and are skipped.
- `DynamicAnnotationAudit` imports every module, binds each module's own `if TYPE_CHECKING:` imports
  into its globals (so the expected TYPE_CHECKING-only NameError cannot occur), then evaluates every
  reachable annotation owner in VALUE format. It mutates module globals: run it in a throwaway
  process (the command-line entry point below).

Usage (from the repository root):
    python -X gil=0 tests/_annotation_audit_support.py src melder [--static-only | --dynamic-only]
Exit status 1 when any finding exists.
"""
import argparse
import ast
import builtins
import importlib
import importlib.util
import inspect
import json
import pathlib
import sys
from annotationlib import Format, get_annotations
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple


#region AnnotationFinding


class AnnotationFinding:
    """
    One located annotation defect.

    Contract:
        - `kind` is one of STRING_IN_UNION, UNDEFINED_NAME, UNPARSEABLE_STRING, EVAL_ERROR,
          TC_IMPORT_ERROR or IMPORT_ERROR.
        - `path` is relative to the parent of the scanned source root (so it reads `src/...`);
          `line` is 1-based.
        - `owner` is the dotted definition path the annotation belongs to; `detail` is the offending
          expression text or the exception message.
        - Value object: no references to live modules or AST nodes are kept.
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
        return {
            "kind": self.kind,
            "path": self.path,
            "line": self.line,
            "owner": self.owner,
            "detail": self.detail,
        }

    def render(self) -> str:
        """Return one report line: `KIND path:line owner -- detail`."""
        return f"{self.kind:18} {self.path}:{self.line} {self.owner} -- {self.detail}"
#endregion


#region StaticAnnotationAudit


class StaticAnnotationAudit(ast.NodeVisitor):
    """
    Check every annotation site of one module's source without importing it.

    Contract:
        - Tracks enclosing scopes (module, classes, functions) and the names each binds; a name is
          UNDEFINED only when no enclosing scope, PEP 695 type parameter or builtin provides it.
          Imports under `if TYPE_CHECKING:` count as bindings (type checkers see them, and the dynamic
          pass binds them).
        - Class-body annotation scopes can see class-level names on 3.14, so method and class-variable
          annotations may use them.
        - Names inside `Literal[...]` are values, not references, and are not checked.
        - A module containing a wildcard import skips UNDEFINED_NAME (its names are unknowable).
        - Only the outermost `|` of a chain is examined, so `a | b | c` yields at most one finding.

    Args:
        source: Module source text.
        rel_path: Path reported in findings.
    """

    def __init__(self, source: str, rel_path: str) -> None:
        """Parse `source` and prepare the module scope; call `run()` to collect findings."""
        self.rel_path: str = rel_path
        self.tree: ast.Module = ast.parse(source)
        self.findings: List[AnnotationFinding] = []
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
        # One entry per enclosing scope: (kind, name, names bound there); kind is module/class/function.
        self.scopes: List[Tuple[str, str, Set[str]]] = [
            ("module", "<module>", self._bound_names(self.tree.body)),
        ]

    def run(self) -> "StaticAnnotationAudit":
        """Visit the whole module and return self (findings on `self.findings`)."""
        self.visit(self.tree)
        return self

    # --- scope bookkeeping ---------------------------------------------------------------------

    def _bound_names(self, body: Iterable[ast.stmt]) -> Set[str]:
        """
        Return every name a statement block binds at its own level.

        Contract:
            Recurses into if/while/for/with/try/match blocks (not into nested def/class bodies).
            Imports, def/class names, (annotated/augmented) assignment and for/with targets, walrus
            targets, exception names, `type` aliases and `global`/`nonlocal` declarations all bind.
        """
        names: Set[str] = set()
        stack: List[ast.AST] = list(body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names.update(
                    alias.asname or alias.name.split(".")[0]
                    for alias in node.names
                    if alias.name != "*"
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.TypeAlias):
                names.update(self._target_names(node.name))
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    names.update(self._target_names(target))
                names.update(self._walrus_names(node))
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                names.update(self._target_names(node.target))
                stack.extend(node.body + node.orelse)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        names.update(self._target_names(item.optional_vars))
                stack.extend(node.body)
            elif isinstance(node, (ast.If, ast.While)):
                stack.extend(node.body + node.orelse)
            elif isinstance(node, (ast.Try, ast.TryStar)):
                stack.extend(node.body + node.orelse + node.finalbody)
                for handler in node.handlers:
                    if handler.name:
                        names.add(handler.name)
                    stack.extend(handler.body)
            elif isinstance(node, ast.Match):
                for case in node.cases:
                    stack.extend(case.body)
                    names.update(
                        pattern.name
                        for pattern in ast.walk(case.pattern)
                        if isinstance(pattern, ast.MatchAs) and pattern.name
                    )
            elif isinstance(node, (ast.Global, ast.Nonlocal)):
                names.update(node.names)
            elif isinstance(node, ast.Expr):
                names.update(self._walrus_names(node))
        return names

    @staticmethod
    def _target_names(target: ast.AST) -> Set[str]:
        """Return the plain names an assignment target binds (tuple, list and starred included)."""
        return {node.id for node in ast.walk(target) if isinstance(node, ast.Name)}

    @staticmethod
    def _walrus_names(node: ast.AST) -> Set[str]:
        """Return names bound by `:=` anywhere inside one statement."""
        return {
            inner.target.id
            for inner in ast.walk(node)
            if isinstance(inner, ast.NamedExpr) and isinstance(inner.target, ast.Name)
        }

    @staticmethod
    def _type_param_names(node: ast.AST) -> Set[str]:
        """Return the PEP 695 type parameter names declared on a def, class or `type` statement."""
        return {param.name for param in node.type_params}

    def _function_bindings(self, node: ast.AST) -> Set[str]:
        """Return a function's parameters, type parameters and body-level bindings."""
        args = node.args
        names = {arg.arg for arg in args.posonlyargs + args.args + args.kwonlyargs}
        for special in (args.vararg, args.kwarg):
            if special is not None:
                names.add(special.arg)
        return names | self._type_param_names(node) | self._bound_names(node.body)

    def _owner(self, leaf: str) -> str:
        """Return the dotted owner path (enclosing classes/functions, then `leaf`)."""
        parts = [name for kind, name, _ in self.scopes if kind != "module"]
        return ".".join(parts + [leaf])

    def _visible_names(self, extra: Set[str]) -> Set[str]:
        """Return the names visible to an annotation evaluated in the current scope chain."""
        names: Set[str] = set(self.builtin_names) | extra
        for _, _, bound in self.scopes:
            names |= bound
        return names

    # --- visitors ------------------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Enter a class scope and visit its body."""
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
        """Check parameter/return annotations (enclosing scopes plus type parameters are visible)."""
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
            self._check_annotation(node.annotation, self._owner(ast.unparse(node.target)), set())
        if node.value is not None:
            self.visit(node.value)

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        """Check a `type X = ...` value (evaluated lazily through `__value__`)."""
        self._check_annotation(node.value, self._owner(ast.unparse(node.name)), self._type_param_names(node))

    # --- checks --------------------------------------------------------------------------------

    def _check_annotation(self, annotation: ast.expr, owner: str, extra_names: Set[str]) -> None:
        """Check one annotation expression, and the parsed text of a string annotation."""
        self._check_expression(annotation, owner, extra_names, in_string=False, anchor=annotation)
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            self.quoted_annotations += 1
            try:
                inner = ast.parse(annotation.value, mode="eval").body
            except SyntaxError:
                self._add("UNPARSEABLE_STRING", annotation, owner, repr(annotation.value))
                return
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
            anchor: ast.expr,
    ) -> None:
        """
        Report string operands of `|` and undefined names inside one expression.

        Contract:
            Findings inside a string annotation are reported at the string's line (`anchor`), since
            the parsed text carries no file positions of its own.
        """
        suffix = " (inside a string annotation)" if in_string else ""
        literal_nodes = self._literal_node_ids(expression)
        inner_unions = {
            id(child)
            for node in ast.walk(expression)
            if self._is_union(node)
            for child in (node.left, node.right)
            if self._is_union(child)
        }
        for node in ast.walk(expression):
            if not self._is_union(node) or id(node) in inner_unions:
                continue
            if not in_string:
                self.pep604_unions += 1
            if any(isinstance(op, ast.Constant) and isinstance(op.value, str) for op in self._union_operands(node)):
                self._add("STRING_IN_UNION", anchor if in_string else node, owner, ast.unparse(node) + suffix)
        if self.has_wildcard_import:
            return
        visible = self._visible_names(extra_names)
        for node in ast.walk(expression):
            if (
                    isinstance(node, ast.Name)
                    and isinstance(node.ctx, ast.Load)
                    and id(node) not in literal_nodes
                    and node.id not in visible
            ):
                self._add("UNDEFINED_NAME", anchor if in_string else node, owner, node.id + suffix)

    @staticmethod
    def _is_union(node: ast.AST) -> bool:
        """Return whether `node` is a `|` operation."""
        return isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr)

    @staticmethod
    def _union_operands(node: ast.BinOp) -> List[ast.expr]:
        """Return the operands of one `|` chain, flattening nested `|` on either side."""
        operands: List[ast.expr] = []
        stack: List[ast.expr] = [node]
        while stack:
            current = stack.pop()
            if StaticAnnotationAudit._is_union(current):
                stack.extend((current.left, current.right))
            else:
                operands.append(current)
        return operands

    @staticmethod
    def _literal_node_ids(expression: ast.expr) -> Set[int]:
        """Return ids of the nodes inside `Literal[...]` subscripts (values, not name references)."""
        ids: Set[int] = set()
        for node in ast.walk(expression):
            if not isinstance(node, ast.Subscript):
                continue
            base = node.value
            is_literal = (
                    (isinstance(base, ast.Name) and base.id == "Literal")
                    or (isinstance(base, ast.Attribute) and base.attr == "Literal")
            )
            if is_literal:
                ids.update(id(inner) for inner in ast.walk(node.slice))
        return ids

    def _add(self, kind: str, node: ast.expr, owner: str, detail: str) -> None:
        """Record one finding at `node`'s line."""
        self.findings.append(AnnotationFinding(kind, self.rel_path, node.lineno, owner, detail))
#endregion


#region DynamicAnnotationAudit


class DynamicAnnotationAudit:
    """
    Import a package, bind each module's TYPE_CHECKING imports, and evaluate every annotation.

    Contract:
        - Mutates the imported modules' globals (adds the TYPE_CHECKING names they lack); run it only
          in a throwaway process.
        - Owners evaluated: each module, every class it defines (nested classes included), module
          functions, and each class's methods, static/class methods and property accessors.
        - A VALUE-format read that raises is an EVAL_ERROR. With TYPE_CHECKING names bound, a NameError
          means the name is undefined even for a type checker.
        - A module that fails to import is an IMPORT_ERROR; a TYPE_CHECKING import that fails to
          resolve is a TC_IMPORT_ERROR.

    Args:
        src_root: Directory containing the package directory.
        package: Top-level package name.
    """

    def __init__(self, src_root: pathlib.Path, package: str) -> None:
        """Remember the tree to import; call `run()` to collect findings."""
        self.src_root: pathlib.Path = src_root
        self.package: str = package
        self.findings: List[AnnotationFinding] = []
        self.modules: List[Tuple[pathlib.Path, Any]] = []
        self.owners_checked: int = 0
        self.type_checking_names_bound: int = 0

    def run(self) -> "DynamicAnnotationAudit":
        """Import every module, bind TYPE_CHECKING imports, then evaluate every owner."""
        sys.path.insert(0, str(self.src_root))
        for path, name in self._module_paths():
            try:
                self.modules.append((path, importlib.import_module(name)))
            except Exception as exc:
                self._record("IMPORT_ERROR", path, 1, name, f"{type(exc).__name__}: {exc}")
        for path, module in self.modules:
            self._bind_type_checking_imports(path, module)
        for path, module in self.modules:
            for owner, qualname, line in self._owners(module):
                self._evaluate(owner, qualname, path, line)
        return self

    def _module_paths(self) -> Iterator[Tuple[pathlib.Path, str]]:
        """Yield (file, dotted module name) for every `.py` file under the package."""
        for path in sorted((self.src_root / self.package).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            parts = list(path.relative_to(self.src_root).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            yield path, ".".join(parts)

    def _record(self, kind: str, path: pathlib.Path, line: int, owner: str, detail: str) -> None:
        """Append one finding with `path` made relative to the source root's parent."""
        rel = str(path.relative_to(self.src_root.parent)) if path.is_relative_to(self.src_root.parent) else str(path)
        self.findings.append(AnnotationFinding(kind, rel, line, owner, detail))

    def _bind_type_checking_imports(self, path: pathlib.Path, module: Any) -> None:
        """
        Resolve the module's own module-level `if TYPE_CHECKING:` imports and bind missing names.

        Contract:
            Uses `importlib` only (no code execution beyond importing the named modules). Names the
            module already defines are left untouched.
        """
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.If) or ast.unparse(node.test) not in ("TYPE_CHECKING", "typing.TYPE_CHECKING"):
                continue
            for stmt in node.body:
                if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    continue
                try:
                    bindings = self._resolve_import(stmt, module)
                except Exception as exc:
                    self._record(
                        "TC_IMPORT_ERROR", path, stmt.lineno, module.__name__,
                        f"{ast.unparse(stmt)} -> {type(exc).__name__}: {exc}",
                    )
                    continue
                for name, value in bindings.items():
                    if name not in module.__dict__:
                        module.__dict__[name] = value
                        self.type_checking_names_bound += 1

    @staticmethod
    def _resolve_import(stmt: ast.stmt, module: Any) -> Dict[str, Any]:
        """Return the names one import statement would bind, resolved through importlib."""
        bindings: Dict[str, Any] = {}
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                imported = importlib.import_module(alias.name)
                if alias.asname:
                    bindings[alias.asname] = imported
                else:
                    top = alias.name.split(".")[0]
                    bindings[top] = importlib.import_module(top)
            return bindings
        target = "." * stmt.level + (stmt.module or "")
        base_name = importlib.util.resolve_name(target, module.__package__) if stmt.level else target
        base = importlib.import_module(base_name)
        for alias in stmt.names:
            try:
                value = getattr(base, alias.name)
            except AttributeError:
                value = importlib.import_module(f"{base_name}.{alias.name}")
            bindings[alias.asname or alias.name] = value
        return bindings

    def _owners(self, module: Any) -> Iterator[Tuple[Any, str, int]]:
        """Yield (owner, qualname, line) for the module, its classes (recursively) and its functions."""
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
        yield cls, f"{cls.__module__}.{cls.__qualname__}", getattr(cls, "__firstlineno__", 1)
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
            source = path if inspect.ismodule(owner) else pathlib.Path(inspect.getsourcefile(owner) or path)
            self._record("EVAL_ERROR", source, line, qualname, f"{type(exc).__name__}: {exc}")
#endregion


#region AnnotationAudit


class AnnotationAudit:
    """
    Run the static and/or dynamic pass over `<src_root>/<package>` and render a report.

    Contract:
        - `static` and `dynamic` select the passes; at least one must be True.
        - `findings()` returns static findings first, then dynamic ones.
        - `report()` groups findings by kind and appends policy counts (PEP 604 unions and quoted
          annotations), which are informational, not defects.
    """

    def __init__(self, src_root: pathlib.Path, package: str, *, static: bool = True, dynamic: bool = True) -> None:
        """Remember the target and the pass selection."""
        if not static and not dynamic:
            raise ValueError("Select at least one of the static and dynamic passes.")
        self.src_root: pathlib.Path = src_root
        self.package: str = package
        self.static: bool = static
        self.dynamic: bool = dynamic
        self.static_audits: List[StaticAnnotationAudit] = []
        self.dynamic_audit: Optional[DynamicAnnotationAudit] = None

    def run(self) -> "AnnotationAudit":
        """Run the selected passes and return self."""
        if self.static:
            for path in sorted((self.src_root / self.package).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                rel = str(path.relative_to(self.src_root.parent))
                self.static_audits.append(StaticAnnotationAudit(path.read_text(encoding="utf-8"), rel).run())
        if self.dynamic:
            self.dynamic_audit = DynamicAnnotationAudit(self.src_root, self.package).run()
        return self

    def findings(self) -> List[AnnotationFinding]:
        """Return every finding from the passes that ran."""
        found = [finding for audit in self.static_audits for finding in audit.findings]
        if self.dynamic_audit is not None:
            found.extend(self.dynamic_audit.findings)
        return found

    def report(self) -> str:
        """Render the human-readable report."""
        found = self.findings()
        lines = [f"files scanned (static): {len(self.static_audits)}", f"findings: {len(found)}"]
        if self.dynamic_audit is not None:
            lines.append(
                f"dynamic: modules imported {len(self.dynamic_audit.modules)}, TYPE_CHECKING names bound "
                f"{self.dynamic_audit.type_checking_names_bound}, annotation owners evaluated "
                f"{self.dynamic_audit.owners_checked}"
            )
        kinds = ("STRING_IN_UNION", "UNDEFINED_NAME", "UNPARSEABLE_STRING", "EVAL_ERROR", "TC_IMPORT_ERROR", "IMPORT_ERROR")
        for kind in kinds:
            group = sorted((f for f in found if f.kind == kind), key=lambda f: (f.path, f.line))
            lines.append(f"\n== {kind}: {len(group)}")
            lines.extend("  " + finding.render() for finding in group)
        if self.static_audits:
            unions = sum(audit.pep604_unions for audit in self.static_audits)
            quoted = sum(audit.quoted_annotations for audit in self.static_audits)
            lines.append(f"\npolicy counts (not defects): PEP 604 unions {unions}, quoted annotations {quoted}")
        return "\n".join(lines)
#endregion


def main(argv: Optional[List[str]] = None) -> int:
    """Command-line entry point; prints the report and returns 1 when any finding exists."""
    parser = argparse.ArgumentParser(description="Locate annotations that raise when evaluated.")
    parser.add_argument("src_root", help="Directory containing the package, e.g. src")
    parser.add_argument("package", help="Top-level package name, e.g. melder")
    passes = parser.add_mutually_exclusive_group()
    passes.add_argument("--static-only", action="store_true")
    passes.add_argument("--dynamic-only", action="store_true")
    parser.add_argument("--json", help="Also write the findings to this JSON file")
    options = parser.parse_args(argv)
    audit = AnnotationAudit(
        pathlib.Path(options.src_root).resolve(),
        options.package,
        static=not options.dynamic_only,
        dynamic=not options.static_only,
    ).run()
    print(audit.report())
    if options.json:
        pathlib.Path(options.json).write_text(
            json.dumps([finding.as_dict() for finding in audit.findings()], indent=1),
            encoding="utf-8",
        )
    return 1 if audit.findings() else 0


if __name__ == "__main__":
    sys.exit(main())
