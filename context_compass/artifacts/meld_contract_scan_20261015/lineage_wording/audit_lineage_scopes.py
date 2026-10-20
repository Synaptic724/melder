"""List applied edits whose innermost def/class also holds conduit-lineage code (melder_1, 2026-10-18; read-only).

Usage (from the repository root): python audit_lineage_scopes.py > runs/audit_lineage_scopes.txt
"""
import ast, pathlib, re
ROOT = pathlib.Path(".")
AUDIT = ROOT / "context_compass/artifacts/meld_contract_scan_20261015/lineage_wording/runs/audit_edits.txt"
LC = re.compile(r"ConduitLineageGate|conduit_lineage_gate|lineage_gate|_root_conduit_id|_root_creations|lineage_root|"
                r"get_lineage_root|unique_per_conduit_lineage|lesser lineage|lineage tree")
files = set((ROOT / "context_compass/artifacts/meld_contract_scan_20261015/lineage_wording/runs/lineage_code_files.txt").read_text().split())
edits = {}
cur = None
lines = AUDIT.read_text().split("\n")
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("== "):
        cur = ln[3:].strip()
    m = re.match(r"^\s+(\d+) (ok|CHECK)\s+\[", ln)
    if m and cur in files:
        old = lines[i + 1].strip()[2:]
        new = lines[i + 2].strip()[2:]
        edits.setdefault(cur, []).append((int(m.group(1)), old, new))
    i += 1
for path in sorted(edits):
    src = (ROOT / path).read_bytes().decode("utf-8")
    flines = src.splitlines()
    tree = ast.parse(src.replace("\r\n", "\n"))
    scopes = [(n.lineno, n.end_lineno, n.name, type(n).__name__) for n in ast.walk(tree)
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    for line, old, new in edits[path]:
        inner = sorted([s for s in scopes if s[0] <= line <= s[1]], key=lambda s: s[1] - s[0])
        if inner:
            s, e, name, kind = inner[0]
            # for a class-level docstring line, only scan the class docstring span, not the whole class
            if kind == "ClassDef":
                node = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.lineno == s][0]
                body0 = node.body[0]
                e = body0.end_lineno if isinstance(body0, ast.Expr) else s
        else:
            s, e, name, kind = 1, len(flines), "<module>", "Module"
        hits = [(k, flines[k - 1].strip()) for k in range(s, e + 1) if LC.search(flines[k - 1])]
        if hits:
            print(f"== {path}:{line} [{kind} {name} {s}-{e}]")
            print(f"   - {old}")
            print(f"   + {new}")
            for k, t in hits[:8]:
                print(f"     LC {k}: {t[:150]}")
