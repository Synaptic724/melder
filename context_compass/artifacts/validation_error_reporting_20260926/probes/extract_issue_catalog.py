"""List every Phase-4 SpellValidationIssue and Phase-6 SystemDiagnostic construction in src/melder.

Usage: python extract_issue_catalog.py <repo_root>  -> prints one block per construction site:
file:line, enclosing class.function, severity, code, and the message source text.
"""
import ast
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
files = sorted((root / "src/melder").rglob("*.py"))
for path in files:
    text = path.read_text(encoding="utf-8")
    if "SpellValidationIssue(" not in text and "SystemDiagnostic(" not in text:
        continue
    tree = ast.parse(text)
    stack = []

    def visit(node):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.append(node.name)
            for child in ast.iter_child_nodes(node):
                visit(child)
            stack.pop()
            return
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in ("SpellValidationIssue", "SystemDiagnostic"):
                kw = {k.arg: k.value for k in node.keywords}
                pos = node.args
                def seg(v):
                    return " ".join((ast.get_source_segment(text, v) or "?").split()) if v is not None else "-"
                if name == "SpellValidationIssue":
                    sev = kw.get("severity", pos[0] if len(pos) > 0 else None)
                    code = kw.get("code", pos[1] if len(pos) > 1 else None)
                    msg = kw.get("message", pos[2] if len(pos) > 2 else None)
                else:
                    sev = kw.get("severity"); code = kw.get("code"); msg = kw.get("message")
                rel = path.relative_to(root)
                print(f"== {rel}:{node.lineno} [{name}] {'.'.join(stack)}")
                print(f"   severity: {seg(sev)}")
                print(f"   code:     {seg(code)}")
                print(f"   message:  {seg(msg)}")
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
