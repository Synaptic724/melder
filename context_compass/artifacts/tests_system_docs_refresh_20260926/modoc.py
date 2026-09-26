import ast, sys, pathlib
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    src = p.read_text(encoding="utf-8-sig")
    tree = ast.parse(src)
    doc = ast.get_docstring(tree) or ""
    tests = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test")]
    first = ""
    if not doc and tests:
        first = " ".join((ast.get_docstring(tests[0]) or "").split())[:140]
    print(f"{p} | {len(src.splitlines())}L | {len(tests)}t | {' '.join(doc.split())[:170] or '(no module doc) ' + tests[0].name + ': ' + first if tests else ''}")
