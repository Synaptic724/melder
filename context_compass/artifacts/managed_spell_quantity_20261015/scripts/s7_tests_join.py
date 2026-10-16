"""Check the tests docs' join: the Key Files union against the C1 map, and every cited path and range.

Read-only. Run from the repository root:
    python context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_tests_join.py

Prints the size of the deduplicated union of every `Key Files (C1)` list in tests_components, the C1 map's
paths, the differences both ways, then the documents' own verification recipe (MISSING, OUT OF BOUNDS, STALE
RANGE) over tests_components and tests_architecture.
"""

import pathlib
import re


def key_files_union(text: str, root: pathlib.Path) -> set[str]:
    """Return every backticked, non-glob path in the Key Files (C1) blocks of the document.

    A token without a slash counts only when it names a file at the repository root (pyproject.toml); a
    sibling document named in prose (tests_architecture.md) is not a key file.
    """
    paths: set[str] = set()
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if "Key Files (C1):" in lines[i]:
            block = [lines[i].split("Key Files (C1):", 1)[1]]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith("#") \
                    and (lines[j].startswith("- ") or lines[j].startswith("  ")):
                block.append(lines[j])
                j += 1
            for chunk in block:
                for p in re.findall(r"`([^`]+)`", chunk):
                    if "*" in p or "?" in p:
                        continue
                    if "/" not in p and not (root / p).is_file():
                        continue
                    paths.add(p)
            i = j
        else:
            i += 1
    return paths


def map_paths(text: str) -> list[str]:
    """Return the C1 map's record paths in document order."""
    return re.findall(r"^- path: `([^`]+)`", text, re.M)


def recipe(root: pathlib.Path, doc: pathlib.Path) -> None:
    """The documents' own check: cited paths exist, ranges in bounds, C1 end_line current."""
    cite = re.compile(r"`?((?:tests|src)/[A-Za-z0-9_/.]*\.py):(\d+)(?:\s*-\s*(\d+))?`?")
    path_re = re.compile(r"`((?:tests|src)/[^`]+\.py)`")
    text = doc.read_text(encoding="utf-8")
    for i, line in enumerate(text.split("\n"), 1):
        for p in path_re.findall(line):
            if "*" in p or "?" in p:
                continue
            if not (root / p).exists():
                print("MISSING", doc.name, i, p)
        for m in cite.finditer(line):
            f = root / m.group(1)
            if not f.exists():
                continue
            n = len(f.read_bytes().decode("utf-8", "replace").splitlines())
            s = int(m.group(2))
            e = int(m.group(3) or m.group(2))
            if s < 1 or e > n or s > e:
                print("OUT OF BOUNDS", doc.name, i, m.group(0), "file has", n)
    cur = None
    for i, line in enumerate(text.split("\n"), 1):
        m = re.match(r"^- path: `([^`]+)`", line)
        if m:
            cur = m.group(1)
            continue
        if cur:
            m2 = re.match(r"^\s+end_line:\s*(\d+)", line)
            if m2:
                f = root / cur
                if f.exists():
                    n = len(f.read_bytes().decode("utf-8", "replace").splitlines())
                    if int(m2.group(1)) != n:
                        print("STALE RANGE", doc.name, i, cur, m2.group(1), "->", n)
                else:
                    print("MISSING RECORD", doc.name, i, cur)
                cur = None


def main() -> None:
    """Print the join report."""
    root = pathlib.Path.cwd()
    tc = root / "context_compass/system_docs/tests_components.md"
    ta = root / "context_compass/system_docs/tests_architecture.md"
    text = tc.read_text(encoding="utf-8")
    union = key_files_union(text, root)
    mapped = map_paths(text)
    print(f"key files union: {len(union)}; C1 records: {len(mapped)} ({len(set(mapped))} distinct)")
    for p in sorted(union - set(mapped)):
        print("IN UNION, NO RECORD:", p)
    for p in sorted(set(mapped) - union):
        print("RECORD, NOT IN UNION:", p)
    dupes = sorted({p for p in mapped if mapped.count(p) > 1})
    for p in dupes:
        print("DUPLICATE RECORD:", p)
    for p in sorted(union):
        if not (root / p).exists():
            print("KEY FILE MISSING ON DISK:", p)
    recipe(root, tc)
    recipe(root, ta)


if __name__ == "__main__":
    main()
