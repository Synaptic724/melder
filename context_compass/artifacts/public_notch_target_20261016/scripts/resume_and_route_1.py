"""Refresh the ticket's one current resume view and its attention-board row after the docs pass (2026-10-16).

Run from the context_compass root:  python artifacts/public_notch_target_20261016/scripts/resume_and_route_1.py <NOW>
Both files are re-read right before the write; each edit is an exact, asserted replacement (LF files).
"""
import pathlib
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")

OLD_RESUME = """- State: in_progress (melder_0), discovery. Source revision 0.2.8248. conduit.py is held by this task until it
  lands (melder_1's D3 edits `notch_spell` too); spellbook.py and transfer_of_ownership.py are released to melder_1.
- Open for the owner: whether `add_to_spell_index` / `remove_from_spell_index` get the same keyword (Notes).
- Next: (1) read the notch path whole and probe today's target checks; (2) the patch lane and mapping note;
  (3) red tests, the change, green with the GIL off and on, the README-loop probe; docs, notch, rebuild last.
- Limits: nothing run yet (Not run).
"""

NEW_RESUME = """- State: in_progress (melder_0), implementation. Source: 0.2.8248 plus this task's conduit.py change, not yet
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

OLD_ROW_HEAD = ("| public_notch_target | in_progress | discovery | claude | melder_0 | none | Write the patch lane "
                "public_notch_target_2026_10_16 and the mapping note, then the red tests. |")
NEW_ROW_HEAD = ("| public_notch_target | in_progress | implementation | claude | melder_0 | none | Promote the patch lane "
                "into the system docs and their indexes, then re-extract and reassemble the graph. |")
OLD_ROW_TAIL = ("| tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md | 2026-10-16T12:33:26Z "
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
