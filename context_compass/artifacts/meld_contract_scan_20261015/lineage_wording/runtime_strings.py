# Lists "lineage" in f-string text and in string literals that are not docstrings (runtime messages, keys, slot names).
# melder_1 (synaptic_python_developer), 2026-10-18. Read-only. Usage: python runtime_strings.py <path.py> [...]
import io, re, sys, tokenize, ast
# Lists "lineage" inside f-string text and non-docstring string literals (runtime messages, keys) per file.
for path in sys.argv[1:]:
    src = open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    tree = ast.parse(src)
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
                for ln in range(body[0].lineno, body[0].end_lineno + 1):
                    doc_lines.add(ln)
    out = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        kind = tokenize.tok_name[t.type]
        if kind in ("FSTRING_MIDDLE", "STRING") and re.search("lineage", t.string, re.I):
            if t.start[0] in doc_lines:
                continue
            out.append((t.start[0], kind, t.string.strip()[:110]))
    for ln, kind, s in out:
        print(f"{path}:{ln}: [{kind}] {s}")
