"""
Object composition scanner: what shapes does a real codebase actually build?

WHY THIS EXISTS
    The PGO composition experiment (`pgo_codegen_composition_experiment.py`) measured
    what an ideal profile-guided body saves per creation for synthetic shapes: a
    constant ~183 ns door (3 Python calls) plus ~45 ns per singleton dependency read
    and ~20 ns per transient site. Whether that is worth building depends on the
    shapes real code composes: how many constructor collaborators a class takes
    (width), how deep construction trees go (depth), and how big a whole tree is.

    This tool reads a package's source with `ast` - no import, no side effects - and
    reports those distributions for every class, plus the ceiling the experiment's
    model puts on each width bucket. Run it on Melder itself first, because Melder is
    the largest body of dependency-composed code at hand.

WHAT IT MEASURES
    For every `class` in the package:
      width      constructor parameters whose annotation names another class of the
                 package (an object collaborator), counting `Optional[X]`, `Union[X, Y]`
                 and `List[X]` / `Sequence[X]` as collaborators of X (and Y)
      plain      constructor parameters that are data (str, int, bool, mappings, callables,
                 typing-only names, stdlib types) - not injected objects
      depth      longest chain of collaborators below the class (cycles cut)
      tree       distinct classes reachable through collaborators (the objects a full
                 construction of the class touches at most)
      mro        inheritance depth inside the package (bases resolved by simple name)
    Distributions are reported as histograms; the widest classes, the deepest chains
    and the largest trees are listed.

ESTIMATE
    Per width bucket, the ceiling an ideal PGO body wins per creation from the
    experiment's model: door 183 ns + 45 ns per collaborator if every collaborator is
    a stored singleton, 183 + 20 ns per collaborator if every one is a transient site.
    Constructors themselves are never removed.

RUN
    python tests/experimentation/pgo_composition_scanner.py [package_root] [--top N]
    default package root: src/melder relative to the repository root.
"""

import ast
import os
import sys
from collections import Counter
from typing import ClassVar, Dict, List, Optional, Set, Tuple


class ScanSettings:
    """Command-line settings: the package root to scan and how many rows to list."""

    __slots__ = ("root", "top")

    DEFAULT_ROOT: ClassVar[str] = os.path.join("src", "melder")
    DEFAULT_TOP: ClassVar[int] = 15

    def __init__(self, argv: List[str]) -> None:
        args = [arg for arg in argv if not arg.startswith("--")]
        self.root: str = args[0] if args else self.DEFAULT_ROOT
        self.top: int = self.DEFAULT_TOP
        if "--top" in argv:
            self.top = int(argv[argv.index("--top") + 1])


class ClassRecord:
    """One scanned class: where it is, what its constructor takes, what it extends."""

    __slots__ = ("name", "module", "bases", "collaborators", "plain", "init_params", "has_init")

    def __init__(self, name: str, module: str, bases: List[str]) -> None:
        self.name: str = name
        self.module: str = module
        self.bases: List[str] = bases
        self.collaborators: List[str] = []
        self.plain: List[str] = []
        self.init_params: int = 0
        self.has_init: bool = False


class AnnotationNames:
    """
    Pulls the class names an annotation refers to.

    Contract:
        - `Optional[X]`, `Union[X, Y]`, `List[X]`, `Sequence[X]`, `Tuple[X, ...]`,
          `Iterable[X]`, `Dict[K, V]` and string annotations are unwrapped; every
          `Name` or attribute tail found is returned.
        - The caller decides which names are package classes.
    """

    __slots__ = ()

    @staticmethod
    def of(node: Optional[ast.AST]) -> List[str]:
        """Return every bare name inside `node`, in source order."""
        if node is None:
            return []
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                node = ast.parse(node.value, mode="eval").body
            except SyntaxError:
                return []
        names: List[str] = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                names.append(sub.id)
            elif isinstance(sub, ast.Attribute):
                names.append(sub.attr)
        return names


class PackageScanner:
    """
    Walks a package root, parses every module, and builds the composition graph.

    Contract:
        - Parse errors are reported and the module skipped; nothing is imported.
        - Class names are matched by simple name; a duplicate simple name across
          modules is counted once as a collaborator target (reported in `duplicates`).
    """

    __slots__ = ("root", "records", "class_names", "duplicates", "skipped")

    def __init__(self, root: str) -> None:
        self.root: str = root
        self.records: Dict[str, ClassRecord] = {}
        self.class_names: Set[str] = set()
        self.duplicates: Counter = Counter()
        self.skipped: List[str] = []

    def scan(self) -> None:
        """Parse every `.py` under the root; two passes so collaborators resolve."""
        modules: List[Tuple[str, ast.Module]] = []
        for directory, _dirs, files in os.walk(self.root):
            if "__pycache__" in directory or "__melder_cache__" in directory or "_build_assets" in directory:
                continue
            for filename in sorted(files):
                if not filename.endswith(".py"):
                    continue
                path = os.path.join(directory, filename)
                try:
                    with open(path, "rb") as handle:
                        tree = ast.parse(handle.read(), filename=path)
                except SyntaxError as error:
                    self.skipped.append(f"{path}: {error}")
                    continue
                modules.append((os.path.relpath(path, self.root), tree))
        for module, tree in modules:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.duplicates[node.name] += 1
                    self.class_names.add(node.name)
        for module, tree in modules:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._record(module, node)

    def _record(self, module: str, node: ast.ClassDef) -> None:
        """Build the `ClassRecord` for one class definition."""
        bases = [name for base in node.bases for name in AnnotationNames.of(base)[-1:]]
        record = ClassRecord(node.name, module, bases)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                record.has_init = True
                params = item.args.args[1:] + item.args.kwonlyargs
                record.init_params = len(params)
                for param in params:
                    referenced = [n for n in AnnotationNames.of(param.annotation) if n in self.class_names]
                    if referenced:
                        record.collaborators.extend(dict.fromkeys(referenced))
                    else:
                        record.plain.append(param.arg)
                break
        self.records.setdefault(node.name, record)

    def depth_and_tree(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Longest collaborator chain and reachable-class count per class (cycles cut)."""
        depth: Dict[str, int] = {}
        tree: Dict[str, int] = {}

        def walk_depth(name: str, visiting: Set[str]) -> int:
            if name in depth:
                return depth[name]
            if name in visiting or name not in self.records:
                return 0
            visiting.add(name)
            best = 0
            for dep in self.records[name].collaborators:
                best = max(best, 1 + walk_depth(dep, visiting))
            visiting.discard(name)
            depth[name] = best
            return best

        def walk_tree(name: str) -> int:
            if name in tree:
                return tree[name]
            seen: Set[str] = set()
            stack = list(self.records[name].collaborators)
            while stack:
                dep = stack.pop()
                if dep in seen or dep not in self.records:
                    continue
                seen.add(dep)
                stack.extend(self.records[dep].collaborators)
            tree[name] = len(seen)
            return tree[name]

        for name in self.records:
            walk_depth(name, set())
            walk_tree(name)
        return depth, tree

    def mro_depth(self) -> Dict[str, int]:
        """Inheritance depth inside the package, by simple base names (cycles cut)."""
        memo: Dict[str, int] = {}

        def walk(name: str, visiting: Set[str]) -> int:
            if name in memo:
                return memo[name]
            if name in visiting or name not in self.records:
                return 0
            visiting.add(name)
            best = 0
            for base in self.records[name].bases:
                best = max(best, 1 + walk(base, visiting))
            visiting.discard(name)
            memo[name] = best
            return best

        for name in self.records:
            walk(name, set())
        return memo


class Report:
    """Renders the distributions, the top lists and the ceiling estimate as Markdown."""

    __slots__ = ()

    WIDTH_BUCKETS: ClassVar[List[Tuple[str, int, int]]] = [
        ("0", 0, 0), ("1", 1, 1), ("2", 2, 2), ("3-4", 3, 4), ("5-8", 5, 8), ("9-16", 9, 16), ("17+", 17, 10**6),
    ]
    DOOR_NS: ClassVar[int] = 183
    SINGLETON_NS: ClassVar[int] = 45
    TRANSIENT_NS: ClassVar[int] = 20

    @staticmethod
    def bucket(value: int, buckets: List[Tuple[str, int, int]]) -> str:
        """Return the label of the bucket holding `value`."""
        for label, low, high in buckets:
            if low <= value <= high:
                return label
        return buckets[-1][0]

    @staticmethod
    def render(scanner: PackageScanner, settings: ScanSettings) -> str:
        """Build the whole report."""
        records = scanner.records
        depth, tree = scanner.depth_and_tree()
        mro = scanner.mro_depth()
        with_init = [r for r in records.values() if r.has_init]
        composed = [r for r in with_init if r.collaborators]
        lines: List[str] = []
        lines.append(f"# Object composition of `{scanner.root}`\n")
        lines.append(f"classes {len(records)}; with `__init__` {len(with_init)}; taking at least one package-class "
                     f"collaborator {len(composed)} ({100 * len(composed) / max(1, len(with_init)):.0f}% of those with an "
                     f"`__init__`); duplicate simple names {sum(1 for c in scanner.duplicates.values() if c > 1)}; "
                     f"modules skipped {len(scanner.skipped)}\n")
        total_params = sum(r.init_params for r in with_init)
        total_collab = sum(len(r.collaborators) for r in with_init)
        lines.append(f"constructor parameters {total_params}, of which object collaborators {total_collab} "
                     f"({100 * total_collab / max(1, total_params):.0f}%) and plain data {total_params - total_collab}\n")

        lines.append("## Width: object collaborators per constructor (classes with an `__init__`)\n")
        lines.append("| width | classes | share | ceiling if all singletons | ceiling if all transient |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        width_counts = Counter(Report.bucket(len(r.collaborators), Report.WIDTH_BUCKETS) for r in with_init)
        for label, low, high in Report.WIDTH_BUCKETS:
            count = width_counts.get(label, 0)
            mid = low if low == high else (low + min(high, 24)) // 2
            lines.append(f"| {label} | {count} | {100 * count / max(1, len(with_init)):.0f}% | "
                         f"{Report.DOOR_NS + Report.SINGLETON_NS * mid} ns | {Report.DOOR_NS + Report.TRANSIENT_NS * mid} ns |")
        lines.append("")

        lines.append("## Depth: longest collaborator chain below a class\n")
        depth_counts = Counter(depth[r.name] for r in with_init)
        lines.append("| depth | classes |")
        lines.append("| --- | ---: |")
        for value in sorted(depth_counts):
            lines.append(f"| {value} | {depth_counts[value]} |")
        lines.append("")

        lines.append("## Tree: distinct classes reachable through collaborators\n")
        tree_buckets: List[Tuple[str, int, int]] = [("0", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5), ("6-10", 6, 10), ("11-20", 11, 20), ("21-50", 21, 50), ("51+", 51, 10**6)]
        tree_counts = Counter(Report.bucket(tree[r.name], tree_buckets) for r in with_init)
        lines.append("| reachable classes | classes |")
        lines.append("| --- | ---: |")
        for label, _low, _high in tree_buckets:
            lines.append(f"| {label} | {tree_counts.get(label, 0)} |")
        lines.append("")

        lines.append("## Inheritance depth inside the package (MRO minus object and external bases)\n")
        mro_counts = Counter(mro[r.name] for r in records.values())
        lines.append("| depth | classes |")
        lines.append("| --- | ---: |")
        for value in sorted(mro_counts):
            lines.append(f"| {value} | {mro_counts[value]} |")
        lines.append("")

        top = settings.top
        lines.append(f"## Widest constructors (top {top})\n")
        lines.append("| class | width | plain | module | collaborators |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        for r in sorted(composed, key=lambda rec: -len(rec.collaborators))[:top]:
            lines.append(f"| {r.name} | {len(r.collaborators)} | {len(r.plain)} | {r.module} | {', '.join(r.collaborators)} |")
        lines.append("")
        lines.append(f"## Deepest chains (top {top})\n")
        lines.append("| class | depth | tree | module |")
        lines.append("| --- | ---: | ---: | --- |")
        for r in sorted(composed, key=lambda rec: (-depth[rec.name], -tree[rec.name]))[:top]:
            lines.append(f"| {r.name} | {depth[r.name]} | {tree[r.name]} | {r.module} |")
        lines.append("")
        lines.append(f"## Largest trees (top {top})\n")
        lines.append("| class | tree | width | depth | module |")
        lines.append("| --- | ---: | ---: | ---: | --- |")
        for r in sorted(composed, key=lambda rec: -tree[rec.name])[:top]:
            lines.append(f"| {r.name} | {tree[r.name]} | {len(r.collaborators)} | {depth[r.name]} | {r.module} |")
        lines.append("")
        if scanner.skipped:
            lines.append("## Skipped modules\n")
            lines.extend(f"- {entry}" for entry in scanner.skipped)
            lines.append("")
        return "\n".join(lines)


def main(argv: List[str]) -> int:
    """Scan the package and print the report."""
    settings = ScanSettings(argv)
    if not os.path.isdir(settings.root):
        print(f"not a directory: {settings.root}", file=sys.stderr)
        return 2
    scanner = PackageScanner(settings.root)
    scanner.scan()
    print(Report.render(scanner, settings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
