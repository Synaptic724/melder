"""For file:line sites, print the enclosing function and the `with` items that enclose the line (AST, exact)."""
import ast, sys, pathlib
def ctx(path, line):
    src = pathlib.Path(path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    best = None
    stack = []
    def visit(node, chain):
        nonlocal best
        for child in ast.iter_child_nodes(node):
            if hasattr(child, "lineno") and child.lineno <= line <= getattr(child, "end_lineno", child.lineno):
                c = chain
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    c = chain + [("def" if not isinstance(child, ast.ClassDef) else "class", child.name, child.lineno)]
                elif isinstance(child, (ast.With, ast.AsyncWith)):
                    items = ", ".join(ast.get_source_segment(src, it.context_expr) or "?" for it in child.items)
                    c = chain + [("with", items[:70], child.lineno)]
                best = c
                visit(child, c)
    visit(tree, [])
    return best or []
for arg in sys.argv[1:]:
    f, l = arg.rsplit(":", 1)
    chain = ctx(f, int(l))
    print(f"{f.split('melder/',1)[-1]}:{l}  " + " > ".join(f"{k} {n}@{ln}" for k, n, ln in chain))
