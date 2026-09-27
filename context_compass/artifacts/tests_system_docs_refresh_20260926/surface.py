import ast, sys, pathlib
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    src = p.read_text(encoding="utf-8-sig")
    tree = ast.parse(src)
    doc = ast.get_docstring(tree) or ""
    n = len(src.splitlines())
    print(f"=== {p} ({n} lines)")
    if doc:
        print("  DOC:", " ".join(doc.split())[:400])
    def walk(body, prefix=""):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                d = ast.get_docstring(node) or ""
                print(f"  {prefix}{node.name}:{node.lineno}  {' '.join(d.split())[:160]}")
            elif isinstance(node, ast.ClassDef):
                walk(node.body, prefix=node.name + ".")
            elif isinstance(node, (ast.FunctionDef,)) and any(isinstance(d, ast.Name) and d.id=="fixture" or isinstance(d, ast.Attribute) and d.attr=="fixture" or isinstance(d, ast.Call) and getattr(getattr(d,'func',None),'attr',None)=="fixture" for d in node.decorator_list):
                print(f"  FIXTURE {node.name}:{node.lineno}")
    walk(tree.body)
