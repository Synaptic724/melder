"""S5 turn-in: deterministic closure sync of attention_board.md and artifact_board.md; fix the epic note's range."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
BOARD = ROOT / "attention_board.md"
ARTIFACTS = ROOT / "artifact_board.md"
EPIC = ROOT / "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
STORY_DONE = ROOT / "tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md"

board = BOARD.read_text(encoding="utf-8")
# Active row: route to S6.
start = board.index("| melder_object_pools | in_progress | implementation |")
end = board.index("\n", start)
new_row = ("| melder_object_pools | ready | discovery | claude | melder_0 | none | S6: read TransferOfOwnership's creation "
           "moves, rollback, `_migrate_inactive_members` and `_apply_notch` whole (U9), then write the S6 component "
           "patch. | `managed_spell_quantity` built in seven stories (epic Build Specification), one notch per story, "
           "rebuild last. | Every story landed with green tests and the owner accepts, or the owner redirects. | "
           f"tickets/stories/2026-10-15_managed_ownership_transfer_story.md | {NOW} | REQUIRED |")
board = board[:start] + new_row + board[end:]
# Detail entry.
old_detail = """    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md
    - tickets/stories/2026-10-15_managed_dispense_codegen_story.md
"""
new_detail = """    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md
    - tickets/stories/2026-10-15_managed_ownership_transfer_story.md
"""
assert board.count(old_detail) == 1, "detail"
board = board.replace(old_detail, new_detail)
# Closed anchors: drop the oldest (top) row, add S5.
begin_marker = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
region_start = board.index(begin_marker) + len(begin_marker)
region_end = board.index("<!-- END USER-DEFINED: closed_anchors -->")
rows = [row for row in board[region_start:region_end].splitlines() if row.startswith("| ")]
assert len(rows) == 12, len(rows)
assert rows[0].startswith("| slotted_d1_cluster_exit |"), rows[0][:40]
anchor = ("| managed_dispense_codegen | done | melder_0 | "
          "tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md | "
          "Landed 0.2.8245 (S5 of EPIC-2026-10-14-managed_spell_quantity: leases through emitted plans and doors, "
          f"Conduit.managed_spell_meld). Next: S6 ownership transfer. | {NOW} |")
rows = rows[1:] + [anchor]
board = board[:region_start] + "\n".join(rows) + "\n" + board[region_end:]
# Notch notice.
old_notice = """- melder_0 landed 0.2.8244 (`ReleaseManagedSpell`, the Aether-owned registry that gives managed objects back,
  `ManagedSpellLease` and four package-root exports; S4). Notch above it if you land after.
"""
new_notice = old_notice + """- melder_0 landed 0.2.8245 (managed objects leased through the emitted plans and doors - direct melds and
  injections - and `Conduit.managed_spell_meld`; S5). Notch above it if you land after.
"""
assert board.count(old_notice) == 1, "notice"
board = board.replace(old_notice, new_notice)
BOARD.write_text(board, encoding="utf-8")

arts = ARTIFACTS.read_text(encoding="utf-8")
old_rows = [
    ("| tickets/stories/2026-10-15_managed_dispense_codegen_story.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md | patch_doc | active | promote_to_documentation | S5 (in progress): per-path sharedness, solo decline, manifest key, door rows on the many templates, the specializer decline, the managed site kind (lease, miss, placement, return), managed_spell_meld; promote at S7. | 2026-10-15T16:26:20Z | REQUIRED |",
     f"| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md | patch_doc | active | promote_to_documentation | S5 (landed 0.2.8245, story closed): per-path sharedness, solo decline, manifest key, door rows on the many templates, the specializer decline, the managed site kind (lease, miss, placement, return), managed_spell_meld; promote at S7. | {NOW} | REQUIRED |"),
    ("| tickets/stories/2026-10-15_managed_dispense_codegen_story.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_dispense_codegen.md | patch_doc | active | promote_to_documentation | S5 (in progress): the emitted shapes, lease groups and returns, edge semantics and invariants of the managed site; promote at S7. | 2026-10-15T16:26:20Z | REQUIRED |",
     f"| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_dispense_codegen.md | patch_doc | active | promote_to_documentation | S5 (landed 0.2.8245, story closed): the emitted shapes, lease groups and returns, edge semantics and invariants of the managed site; promote at S7. | {NOW} | REQUIRED |"),
]
for old, new in old_rows:
    assert arts.count(old) == 1, old[:90]
    arts = arts.replace(old, new)
ARTIFACTS.write_text(arts, encoding="utf-8")

lines = len(STORY_DONE.read_text(encoding="utf-8").splitlines())
epic = EPIC.read_text(encoding="utf-8")
old_ev = "  - context_compass/tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md:1-STORY_LINES\n"
assert epic.count(old_ev) == 1
epic = epic.replace(old_ev, f"  - context_compass/tickets/stories/completed/2026-10-15_managed_dispense_codegen_story.md:1-{lines}\n")
EPIC.write_text(epic, encoding="utf-8")
print("boards synced", NOW, "story lines", lines)
