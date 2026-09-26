import ast, sys, pathlib, collections
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    tree = ast.parse(p.read_text(encoding="utf-8-sig"))
    names = [n.name[5:] for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")]
    # keyword frequency
    words = collections.Counter(w for n in names for w in n.split("_") if len(w) > 3)
    top = ", ".join(w for w, _ in words.most_common(25))
    print(f"== {p.name} ({len(names)}t) TOP: {top}")
    print("   " + "; ".join(names)[:320])
