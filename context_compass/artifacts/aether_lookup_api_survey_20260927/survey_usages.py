"""
Usage survey for EPIC-2026-09-27-aether-conduit-lookup-api (melder_0).

Finds every call of the eight Aether conduit lookups and classifies the RECEIVER, because ConduitCloud,
the Nexus command systems and FrameViewer define methods with the same names. Python files are parsed
with `ast`; a Name receiver is resolved through assignments in its enclosing function (then module).
Markdown/text files use a receiver regex. Generated trees are counted, not classified.

Run from the repository root:  python context_compass/artifacts/aether_lookup_api_survey_20260927/survey_usages.py
Re-run at epic closure: the Aether rows must be empty (or match the approved compatibility aliases).
"""
import ast
import pathlib
import re
import sys
from collections import Counter, defaultdict

NAMES = ("list_conduit_ids", "list_conduit_names", "count_conduits", "has_conduit_id", "has_conduit_name",
         "find_conduit_id_by_name", "get_conduit_by_name", "get_conduit_by_id")
PY_ROOTS = ("src/melder", "tests", "benchmarks", "docs")
TEXT_ROOTS = ("docs", "UX_and_AIX_experiences", "release_docs", "agents", "README.md", "CONTRIBUTING.md",
              "context_compass/system_docs/src_components.md", "context_compass/system_docs/src_architecture.md",
              "context_compass/system_docs/tests_components.md", "context_compass/system_docs/tests_architecture.md")
GENERATED = ("docs/_build", "_readthedocs", "llm_support", "context_compass/system_docs/src_graph.md",
             "src/melder/_build_assets")
SKIP_PARTS = {"__pycache__", "__melder_cache__", "_build", ".venv_new"}
AETHER_CLASS_FILES = {"src/melder/aether/aether.py": "Aether"}


def classify_text(receiver):
    """Classify a receiver expression by its text. Order matters: Aether() before generic names."""
    r = receiver.replace(" ", "")
    if re.search(r"(^|\.)Aether\(\)$", r):
        return "aether"
    if "get_conduit_cloud()" in r or re.search(r"cloud", r, re.I):
        return "cloud"
    if re.search(r"command", r, re.I):
        return "nexus_commands"
    if re.search(r"viewer", r, re.I):
        return "viewer"
    if re.search(r"aether", r, re.I):
        return "aether?"
    return "unknown"


class Scope(ast.NodeVisitor):
    """Collect `name = <expr>` bindings per function so Name receivers can be traced one hop."""

    def __init__(self):
        self.bindings = defaultdict(dict)
        self.stack = ["<module>"]

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        for arg in node.args.args + node.args.kwonlyargs:
            self.bindings[node.name].setdefault(arg.arg, "<param>")
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name):
                self.bindings[self.stack[-1]][t.id] = ast.unparse(node.value)
        self.generic_visit(node)


def py_calls(path, rel):
    """Yield (method, line, receiver_text, enclosing, class_name) for each call of the surveyed names."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        yield ("<parse-error>", 0, str(exc), "", "")
        return
    scope = Scope()
    scope.visit(tree)
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in NAMES:
            fn, cls, p = "<module>", "", parents.get(node)
            while p is not None:
                if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn == "<module>":
                    fn = p.name
                if isinstance(p, ast.ClassDef):
                    cls = p.name
                    break
                p = parents.get(p)
            yield (node.func.attr, node.lineno, ast.unparse(node.func.value), fn, cls)


def classify_py(receiver, fn, cls, rel, scope_bindings):
    """Classify a Python receiver: self by class, Name by its binding, else by text."""
    if receiver == "self":
        return {"Aether": "aether_internal", "ConduitCloud": "cloud_internal"}.get(cls, "self:" + (cls or "?"))
    if re.fullmatch(r"[A-Za-z_]\w*", receiver):
        bound = scope_bindings.get(fn, {}).get(receiver) or scope_bindings.get("<module>", {}).get(receiver)
        if bound and bound != "<param>":
            c = classify_text(bound)
            if c != "unknown":
                return c
    return classify_text(receiver)


def iter_files(root, suffixes, skip=SKIP_PARTS):
    p = pathlib.Path(root)
    if p.is_file():
        if p.suffix in suffixes:
            yield p
        return
    for f in sorted(p.rglob("*")):
        if f.is_file() and f.suffix in suffixes and not (skip & set(f.parts)):
            yield f


def main():
    rows = []
    for root in PY_ROOTS:
        for f in iter_files(root, {".py"}):
            rel = f.as_posix()
            text = f.read_text(encoding="utf-8-sig", errors="replace")
            if not any(n in text for n in NAMES):
                continue
            tree_scope = Scope()
            try:
                tree_scope.visit(ast.parse(text))
            except SyntaxError:
                pass
            for method, line, recv, fn, cls in py_calls(f, rel):
                rows.append((rel, line, method, recv, classify_py(recv, fn, cls, rel, tree_scope.bindings), fn))
    rx = re.compile(r"([\w\.\[\]\"'\(\)]*?)\.(" + "|".join(NAMES) + r")\(")
    for root in TEXT_ROOTS:
        for f in iter_files(root, {".md", ".rst", ".txt"}):
            rel = f.as_posix()
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for m in rx.finditer(line):
                    rows.append((rel, i, m.group(2), m.group(1) or "<bare>", classify_text(m.group(1) or ""), "<text>"))
                for n in NAMES:
                    if re.search(r"(?<![\w.])" + n + r"(?![\w(])", line):
                        rows.append((rel, i, n, "<mention>", "mention", "<text>"))
    gen = Counter()
    for root in (GENERATED if "--generated" in sys.argv else ()):
        for f in iter_files(root, {".py", ".md", ".txt", ".html", ".js", ".json", ".xhtml"}, skip={"__pycache__"}):
            t = f.read_text(encoding="utf-8", errors="replace")
            gen[root] += sum(t.count(n) for n in NAMES)
    by = Counter((r[2], r[4], r[0].split("/")[0]) for r in rows)
    print("# Aether conduit lookup usage survey")
    print("## Counts: method x receiver class x top-level area")
    for (method, klass, area), n in sorted(by.items()):
        print(f"{method:24} {klass:18} {area:28} {n}")
    print("## Aether call sites (external + internal)")
    for r in sorted(rows):
        if r[4] in ("aether", "aether_internal", "aether?"):
            print(f"{r[0]}:{r[1]}  {r[2]}  recv={r[3]}  in={r[5]}  class={r[4]}")
    print("## Unknown receivers (need a read)")
    for r in sorted(rows):
        if r[4] == "unknown":
            print(f"{r[0]}:{r[1]}  {r[2]}  recv={r[3]}  in={r[5]}")
    print("## Generated trees (occurrences; pass --generated to count here, slow on the device mount)")
    for root, n in gen.items():
        print(f"{root:48} {n}")


if __name__ == "__main__":
    sys.exit(main())
