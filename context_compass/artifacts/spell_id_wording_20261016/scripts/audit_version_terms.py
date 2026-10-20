"""Audit every remaining "version id"-family term in the live trees, classified by where it sits.

Run from the repository root:  python audit_version_terms.py <out_file>
Terms (case-insensitive): version id / version_id / version-id / versionid (and plurals), version identifier(s),
version identity / identities. Live trees: src/ (no build-asset payloads or manifests), tests/, the four system
documents, the graph descriptors, the running release note, README.md, CONTRIBUTING.md, docs/ (no _build, no
.venv), agents/, architecture_and_design/, benchmarks/, .github/. For a .py file each hit is classified by the token
it sits in: NAME (a code identifier), STRING (a docstring or string literal) or COMMENT; other files are DOC.
"""
import io
import json
import os
import pathlib
import re
import sys
import tokenize

TERM = re.compile(r"version[ _-]?ids?\b|version identifiers?\b|version identit(?:y|ies)\b", re.IGNORECASE)
HELD = set(json.loads(pathlib.Path(
    "context_compass/artifacts/spell_id_wording_20261016/inventory/held_files.json").read_text(encoding="utf-8")))


def live_files() -> list:
    """Return the live files to scan."""
    out = []
    for path in pathlib.Path("src").rglob("*.py"):
        if not {"__pycache__", "payloads", "manifest"} & set(path.parts):
            out.append(path)
    out += [p for p in pathlib.Path("tests").rglob("*.py") if "__pycache__" not in p.parts]
    docs = pathlib.Path("context_compass/system_docs")
    out += [docs / n for n in ("src_architecture.md", "src_components.md", "tests_architecture.md",
                               "tests_components.md")]
    out += list((docs / "graph").rglob("*.json"))
    out += [pathlib.Path(p) for p in ("release_docs/next_version_release.md", "README.md", "CONTRIBUTING.md")]
    skip = {"_build", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
    for root in ("docs", "agents", "architecture_and_design", "benchmarks", ".github"):
        for folder, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".venv")]
            for name in names:
                path = pathlib.Path(folder) / name
                if path.suffix in {".md", ".py", ".toml", ".txt", ".rst", ".yml", ".yaml", ".json"}:
                    out.append(path)
    return sorted(set(out), key=str)


def py_kinds(text: str) -> dict:
    """Map (line, col) spans of NAME, STRING and COMMENT tokens; return {line: [(start, end, kind)]}."""
    spans = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            kind = {tokenize.NAME: "NAME", tokenize.STRING: "STRING", tokenize.COMMENT: "COMMENT"}.get(tok.type)
            if kind is None and tok.type == getattr(tokenize, "FSTRING_MIDDLE", -1):
                kind = "STRING"
            if kind is None:
                continue
            (sl, sc), (el, ec) = tok.start, tok.end
            for line in range(sl, el + 1):
                start = sc if line == sl else 0
                end = ec if line == el else 10 ** 6
                spans.setdefault(line, []).append((start, end, kind))
    except (tokenize.TokenError, SyntaxError) as error:
        spans[-1] = [(0, 0, "TOKENIZE_ERROR %s" % error)]
    return spans


def main() -> None:
    """Write one row per hit and a summary."""
    rows, summary = [], {}
    for path in live_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        spans = py_kinds(text) if path.suffix == ".py" else {}
        for number, line in enumerate(lines, 1):
            for match in TERM.finditer(line):
                kind = "DOC"
                if path.suffix == ".py":
                    kind = "CODE"
                    for start, end, k in spans.get(number, []):
                        if start <= match.start() < end:
                            kind = k
                            break
                held = str(path) in HELD or str(path).startswith("context_compass/system_docs/graph/")
                key = (kind, "held" if held else "free", match.group(0).lower().replace("_", " ").replace("-", " "))
                summary[key] = summary.get(key, 0) + 1
                rows.append("%-7s %-4s %s:%d | %s" % (kind, "HELD" if held else "free", path, number, line.strip()))
    out = pathlib.Path(sys.argv[1])
    body = ["%5d  %-7s %-4s %s" % (count, k[0], k[1], k[2]) for k, count in sorted(summary.items())]
    out.write_text("SUMMARY\n" + "\n".join(body) + "\n\nHITS\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print("hits:", len(rows))


if __name__ == "__main__":
    main()
