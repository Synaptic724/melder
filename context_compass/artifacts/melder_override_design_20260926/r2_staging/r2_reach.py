"""R2 reachability: which top-level symbols of candidate modules does live code still reach?

Usage: python r2_reach.py <tree_root> <candidate_module> [<candidate_module> ...]

Static and conservative (keeps more than needed, never less): live modules are those reachable by static
imports (module- or function-level) from the `melder` package; every top-level symbol of a live
non-candidate module is a root (so dead code outside the candidates still counts as a user); edges follow
Name references resolved through each module's import table and same-module top-level names, plus
`alias.attr` references to imported modules. Prints, per candidate, the reachable and unreachable symbols
and which live non-candidate modules import it. Excludes _build_assets (generated manifests only name
classes).
"""

import ast
import pathlib
import sys
from typing import Dict, List, Set, Tuple

Symbol = Tuple[str, str]


def module_name(root: pathlib.Path, path: pathlib.Path) -> str:
    """Dotted module name for a file under src/."""
    rel = path.relative_to(root / "src").with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def resolve_from(module: str, is_package: bool, level: int, target: str) -> str:
    """Resolve a relative `from` import."""
    if level == 0:
        return target
    base = module.split(".")
    if not is_package:
        base = base[:-1]
    base = base[: len(base) - (level - 1)]
    return ".".join(base + ([target] if target else []))


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    candidates = set(sys.argv[2:])
    files: Dict[str, pathlib.Path] = {}
    for path in (root / "src" / "melder").rglob("*.py"):
        if "_build_assets" in path.parts or "__pycache__" in path.parts:
            continue
        files[module_name(root, path)] = path
    trees = {name: ast.parse(path.read_text(encoding="utf-8")) for name, path in files.items()}
    imports: Dict[str, Set[str]] = {}
    alias_table: Dict[str, Dict[str, Symbol]] = {}
    module_alias: Dict[str, Dict[str, str]] = {}
    top: Dict[str, Dict[str, ast.AST]] = {}
    for name, tree in trees.items():
        is_package = files[name].name == "__init__.py"
        imports[name] = set()
        alias_table[name] = {}
        module_alias[name] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    imports[name].add(a.name)
                    module_alias[name][(a.asname or a.name).split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom):
                base = resolve_from(name, is_package, node.level, node.module or "")
                imports[name].add(base)
                for a in node.names:
                    full = f"{base}.{a.name}"
                    if full in files:
                        imports[name].add(full)
                        module_alias[name][a.asname or a.name] = full
                    else:
                        alias_table[name][a.asname or a.name] = (base, a.name)
        top[name] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                top[name][node.name] = node
            if isinstance(node, ast.ClassDef) and name in candidates:
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        top[name][f"{node.name}.{member.name}"] = member
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        top[name][t.id] = node
    live: Set[str] = set()
    stack = ["melder"]
    while stack:
        mod = stack.pop()
        if mod in live or mod not in files:
            continue
        live.add(mod)
        parts = mod.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[:i])
            if parent in files and parent not in live:
                stack.append(parent)
        stack.extend(m for m in imports.get(mod, ()) if m in files)

    def follow(sym: Symbol) -> Symbol:
        """Follow re-export chains (`from X import Y as Z` in the target module) to the defining module."""
        seen = set()
        while sym not in seen:
            seen.add(sym)
            mod, name = sym
            if mod in top and name in top[mod]:
                return sym
            if mod in alias_table and name in alias_table[mod]:
                sym = alias_table[mod][name]
                continue
            return sym
        return sym

    def refs(mod: str, node: ast.AST) -> Set[Symbol]:
        return {follow(sym) for sym in _refs(mod, node)}

    def _refs(mod: str, node: ast.AST) -> Set[Symbol]:
        out: Set[Symbol] = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if sub.id in top[mod]:
                    out.add((mod, sub.id))
                elif sub.id in alias_table[mod]:
                    out.add(alias_table[mod][sub.id])
            elif isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name):
                target = module_alias[mod].get(sub.value.id)
                if target:
                    out.add((target, sub.attr))
        return out

    reached: Set[Symbol] = set()
    work: List[Symbol] = []
    for mod in live:
        if mod in candidates:
            continue
        for sym in top[mod]:
            work.append((mod, sym))
        # module-level statements that are not defs also reference names
        for node in trees[mod].body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                work.extend(refs(mod, node))
    def class_shell_refs(mod: str, node: ast.ClassDef) -> Set[Symbol]:
        out: Set[Symbol] = set()
        for part in node.bases + node.keywords + node.decorator_list:
            out |= refs(mod, part)
        for member in node.body:
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out |= refs(mod, member)
        return out

    attr_names: Set[str] = set()
    # R2_DEAD="module:Class.method,..." marks methods verified dead by reading (never instantiated classes).
    import os
    dead = {tuple(item.split(":", 1)) for item in os.environ.get("R2_DEAD", "").split(",") if item}
    reached |= dead
    while True:
        while work:
            sym = work.pop()
            if sym in reached:
                continue
            reached.add(sym)
            mod, name = sym
            node = top.get(mod, {}).get(name)
            if node is None:
                continue
            if isinstance(node, ast.ClassDef) and mod in candidates:
                work.extend(class_shell_refs(mod, node))
            else:
                work.extend(refs(mod, node))
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Attribute):
                        attr_names.add(sub.attr)
        added = False
        for mod in candidates:
            for name in list(top.get(mod, {})):
                if "." not in name:
                    continue
                cls, meth = name.split(".", 1)
                if (mod, cls) in reached and (mod, name) not in reached and (
                        meth in attr_names or meth.startswith("__")):
                    work.append((mod, name))
                    added = True
        if not added:
            break
    for cand in sorted(candidates):
        if cand not in files:
            print(f"== {cand}: MISSING")
            continue
        importers = sorted(m for m in live if cand in imports[m] and m not in candidates)
        cimporters = sorted(m for m in live if cand in imports[m] and m in candidates)
        print(f"== {cand} (live module: {cand in live}; lines {len(files[cand].read_text(encoding='utf-8').splitlines())})")
        print(f"   imported by live non-candidates: {importers}")
        print(f"   imported by candidates: {cimporters}")
        live_syms = [s for s in top[cand] if (cand, s) in reached and (cand, s) not in dead]
        dead_syms = [s for s in top[cand] if (cand, s) not in reached or (cand, s) in dead]
        print(f"   REACHED ({len(live_syms)}): {live_syms}")
        print(f"   UNREACHED ({len(dead_syms)}): {dead_syms}")


if __name__ == "__main__":
    main()
