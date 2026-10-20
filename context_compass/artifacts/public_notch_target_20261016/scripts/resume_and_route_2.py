"""Refresh the ticket's resume view and its attention-board row while the closure waits for the owner (2026-10-16).

Run from the context_compass root:  python artifacts/public_notch_target_20261016/scripts/resume_and_route_2.py <NOW>
Both files are re-read right before the write; each edit is an exact, asserted replacement (LF files).
"""
import pathlib
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")

OLD_RESUME = """- State: in_progress (melder_0), implementation. Source: 0.2.8248 plus this task's conduit.py change, not yet
  notched. Done: the patch lane and mapping; red then green (16 unit, 10 integration tests) and the notch callers'
  suites with the GIL off and on (Notes 13:28:26Z); README, governed-change, UX expert 17 and 26, the concept map
  and the README-loop probe (Notes 13:41:41Z). conduit.py is held by this task until it lands; spellbook.py and
  transfer_of_ownership.py are melder_1's (M1-20, Notes 13:40:45Z).
- Open for the owner: whether `add_to_spell_index` / `remove_from_spell_index` get the same keyword (Notes).
- Next: (1) promote the patch lane into src_architecture, src_components and the tests docs, regenerate their
  indexes, re-extract and reassemble the graph; (2) the release note, the notch (read `__version__` then), the
  patch lane archived; (3) the closure with the NOTICE that releases conduit.py, the rebuild last.
- Limits: the whole tree was not run; the suites that were run are listed in the 13:28:26Z note.
"""

NEW_RESUME = """- State: in_progress (melder_0), implementation; notched 0.2.8249 (0.2.8248 plus this task's conduit.py change).
  Done: the patch lane and mapping; red then green (16 unit, 10 integration tests) and the notch callers' suites
  with the GIL off and on (Notes 13:28:26Z); README, governed-change, UX expert 17 and 26, the concept map and the
  README-loop probe (13:41:41Z); the system docs, their indexes and the graph (14:15:44Z); the rubric scores
  (14:15:45Z); the notch, the release-note section with both note examples probed, the patch lane archived and
  the artifact board synced (14:23:00Z). conduit.py is held by this task until it lands; spellbook.py and
  transfer_of_ownership.py are melder_1's (M1-20, Notes 13:40:45Z).
- Open for the owner: whether `add_to_spell_index` / `remove_from_spell_index` also take `spell_id=` to name the
  owned, parked version they move (restated in chat after the owner asked what it meant; ids stay identities).
  The closure waits for the answer: yes -> the keyword, tests, docs and release note join this landing; no or
  later -> a backlog task.
- Next: (1) the owner's answer; (2) the closure - summary "notched 0.2.8249" naming the release-note section, move
  to completed/, board sync (drop the oldest anchor), the folder row, NOTICE M0-177 releasing conduit.py to
  melder_1 with the INTENT-docstring FYI; (3) the rebuild last (assets and LLM bundles, both checks OK).
- Limits: the whole tree was not run; the suites that were run are listed in the 13:28:26Z note; the build assets
  and LLM bundles are stale until the rebuild.
"""

OLD_ROW_HEAD = ("| public_notch_target | in_progress | implementation | claude | melder_0 | none | Promote the patch lane "
                "into the system docs and their indexes, then re-extract and reassemble the graph. |")
NEW_ROW_HEAD = ("| public_notch_target | in_progress | implementation | claude | melder_0 | none | Owner answers whether "
                "add_to_spell_index / remove_from_spell_index take spell_id= too (this landing or backlog); then closure, "
                "NOTICE M0-177 and the rebuild last. |")
OLD_ROW_TAIL = ("| tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md | 2026-10-16T13:42:11Z "
                "| REQUIRED |")
NEW_ROW_TAIL = ("| tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md | " + NOW + " | REQUIRED |")


def replace_once(path: pathlib.Path, pairs: list) -> None:
    """Apply exact (old, new) replacements, each old occurring exactly once in an LF file."""
    text = path.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit(f"{path}: expected LF")
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit(f"{path}: {text.count(old)} occurrences of {old[:70]!r}")
        text = text.replace(old, new, 1)
    path.write_bytes(text.encode("utf-8"))
    print(f"{path}: {len(pairs)} edit(s)")


if __name__ == "__main__":
    ticket_text = TICKET.read_text(encoding="utf-8")
    updated = [ln for ln in ticket_text.split("\n") if ln.startswith("- Updated: ")]
    if len(updated) != 1:
        raise SystemExit("Updated line not found once")
    replace_once(TICKET, [(OLD_RESUME, NEW_RESUME), (updated[0] + "\n", "- Updated: " + NOW + "\n")])
    replace_once(pathlib.Path("attention_board.md"), [(OLD_ROW_HEAD, NEW_ROW_HEAD), (OLD_ROW_TAIL, NEW_ROW_TAIL)])
    for line in NEW_RESUME.splitlines():
        if len(line) > 120:
            print("LONG", len(line), line[:60])
