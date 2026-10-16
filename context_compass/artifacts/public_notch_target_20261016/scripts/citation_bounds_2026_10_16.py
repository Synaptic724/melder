"""The citation-bounds recipe from src_architecture's `## Indexing` section, verbatim, saved for the 0.2.8249
rubric pass (melder_0, 2026-10-16). Run from the documentation root (context_compass/). In-bounds is necessary,
not sufficient: it proves every `path:line` citation in the two src documents points inside an existing file."""
import pathlib, re
CITE = re.compile(r"`?([a-z][A-Za-z0-9_/.]*\.py):(\d+)(?:\s*-\s*(\d+))?`?")
# Cited source paths are relative to the SOURCE-TREE root, which is not
# necessarily the directory you run this from. Walk up until `src/` appears, so
# the check works from the documentation root or the repository root.
here = pathlib.Path.cwd().resolve()
root = next((p for p in (here, *here.parents) if (p / "src").is_dir()), here)
docs = next(p for p in (pathlib.Path("system_docs"), pathlib.Path("."))
            if list(p.glob("src_*.md")))
for doc in docs.glob("src_*.md"):
    if doc.name.endswith("_index.md"):
        continue
    for i, line in enumerate(doc.read_text(encoding="utf-8").split("\n"), 1):
        for m in CITE.finditer(line):
            f = root / m.group(1)
            if not f.exists():
                print("MISSING", doc.name, i, m.group(0)); continue
            n = len(f.read_bytes().decode("utf-8", "replace").splitlines())
            s = int(m.group(2)); e = int(m.group(3) or m.group(2))
            if s < 1 or e > n or s > e:
                print("OUT OF BOUNDS", doc.name, i, m.group(0), "file has", n)
print("done")
