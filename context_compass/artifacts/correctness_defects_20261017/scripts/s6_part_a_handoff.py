"""S6 part A's hand-off after the rebuild and M0-192: the story's task, test plan and resume view; the epic's S6 lines
and resume view; the board row to handoff (melder_0, 2026-10-18).

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/s6_part_a_handoff.py <NOW>
Exact replacements, each asserted once (LF files), each file re-read right before its write.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md")
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
BOARD = pathlib.Path("attention_board.md")


def edit(path: pathlib.Path, pairs: list) -> None:
    """Apply exact replacements, each expected once, set the Updated line; write once."""
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        assert text.count(old) == 1, (path.name, old[:90], text.count(old))
        text = text.replace(old, new)
    text, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, text, count=1)
    assert count == 1
    long = [line for _old, new in pairs for line in new.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    path.write_bytes(text.encode("utf-8"))
    print("edited", path)


edit(STORY, [
    ("- [ ] Task: part A with symptom-named regression tests, docs, notch and the rebuild last.\n",
     "- [x] Task: part A with symptom-named regression tests, docs, notch and the rebuild last (0.2.8254,\n"
     "  2026-10-18; MEASURE notes).\n"),
    ("  GIL off and on; probes Q1-Q6 and S1-S2 re-run. Not run: no fix exists yet.\n",
     "  GIL off and on; probes Q1-Q6, S1-S2 and R1-R3 re-run at the fix. Part A ran green (MEASURE notes); not run:\n"
     "  hosted CI and coverage (the owner's).\n"),
    ("- State: in_progress (melder_0), implementation. The direction and the scope are the owner's (DECISION notes\n"
     "  of 2026-10-17T23:50:39Z and 2026-10-18T00:42:22Z): only the four managed settings leave the spell_id.\n"
     "  melder_1's 0.2.8253 landed (M1-26). Part A sits in free files (bind.py, managed_spell_quantity.py,\n"
     "  creations.py, caching_system.py); part B in spellbook.py (melder_1's until its release).\n"
     "- Next: (1) part A with its tests, docs, notch (above 0.2.8253) and the rebuild last; (2) report to the owner\n"
     "  and talk through part B, the legacy record and anything more of the bind call; (3) part B after melder_1's\n"
     "  release of spellbook.py.\n",
     "- State: in_progress (melder_0), handoff. The direction and the scope are the owner's (DECISION notes\n"
     "  of 2026-10-17T23:50:39Z and 2026-10-18T00:42:22Z): only the four managed settings leave the spell_id.\n"
     "  Part A is landed at 0.2.8254 - the fingerprint, the pool's rebind, cache generation 22 - with its tests green\n"
     "  with the GIL off and on (the whole tree), the release note, the system documents and the graph, and rebuilt\n"
     "  last with both checks OK (MEASURE notes); its files are released to melder_1 (M0-192). Part B sits in\n"
     "  spellbook.py (melder_1's until its release); its patch doc is a draft.\n"
     "- Next: (1) the owner's talk: part B's staging refusal, the legacy record (two settings-only versions of one\n"
     "  class in one index: with no extra code its restore fails whole on the collision) and anything more of the\n"
     "  bind call; (2) part B on his word, after melder_1 releases spellbook.py; (3) closure: the walkthrough, the\n"
     "  patch docs archived, the board synced.\n"),
])
edit(EPIC, [
    ("  sends a parked version's object to the active version's pool and strands its count (sweep A6). In progress:\n"
     "  the managed settings leave the spell_id (owner, 2026-10-17).\n",
     "  sends a parked version's object to the active version's pool and strands its count (sweep A6). Part A landed\n"
     "  at 0.2.8254 (the managed settings left the spell_id; owner, 2026-10-17); part B waits for the owner's talk.\n"),
    ("  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; in progress, melder_0: the managed\n"
     "  settings leave the spell_id),\n",
     "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; in progress, melder_0: part A\n"
     "  landed at 0.2.8254, part B open),\n"),
    ("  The owner confirmed S6's scope (DECISION note of 2026-10-18T00:42:22Z); melder_1's 0.2.8253 landed (M1-26).\n"
     "- Next: (1) S6's part A (the owner's go, 2026-10-18; melder_1's 0.2.8253 landed), then the talk on its part B and\n"
     "  legacy record; (2) a fourth tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n",
     "  The owner confirmed S6's scope (DECISION note of 2026-10-18T00:42:22Z); melder_1's 0.2.8253 landed (M1-26).\n"
     "  S6's part A landed at 0.2.8254 and was rebuilt last; its files are released to melder_1 (M0-192).\n"
     "- Next: (1) the owner's talk on S6's part B, its legacy record and anything more of the bind call; (2) a fourth\n"
     "  tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n"),
])

board = BOARD.read_text(encoding="utf-8")
lines = board.split("\n")
hits = [i for i, line in enumerate(lines) if line.startswith("| managed_settings_spell_id | ")]
assert len(hits) == 1
cells = lines[hits[0]].split(" | ")
assert len(cells) == 12 and cells[2] == "implementation", cells[:3]
cells[2] = "handoff"
cells[6] = ("The owner's word on part B's staging refusal, the legacy record and anything more of the bind call "
            "(part A landed at 0.2.8254, rebuilt, files released).")
cells[10] = NOW
lines[hits[0]] = " | ".join(cells)
BOARD.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("board row: handoff")
