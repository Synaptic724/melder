"""Record the owner's go and melder_0's blocker on EPIC-2026-10-25-codegen_room_policy_defects (melder_0, 2026-10-25).

One all-or-nothing pass: a BLOCKER note on the epic and on each child task, each task's Status set to blocked, and
the three codegen board rows set to blocked with the unblock action. Usage: record_blocker_20261025.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

EPIC = "tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md"
TASKS = ("tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md",
         "tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md",
         "tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md")
ROWS = ("codegen_open_file_d10", "codegen_dynamic_import_d11", "codegen_materialize_d20")


class Pass(Record):
    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_blocker")
    epic_note = r.note(r.now, "BLOCKER", [
        "The owner's go (chat 2026-10-25): \"go ahead and do them one by one\" - D-10, D-11, D-20 in that order.",
        "melder_0's implementation turn was stopped by the session's automated content filter, which withholds the",
        "response and forbids regenerating it; it is the third such stop on this epic's material, so melder_0 cannot",
        "carry the implementation in this session. Nothing in src/ was changed. The three tasks stay fully specified",
        "(the owner's decisions, acceptance criteria, files and the patch-doc plan in their Notes) for whoever takes",
        "them; the owner's go stands."],
        [r.whole(t) for t in TASKS],
        ["The fixes are unstarted; the epic waits on an implementer."],
        ["The owner assigns the implementation to another agent or session."], "REQUIRED", 8)
    text = r.read(EPIC)
    text = r.once(text, "\n\n## Closure Confirmation\n", "\n\n" + epic_note + "\n\n## Closure Confirmation\n", "epic")
    text = r.once(text, "- Status: in_progress\n", "- Status: blocked\n", "epic status")
    r.stage(EPIC, text)
    r.set_field(EPIC, "Updated")
    for rel in TASKS:
        note = r.note(r.now, "BLOCKER", [
            "The owner gave the go on 2026-10-25; melder_0 is blocked by the session's content filter (the epic's",
            "BLOCKER note). Nothing in src/ changed; this task is ready for another implementer as specified."],
            [r.note_range(EPIC, "- DATETIME: " + r.now, "  TYPE: BLOCKER")],
            ["The task is unstarted."], ["The owner assigns an implementer."], "REQUIRED", 7)
        text = r.read(rel)
        text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + note + "\n\n## Context / Handoff Summary\n",
                      rel)
        text = r.once(text, "- Status: in_progress\n", "- Status: blocked\n", rel + " status")
        r.stage(rel, text)
        r.set_field(rel, "Updated")
    board = r.read(r.BOARD)
    for item in ROWS:
        rows = [line for line in board.split("\n") if line.startswith("| " + item + " |")]
        if len(rows) != 1:
            sys.exit(f"ROW {item}: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[1] = "blocked"
        cells[5] = "melder_0 blocked by the session content filter"
        cells[6] = "The owner assigns the implementation (go given 2026-10-25)."
        cells[10] = r.now
        board = board.replace(rows[0], " | ".join(cells))
    r.stage(r.BOARD, board)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
