"""S7: join check - every src/ path cited in src_components' Key Files (C1) lists resolves to a section of src_graph.

Run from the repository root: python s7_graph_join.py
Read-only. Prints the cited count, the resolved count and every unresolved citation with its line.
"""
import pathlib
import re

DOCS = pathlib.Path("context_compass/system_docs")
components = (DOCS / "src_components.md").read_text(encoding="utf-8").split("\n")
index = (DOCS / "src_graph_index.md").read_text(encoding="utf-8")
sources = set(re.findall(r"\|\s*`?(src/[^|`\s]+\.py)`?\s*\|", index))
cited = []
in_key_files = False
for number, line in enumerate(components, 1):
    stripped = line.strip()
    if stripped.startswith("Key Files (C1)"):
        # The list follows the label: "- `src/...`" items up to the first blank or non-item line.
        in_key_files = True
        cited.extend((number, m) for m in re.findall(r"(src/[A-Za-z0-9_/]+\.py)", line))
        continue
    if in_key_files:
        if not stripped.startswith("- "):
            in_key_files = False
            continue
        cited.extend((number, m) for m in re.findall(r"(src/[A-Za-z0-9_/]+\.py)", line))
unresolved = [(n, p) for n, p in cited if p not in sources]
print(f"graph index sources: {len(sources)}; Key Files citations: {len(cited)} ({len({p for _, p in cited})} distinct); "
      f"unresolved: {len(unresolved)}")
for n, p in unresolved:
    print(f"  UNRESOLVED src_components.md:{n} {p}")
