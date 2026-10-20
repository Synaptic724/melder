"""Print the authored tier of graph nodes and, optionally, each node's source diff since HEAD.

Usage: python s7_graph_prose.py <descriptors> <ids file> <out file> [<HEAD src root> <src root>]

For every node id in the ids file (one per line): its role, responsibilities, owns_state,
phases and the authored edges leaving it; with the two source roots, the unified diff
(3 lines of context) of the node's own span (its AST definition, decorators included)
between HEAD and the working tree. Read-only: writes only the out file.
"""
import ast
import difflib
import json
import pathlib
import sys


def find_descriptor(root: pathlib.Path, nid: str):
    for p in root.rglob("*.json"):
        if p.name == "_package_candidates.json":
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if nid in d.get("nodes", {}):
            return p, d
    return None, None


def span(src_file: pathlib.Path, label: str):
    if not src_file.is_file():
        return []
    text = src_file.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == label:
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            return lines[start - 1:node.end_lineno]
    return []


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    ids = [l.strip() for l in pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    head_root = pathlib.Path(sys.argv[4]) if len(sys.argv) > 5 else None
    now_root = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else None
    for nid in ids:
        path, d = find_descriptor(root, nid)
        out.append("=" * 100)
        out.append(f"NODE {nid}")
        if d is None:
            out.append("  NOT FOUND")
            continue
        node = d["nodes"][nid]
        out.append(f"  descriptor: {path}")
        out.append(f"  file: {node.get('file')}  lineno: {node.get('lineno')}  kind: {node.get('kind')}")
        for field in ("include", "role", "responsibilities", "owns_state", "phases"):
            if field in node:
                out.append(f"  {field}: {json.dumps(node[field], ensure_ascii=False)}")
        for e in d.get("edges_authored", []):
            if e.get("from") == nid:
                out.append(f"  edge: {e.get('relation')} -> {e.get('to')} [{e.get('cardinality')}; "
                           f"{e.get('phase')}] why: {e.get('why', '')}")
        if head_root is not None and node.get("kind") != "module":
            rel = node["file"].split("/", 1)[1]
            label = node.get("label", nid.rsplit(".", 1)[1])
            before = span(head_root / rel, label)
            after = span(now_root / rel, label)
            diff = list(difflib.unified_diff(before, after, "HEAD", "now", n=3, lineterm=""))
            out.append(f"  span lines: HEAD {len(before)} -> now {len(after)}; diff lines {len(diff)}")
            out.extend("  | " + l for l in diff)
    pathlib.Path(sys.argv[3]).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(ids)} nodes; {len(out)} lines")


if __name__ == "__main__":
    main()
