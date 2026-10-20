"""Sync S4's resume view and its board row after the M4-M7, prototype and scope-request notes (melder_1).

Replaces exact anchored text in the S4 story's Context / Handoff Summary and in the minted_index_registry row of
attention_board.md; LF files only; each anchor must occur once; read-back verified. Usage: --check | --apply
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
BOARD = ROOT / "attention_board.md"
TS = "2026-10-18T17:35:35Z"

STORY_OLD = """- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry under its owning
  conduit (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). The fix sits in spellbook.py (or conduit.py); melder_0 holds
  spellbook.py for S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code (M1-38), so the code waits for its
  hand-back.
- Next: (1) re-run probe M1-M3 and V1-V4 on the current tree, GIL off and on, and re-read the minting seam and
  the frame registry whole; (2) the patch and the owner's word on the exact edits; (3) the fix once spellbook.py
  is back, its tests, docs, notch and the rebuild last.
"""
STORY_NEW = """- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry under its owning
  conduit (Requirements). Defect proven on 0.2.8251 and re-verified on 0.2.8256 (Notes); probes and runs in
  Artifact Links.
- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8256, the readers read whole (FACT note); bind's
  collision guard and a transfer by spell_id miss the version too (MEASURE note, M4-M7). The fix is three edits -
  A the seam registers the minted index, B the root's teardown unregisters it, C residency reads the lineage -
  proven in /tmp copies (MEASURE note); B and C widen the EXECUTION_BOUNDARY, so the owner's word is asked
  (DECISION_REQUEST note). spellbook.py is melder_0's until S1 and S2 of
  EPIC-2026-10-18-spell_identity_is_the_code land; no src edit yet.
- Next: (1) the owner's word on A + B + C; (2) the boundary, the patch docs, the red tests and M1-39 to melder_0
  (spellbook.py after his landing, mutation_research.py); (3) the fix once both files are ours, its tests, docs,
  notch and the rebuild last.
"""
ROW_OLD = ("| minted_index_registry | in_progress | discovery | claude | melder_1 | none | Re-run probe M1-M3 and V1-V4 on "
           "0.2.8256 (GIL off and on); re-read the minting seam and the frame registry whole. |")
ROW_NEW = ("| minted_index_registry | in_progress | discovery | claude | melder_1 | none | The owner's word on edits A + B + C "
           "(the seam, the root's teardown, residency); then the patch docs and the red tests. |")
STAMP_OLD = ("tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md | 2026-10-18T17:10:56Z | "
             "REQUIRED |")
STAMP_NEW = ("tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md | " + TS + " | REQUIRED |")


def replace_once(path: pathlib.Path, pairs: list, apply: bool) -> None:
    """Replace each (old, new) pair exactly once in `path`; write and verify with `apply`."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    text = raw.decode("utf-8")
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times: %s" % (path.name, text.count(old), old[:80]))
        text = text.replace(old, new)
    print("%s: %d replacement(s) ready" % (path.name, len(pairs)))
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch: %s" % path.name)
        print("%s: applied" % path.name)


def main() -> None:
    """Check or apply both files; the story first."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    replace_once(STORY, [(STORY_OLD, STORY_NEW)], apply)
    replace_once(BOARD, [(ROW_OLD, ROW_NEW), (STAMP_OLD, STAMP_NEW)], apply)


main()
