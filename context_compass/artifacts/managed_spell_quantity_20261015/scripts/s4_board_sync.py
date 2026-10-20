"""S4 turn-in: deterministic closure sync of attention_board.md and artifact_board.md; fix the epic note's range."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
BOARD = ROOT / "attention_board.md"
ARTIFACTS = ROOT / "artifact_board.md"
EPIC = ROOT / "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
STORY_DONE = ROOT / "tickets/stories/completed/2026-10-15_release_managed_spell_story.md"

board = BOARD.read_text(encoding="utf-8")
# Active row: route to S5.
start = board.index("| melder_object_pools | in_progress | validation |")
end = board.index("\n", start)
new_row = ("| melder_object_pools | ready | discovery | claude | melder_0 | none | S5: read the B7 codegen seams whole "
           "(answer U7 and U8 from source) and write the S5 component patch. | `managed_spell_quantity` built in seven "
           "stories (epic Build Specification), one notch per story, rebuild last. | Every story landed with green tests "
           "and the owner accepts, or the owner redirects. | tickets/stories/2026-10-15_managed_dispense_codegen_story.md "
           f"| {NOW} | REQUIRED |")
board = board[:start] + new_row + board[end:]
# Detail entry.
old_detail = """    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md
    - tickets/stories/2026-10-15_release_managed_spell_story.md
"""
new_detail = """    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md
    - tickets/stories/2026-10-15_managed_dispense_codegen_story.md
"""
assert board.count(old_detail) == 1, "detail"
board = board.replace(old_detail, new_detail)
# Closed anchors: drop the oldest (top) row, add S4.
region_start = board.index("<!-- BEGIN USER-DEFINED: closed_anchors -->\n") + len("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")
region_end = board.index("<!-- END USER-DEFINED: closed_anchors -->")
rows = [row for row in board[region_start:region_end].splitlines() if row.startswith("| ")]
assert len(rows) == 12, len(rows)
assert rows[0].startswith("| pool_decay_clock_rounding |"), rows[0][:40]
anchor = ("| release_managed_spell | done | melder_0 | tickets/stories/completed/2026-10-15_release_managed_spell_story.md | "
          "Landed 0.2.8244 (S4 of EPIC-2026-10-14-managed_spell_quantity: ReleaseManagedSpell, the lease, the Creations "
          f"register/unregister calls, four root exports). Next: S5 dispense codegen. | {NOW} |")
rows = rows[1:] + [anchor]
board = board[:region_start] + "\n".join(rows) + "\n" + board[region_end:]
# Notch notice.
old_notice = """- melder_0 landed 0.2.8243 (the managed pool `ManagedSpellQuantity` in the owning root's Creations,
  `ManagedSpellExhaustedError`, the probes' managed answer and purge 0; S3). Notch above it if you land after.
"""
new_notice = old_notice + """- melder_0 landed 0.2.8244 (`ReleaseManagedSpell`, the Aether-owned registry that gives managed objects back,
  `ManagedSpellLease` and four package-root exports; S4). Notch above it if you land after.
"""
assert board.count(old_notice) == 1, "notice"
board = board.replace(old_notice, new_notice)
BOARD.write_text(board, encoding="utf-8")

arts = ARTIFACTS.read_text(encoding="utf-8")
old_rows = [
    ("| tickets/stories/2026-10-15_release_managed_spell_story.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md | patch_doc | active | promote_to_documentation | S4: the ReleaseManagedSpell singleton (Aether-owned), register/unregister following the stores, release and its resolver, managed, release_all, describe, the lease, the root exports. | 2026-10-15T14:18:05Z | REQUIRED |",
     f"| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md | patch_doc | active | promote_to_documentation | S4 (landed 0.2.8244, story closed): the ReleaseManagedSpell singleton (Aether-owned), register/unregister following the stores, release and its resolver, managed, release_all, describe, the lease, the root exports; promote at S7. | {NOW} | REQUIRED |"),
    ("| tickets/stories/2026-10-15_release_managed_spell_story.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md | patch_doc | active | promote_to_documentation | S4: the registry's state, publication protocol, control flow, edge semantics and invariants. | 2026-10-15T14:18:05Z | REQUIRED |",
     f"| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md | patch_doc | active | promote_to_documentation | S4 (landed 0.2.8244, story closed): the registry's state, publication protocol, control flow, edge semantics and invariants; promote at S7. | {NOW} | REQUIRED |"),
]
for old, new in old_rows:
    assert arts.count(old) == 1, old[:90]
    arts = arts.replace(old, new)
ARTIFACTS.write_text(arts, encoding="utf-8")

lines = len(STORY_DONE.read_text(encoding="utf-8").splitlines())
epic = EPIC.read_text(encoding="utf-8")
old_ev = "  - context_compass/tickets/stories/completed/2026-10-15_release_managed_spell_story.md:1-330\n"
assert epic.count(old_ev) == 1
epic = epic.replace(old_ev, f"  - context_compass/tickets/stories/completed/2026-10-15_release_managed_spell_story.md:1-{lines}\n")
EPIC.write_text(epic, encoding="utf-8")
print("boards synced", NOW, "story lines", lines)
