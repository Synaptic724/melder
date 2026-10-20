"""Audit the applied wording edits against the code they sit in (melder_1, 2026-10-18).

For every hand edit in edits/batch*.py: confirm the new text is what the file holds now, find the innermost def or
class around it, and flag the edit for a manual read when the old line or the enclosing function names the conduit
scope tree (unique_per_conduit_lineage, the lineage root, lessers, parents, children, the lineage gates, ancestors,
clusters) or does not touch a SpellIndex at all. Module- and class-level lines are always flagged. Read-only.

Usage (from the repository root): python audit_edits.py > runs/audit_edits.txt
"""
import ast
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SI = re.compile(r"spell_index|index_id|SpellSystemState|system_state|SpellIndex|_states_by_index_id|spell_system_states")
CL = re.compile(
    r"unique_per_conduit_lineage|lineage_root|_root_conduit|root_conduit|lesser|parent|child|ConduitLineageGate|"
    r"conduit_lineage_gate|lineage_gate|ancestor|lineage_depth|cluster|scope tree|lineage tree"
)


def load(module_path: pathlib.Path) -> list:
    """Return the EDITS list of one edits module without writing bytecode."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EDITS


def scopes(tree: ast.AST) -> list:
    """Return (start, end, name, kind) for every def and class in the tree."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "def"
            out.append((node.lineno, node.end_lineno, node.name, kind, node))
    return out


def main() -> None:
    """Print one row per edit, grouped by file, with its flags."""
    rows = {}
    for module_path in sorted((HERE / "edits").glob("batch*.py")):
        for path, line, old, new in load(module_path):
            rows.setdefault(path, []).append((line, old, new, module_path.stem))
    root = HERE.parents[3]
    total = 0
    flagged = 0
    for path in sorted(rows):
        text = (root / path).read_bytes().decode("utf-8")
        lines = text.splitlines()
        tree = ast.parse(text.replace("\r\n", "\n"))
        all_scopes = scopes(tree)
        print(f"== {path}")
        delta = 0
        for line, old, new, batch in sorted(rows[path]):
            total += 1
            final = line + delta
            delta += len(new) - 1
            if new:
                in_place = lines[final - 1:final - 1 + len(new)] == list(new)
            else:
                in_place = True
            line = final
            inner = [s for s in all_scopes if s[0] <= line <= s[1]]
            inner.sort(key=lambda s: s[1] - s[0])
            if inner and inner[0][3] == "def":
                start, end, name, kind, node = inner[0]
                body = "\n".join(lines[start - 1:end])
                si, cl = len(SI.findall(body)), len(CL.findall(body))
                where = f"def {name}"
            else:
                si, cl = -1, -1
                where = f"class {inner[0][2]}" if inner else "<module>"
            old_cl = bool(CL.search(old))
            flag = "CHECK" if (si < 0 or si == 0 or cl > 0 or old_cl or not in_place) else "ok"
            flagged += flag == "CHECK"
            print(f"{line:>5} {flag:5} [{where}] si={si} cl={cl}{' OLD-CL' if old_cl else ''}"
                  f"{'' if in_place else ' NOT-IN-PLACE'} ({batch})")
            print(f"        - {old.strip()}")
            print(f"        + {' / '.join(n.strip() for n in new)}")
    print(f"total edits {total}, flagged {flagged}")


if __name__ == "__main__":
    main()
