"""S8 after the rebuild: tick the rebuild, the walkthrough and the resume views; the board row's next action.

Run from context_compass/: python <this file> <NOW>
Exact replacements, each asserted once (LF files); then the rebuild MEASURE note goes in with s8_append_note.py.
"""
import pathlib
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md")
EPIC = pathlib.Path("tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
BOARD = pathlib.Path("attention_board.md")


def edit(path: pathlib.Path, pairs: list) -> None:
    """Apply exact replacements, each expected once; write once."""
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        assert text.count(old) == 1, (path.name, old[:90], text.count(old))
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("edited", path)


edit(STORY, [
    ("- [ ] Rebuild last: the asset runner and the LLM bundles, each with `--check`.\n",
     "- [x] Rebuild last: the asset runner and the LLM bundles, each with `--check` (six OK lines).\n"),
    ("- [ ] Work walkthrough shared with user\n",
     f"- [x] Work walkthrough shared with user ({NOW}, the owner report)\n"),
    ("- Next: the rebuild last (both checks), then the report; then the owner accepts S8 with the epic (S7 and S8 close with\n"
     "  it) or redirects.\n",
     "- Next: the owner accepts S8 with the epic (S7 and S8 close with it) or redirects. The rebuild ran last and both\n"
     "  checks print only OK (the MEASURE note after the move to review).\n"),
    ("- Custody: once the rebuild passes, spellbook.py, spellbook_creation_system.py, transfer_of_ownership.py,\n",
     "- Custody: the rebuild passed, so spellbook.py, spellbook_creation_system.py, transfer_of_ownership.py,\n"),
])
edit(EPIC, [
    ("- Remaining: the rebuild for 0.2.8248 (last, both checks), then the owner's acceptance of the epic, which closes S7,\n"
     "  S8 and the epic; Milestone 5 (the MelderOps prototype) after a release, with the owner.\n",
     "- Remaining: the owner's acceptance of the epic, which closes S7, S8 and the epic (the 0.2.8248 rebuild ran last and\n"
     "  both checks print only OK); Milestone 5 (the MelderOps prototype) after a release, with the owner.\n"),
    ("  lane's files (spellbook.py among them) are free for it once the 0.2.8248 rebuild passes.\n",
     "  lane's files (spellbook.py among them) are free for it: the 0.2.8248 rebuild passed.\n"),
    ("- Next 1-3 actions: rebuild last and check; report to the owner; on the owner's acceptance close S7, S8 and the epic\n"
     "  (completion summaries, completed/, board anchors, artifact dispositions).\n",
     "- Next 1-3 actions: the owner accepts or redirects; on acceptance close S7, S8 and the epic (completion summaries,\n"
     "  completed/, board anchors, artifact dispositions).\n"),
    ("- Updated: " + next(line for line in EPIC.read_text(encoding="utf-8").split("\n")
                         if line.startswith("- Updated: "))[len("- Updated: "):] + "\n",
     "- Updated: " + NOW + "\n"),
])
board = BOARD.read_bytes().decode("utf-8")
old_row = next(line for line in board.split("\n") if line.startswith("| melder_object_pools | "))
new_row = old_row.replace(
    "| Rebuild the assets and LLM bundles last (both --check), then report to the owner. |",
    "| The owner accepts S1-S8 and the epic, or redirects. |",
)
new_row = new_row.rsplit(" | ", 2)[0] + " | " + NOW + " | REQUIRED |"
assert new_row != old_row and new_row.count("The owner accepts S1-S8") == 1
edit(BOARD, [(old_row, new_row)])
