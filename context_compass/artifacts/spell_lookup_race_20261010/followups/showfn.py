"""Print functions' source without their docstrings: showfn.py file Class.method [...]"""
import ast, sys, pathlib
path = sys.argv[1]; src = pathlib.Path(path).read_text(encoding="utf-8"); lines = src.split("\n")
tree = ast.parse(src)
def find(name):
    cls, _, meth = name.rpartition(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and (not cls or node.name == cls):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == meth:
                    return item
    return None
for name in sys.argv[2:]:
    fn = find(name)
    if fn is None:
        print(f"### {name}: not found"); continue
    skip = set()
    body0 = fn.body[0]
    if isinstance(body0, ast.Expr) and isinstance(getattr(body0, "value", None), ast.Constant) and isinstance(body0.value.value, str):
        skip = set(range(body0.lineno, body0.end_lineno + 1))
    print(f"### {name} @{fn.lineno}-{fn.end_lineno}")
    for i in range(fn.lineno, fn.end_lineno + 1):
        if i not in skip and lines[i-1].strip():
            print(f"{i}: {lines[i-1]}")
