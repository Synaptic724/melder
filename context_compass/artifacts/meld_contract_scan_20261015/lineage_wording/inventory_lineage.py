"""Inventory every occurrence of "lineage" in the repository's code and documents (melder_1, 2026-10-18).

The owner ruled (chat 2026-10-18) that a SpellIndex is not a lineage - a lineage is a conduit scope tree (a root
conduit and its lessers) - and directed that every place calling a SpellIndex a lineage be reworded. This script
only LISTS occurrences; it decides nothing and writes nothing outside its output file. Python files are tokenized,
so each occurrence is tagged by where it sits: NAME (an identifier), COMMENT, or STRING (a docstring, a message, a
literal). Other files are read line by line (TEXT).

Usage (from the repository root): python <this script> <out.jsonl>
"""
import io
import json
import pathlib
import re
import sys
import tokenize

ROOTS = [
    ("src", pathlib.Path("src/melder"), "*.py"),
    ("tests", pathlib.Path("tests"), "*.py"),
    ("ux", pathlib.Path("UX_and_AIX_experiences"), "*"),
    ("docs", pathlib.Path("docs"), "*"),
    ("system_docs", pathlib.Path("context_compass/system_docs"), "*.md"),
    ("graph", pathlib.Path("context_compass/system_docs/graph"), "*.json"),
]
FILES = [
    ("root", pathlib.Path("README.md")),
    ("root", pathlib.Path("agents/MELDER_AGENT_OPERATIONS.md")),
    ("root", pathlib.Path("release_docs/next_version_release.md")),
]
SKIP_PARTS = {"_build_assets", "__melder_cache__", "__pycache__", "_build", "patches", "graph_scratch"}
SKIP_FILES = {"src_graph.md", "src_graph_index.md"}
WORD = re.compile(r"lineage", re.IGNORECASE)


def wanted(path: pathlib.Path, tree: str) -> bool:
    """True for a file this inventory covers: no build output, caches, generated graph or index files."""
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if path.name in SKIP_FILES or path.name.endswith("_index.md"):
        return False
    if tree == "src" and "tests" in path.parts:
        return False
    if tree == "system_docs" and "graph" in path.parts:
        return False
    return path.is_file() and path.suffix in (".py", ".md", ".txt", ".toml", ".json", ".rst")


def python_hits(path: pathlib.Path, text: str):
    """Yield (line, kind, line_text) for each occurrence in a Python file, by token kind."""
    lines = text.split("\n")
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    for token in tokens:
        if not WORD.search(token.string):
            continue
        kind = tokenize.tok_name[token.type]
        if kind in ("FSTRING_MIDDLE", "FSTRING_START", "FSTRING_END", "TSTRING_MIDDLE"):
            kind = "STRING"
        start_line = token.start[0]
        for offset, piece in enumerate(token.string.split("\n")):
            for _match in WORD.finditer(piece):
                line_no = start_line + offset
                yield line_no, kind, lines[line_no - 1]


def text_hits(text: str):
    """Yield (line, kind, line_text) for each occurrence in a text file."""
    for line_no, line in enumerate(text.split("\n"), 1):
        for _match in WORD.finditer(line):
            yield line_no, "TEXT", line


def main() -> None:
    """Walk the roots and files, write one JSON line per occurrence, print counts by tree and kind."""
    out = pathlib.Path(sys.argv[1])
    targets = []
    for tree, root, pattern in ROOTS:
        for path in sorted(root.rglob(pattern)):
            if wanted(path, tree):
                targets.append((tree, path))
    targets.extend((tree, path) for tree, path in FILES if path.is_file())
    counts = {}
    with out.open("w", encoding="utf-8") as handle:
        for tree, path in targets:
            text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
            if path.suffix == ".py":
                try:
                    hits = list(python_hits(path, text))
                except (tokenize.TokenError, SyntaxError, IndentationError):
                    hits = [(n, "TEXT", l) for n, k, l in text_hits(text)]
            else:
                hits = list(text_hits(text))
            for line_no, kind, line in hits:
                handle.write(json.dumps({"tree": tree, "path": str(path), "line": line_no, "kind": kind,
                                         "text": line.strip()}) + "\n")
                counts[(tree, kind)] = counts.get((tree, kind), 0) + 1
    for (tree, kind), number in sorted(counts.items()):
        print(f"{tree:<12} {kind:<8} {number}")
    print("total", sum(counts.values()))


if __name__ == "__main__":
    main()
