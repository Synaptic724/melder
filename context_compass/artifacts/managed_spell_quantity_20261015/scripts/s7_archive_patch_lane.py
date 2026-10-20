"""S7 D6: record the managed patch lane's archive on the artifact board and in the live ticket sections.

The lane folder was moved first (`mv -n system_docs/patches/active/managed_spell_quantity_2026_10_15
system_docs/patches/completed/`). This script removes its 11 active artifact-board rows, adds one cleared row at the
top of the cleared region, and repoints the live Artifact Links / references in the epic and the S7 story (historical
Notes keep the paths they were written with). Every replacement is asserted exactly; nothing is written on a miss.
Run from context_compass/: python <this file> <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
ACTIVE = "system_docs/patches/active/managed_spell_quantity_2026_10_15/"
DONE = "system_docs/patches/completed/managed_spell_quantity_2026_10_15/"
EPIC = "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
CLEARED_ROW = (
    f"| {EPIC} | {DONE} | promote_to_documentation | Promoted at S7 (0.2.8246) to src_architecture, src_components, "
    "tests_components and tests_architecture with their indexes, and to the graph; the eleven patch docs (architecture, "
    "six component, four code-description) archived. | " + NOW + " |"
)

board = pathlib.Path("artifact_board.md")
text = board.read_bytes().decode("utf-8")
lines = text.split("\n")
begin_active = lines.index("<!-- BEGIN USER-DEFINED: active_artifacts -->")
end_active = lines.index("<!-- END USER-DEFINED: active_artifacts -->")
rows = [i for i in range(begin_active + 1, end_active) if f"| {ACTIVE}" in lines[i]]
assert len(rows) == 11, len(rows)
assert all(lines[i].startswith(f"| {EPIC} | {ACTIVE}") for i in rows)
assert sum(ACTIVE in line for line in lines) == 11
kept = [line for i, line in enumerate(lines) if i not in set(rows)]
begin_cleared = kept.index("<!-- BEGIN USER-DEFINED: cleared_artifacts -->")
kept.insert(begin_cleared + 1, CLEARED_ROW)
board.write_bytes("\n".join(kept).encode("utf-8"))
print("artifact board: removed", len(rows), "active rows; added the cleared row")

replacements = {
    EPIC: (
        (f"- {ACTIVE} (this lane's patch docs)\n", f"- {DONE} (this lane's patch docs, archived at S7)\n"),
        (f"  - {ACTIVE} (patch docs, promoted at S7)\n", f"  - {DONE} (patch docs, promoted and archived at S7)\n"),
    ),
    "tickets/stories/2026-10-15_managed_docs_release_story.md": (
        (f"  - {ACTIVE}architecture_patch.md\n", f"  - {DONE}architecture_patch.md (archived with the lane)\n"),
    ),
}
for path, pairs in replacements.items():
    p = pathlib.Path(path)
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old)
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("repointed", path)
