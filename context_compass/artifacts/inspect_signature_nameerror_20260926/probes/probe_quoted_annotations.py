"""Count quoted (string) annotations in Melder source, by module (AST only, nothing imported).

Usage: python probe_quoted_annotations.py <src_root>
Counts parameter, return and class-level annotations whose node is a string constant, or that
contain a string constant (e.g. Optional["Spell"]).
"""
import ast
import collections
import pathlib
import sys

root = pathlib.Path(sys.argv[1]) / "melder"
whole = nested = 0
per_module = collections.Counter()
future_modules = 0


def classify(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "whole"
    if any(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(node)):
        return "nested"
    return None


for path in sorted(root.rglob("*.py")):
    if "_build_assets" in path.parts:
        continue
    tree = ast.parse(path.read_text(encoding="utf-8"))
    if any(isinstance(n, ast.ImportFrom) and n.module == "__future__" for n in tree.body):
        future_modules += 1
    annotations = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = n.args
            for a in args.posonlyargs + args.args + args.kwonlyargs + [args.vararg, args.kwarg]:
                if a is not None and a.annotation is not None:
                    annotations.append(a.annotation)
            if n.returns is not None:
                annotations.append(n.returns)
        elif isinstance(n, ast.AnnAssign):
            annotations.append(n.annotation)
    for ann in annotations:
        kind = classify(ann)
        if kind:
            per_module[str(path.relative_to(root.parent))] += 1
            if kind == "whole":
                whole += 1
            else:
                nested += 1
print(f"quoted annotations: {whole + nested} (whole-string {whole}, quoted inside a generic {nested}) "
      f"in {len(per_module)} modules; modules with `from __future__ import annotations`: {future_modules}")
for mod, n in per_module.most_common(10):
    print(f"  {n:4d} {mod}")
