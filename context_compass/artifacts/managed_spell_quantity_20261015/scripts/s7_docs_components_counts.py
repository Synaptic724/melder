"""S7: after s7_docs_components.py - the inventory group counts, the source-list header and the handoff's code-map
sentence, measured on the edited document. Run from the repository root: python s7_docs_components_counts.py <NOW>"""
import pathlib
import re
import sys

now = sys.argv[1]
DOC = pathlib.Path("context_compass/system_docs/src_components.md")
text = DOC.read_text(encoding="utf-8")
lines = text.split("\n")


def replace_once(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, (text.count(old), old[:90])
    text = text.replace(old, new)


# Inventory group counts are counts of the listed entries (the inventory's 2026-09-26 note).
start = next(i for i, l in enumerate(lines) if l.startswith("### Full Package Inventory"))
end = next(i for i, l in enumerate(lines) if l.startswith("## Promoted Patch Detail"))
groups = [(i, re.match(r"^\*\*(.*)\*\* - (\d+) modules?$", lines[i])) for i in range(start, end)]
groups = [(i, m) for i, m in groups if m]
for gi, (i, m) in enumerate(groups):
    j = groups[gi + 1][0] if gi + 1 < len(groups) else end
    listed = sum(1 for k in range(i, j) if lines[k].startswith("- `src/"))
    if listed != int(m.group(2)):
        replace_once(lines[i] + "\n", f"**{m.group(1)}** - {listed} modules\n")
        print("group", m.group(1)[:30], m.group(2), "->", listed)

# The source list: every entry resolves now; the header carries the measured count and time.
i = next(i for i, l in enumerate(lines) if l.startswith("Primary source files (167, all resolved"))
entries = []
for line in lines[i + 1:]:
    if line.startswith("- `"):
        entries.append(line[3:line.index("`", 3)])
    elif entries and not line.strip():
        break
missing = [p for p in entries if not pathlib.Path(p).exists()]
assert not missing, missing
replace_once(lines[i] + "\n", f"Primary source files ({len(entries)}, all resolved {now}):\n")
print("sources", len(entries), "all resolve")

replace_once(
    "diagram join. The code map adds the five modules and remeasures every changed file; the inventory adds the\n"
    "modules by hand. Open for the owner: stamping versions staged before conjure (src_architecture, Failure Modes).\n",
    "diagram join. The code map adds the five modules and remeasures 26 extents (the lane's files, and four stale since\n"
    "earlier lanes: caching_system.py, validation_system.py, spell_system_states.py, general_helpers.py); the\n"
    "inventory adds the modules by hand and its group counts follow, and the source list is re-resolved (177 files).\n"
    "Open for the owner: stamping versions staged before conjure (src_architecture, Failure Modes).\n",
)
assert all(len(l) <= 120 or "src/melder" in l for l in text.split("\n") if l not in set(lines)), "long line"
DOC.write_text(text, encoding="utf-8")
print("written", len(text.split("\n")) - 1, "lines")
