"""File TASK-2026-10-16-stamp_test_boots_its_own_aether (backlog) and put the wording lane on hold for melder_1.

Run from context_compass/:  python artifacts/spell_id_wording_20261016/scripts/hold_and_file_backlog.py <NOW>

1. Writes the backlog ticket (refuses an existing file).
2. Adds its artifact-board row.
3. Appends the FACT and BLOCKER notes to the wording ticket; sets Status blocked, the transition, the two done
   checklist items and the resume view.
4. Sets the wording lane's attention-board row to blocked (the detail entry's SWITCH_TRIGGER is unchanged).
"""
import pathlib
import re
import subprocess
import sys

NOW = sys.argv[1]
LANE = pathlib.Path("artifacts/spell_id_wording_20261016")
BACKLOG = pathlib.Path("tickets/tasks/backlog/2026-10-16_stamp_test_boots_its_own_aether_task.md")
WORDING = pathlib.Path("tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md")
TEMPLATE = pathlib.Path("templates/task_template.md")


def template_block(start: str, end: str) -> str:
    """Return the template text from the `start` heading up to (not including) the `end` heading."""
    text = TEMPLATE.read_text(encoding="utf-8")
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def backlog_text() -> str:
    """Compose the backlog ticket; template-owned sections are copied from the template verbatim."""
    done = template_block("## Done Checklist", "## Artifact Links (Optional)")
    noting = template_block("## Noting Behavior", "## Contribution Attribution")
    template = TEMPLATE.read_text(encoding="utf-8")
    tail = template[template.index("## Project-Specific Additions"):]
    body = (pathlib.Path(LANE / "notes/backlog_ticket_body.txt").read_text(encoding="utf-8"))
    body = body.replace("@@DONE@@\n", done).replace("@@NOTING@@\n", noting).replace("@@TAIL@@\n", tail)
    return body.replace("@@NOW@@", NOW)


def write_backlog() -> int:
    """Write the backlog ticket; return its line count."""
    if BACKLOG.exists():
        raise SystemExit(f"{BACKLOG} exists; refusing to overwrite")
    text = backlog_text()
    long = [ln for ln in text.splitlines() if len(ln) > 120]
    if long:
        raise SystemExit(f"backlog ticket: {len(long)} lines over 120: {long[:2]}")
    BACKLOG.write_text(text, encoding="utf-8")
    return len(text.splitlines())


def add_artifact_row() -> None:
    """Add the backlog ticket's reproducer row to the artifact board."""
    board = pathlib.Path("artifact_board.md")
    text = board.read_text(encoding="utf-8")
    assert "\r\n" not in text
    end = "<!-- END USER-DEFINED: active_artifacts -->"
    assert text.count(end) == 1 and str(BACKLOG) not in text
    row = ("| " + str(BACKLOG) + " | artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt | "
           "defect_reproducer | backlog | retain_as_reference | The frame-then-stamp reproducer, its GIL-on twin "
           "(order_dependence_probe_gil1.txt) and the GIL-on unit run that shows it (free_unit_gil1_with_stamp.txt); "
           "rerun when the task is scheduled. | " + NOW + " | HELPFUL |\n")
    board.write_text(text.replace(end, row + end, 1), encoding="utf-8")


def edit_wording_ticket(backlog_lines: int) -> None:
    """Append the two notes, then set Status, transition, checklist and resume view."""
    note = (LANE / "notes/note_hold_and_backlog.txt")
    note_text = note.read_text(encoding="utf-8").replace("@@BACKLOG_LINES@@", str(backlog_lines))
    note.write_text(note_text, encoding="utf-8")
    subprocess.run([sys.executable, str(LANE / "scripts/append_note.py"), NOW, str(note), str(WORDING)], check=True)
    raw = WORDING.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace(nl, "\n")
    pairs = [
        ("- Status: in_progress\n", "- Status: blocked\n"),
        ("- from_state: draft\n- to_state: in_progress\n- transition_reason: opened in progress on the owner's "
         "direction (chat 2026-10-16, quoted in the DECISION note);\n  melder_0 is assigned and its previous lane is "
         "closed.\n",
         "- from_state: in_progress\n- to_state: blocked\n- transition_reason: the decisions for files nobody holds are "
         "applied and green (MEASURE, 18:56:42Z); the\n  125 left sit in files melder_1 holds until its rule-2 "
         "closure and rebuild (M1-22), so the lane waits for its\n  release NOTICE (BLOCKER, " + NOW + ").\n"),
        ("- [ ] Inventory every live occurrence", "- [x] Inventory every live occurrence"),
        ("- [ ] Apply the decisions in files nobody else holds", "- [x] Apply the decisions in files nobody else holds"),
    ]
    for old, new in pairs:
        assert text.count(old) == 1, old[:60]
        text = text.replace(old, new, 1)
    start = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    end = text.index("\n## Project-Specific Additions", start)
    resume = (LANE / "notes/resume_view_blocked.txt").read_text(encoding="utf-8").replace("@@NOW@@", NOW)
    text = text[:start] + resume.rstrip("\n") + "\n" + text[end:]
    long = [ln for ln in resume.splitlines() + pairs[1][1].splitlines() if len(ln) > 120]
    if long:
        raise SystemExit(f"wording ticket: lines over 120: {long[:2]}")
    WORDING.write_bytes(text.replace("\n", nl).encode("utf-8"))


def edit_board_row() -> None:
    """Set the wording lane's active row to blocked with its blocker and next action."""
    board = pathlib.Path("attention_board.md")
    text = board.read_text(encoding="utf-8")
    rx = re.compile(r"^\| spell_id_wording \| .*\| tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task"
                    r"\.md \| [0-9TZ:-]+ \| REQUIRED \|$", re.M)
    assert len(rx.findall(text)) == 1
    row = ("| spell_id_wording | blocked | implementation | claude | melder_0 | melder_1 holds the 25 files of the "
           "held scope (its rule-2 src and tests, the system docs, graph, release note and __version__.py) until its "
           "closure and rebuild (M1-22) | On melder_1's release NOTICE, recheck the 125 held decisions against the "
           "files, then apply them. | Every 'version id' that relates to a spell index names spell_id or the spell "
           "index id, by hand; the rest listed with reasons. | The wording lands with its notch, release note and "
           "rebuild, or the owner redirects. | tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md | "
           + NOW + " | REQUIRED |")
    board.write_text(rx.sub(lambda m: row, text, count=1), encoding="utf-8")


def main() -> None:
    """Run the four steps in order."""
    n = write_backlog()
    add_artifact_row()
    edit_wording_ticket(n)
    edit_board_row()
    print("backlog ticket", BACKLOG, n, "lines; artifact row added; wording ticket blocked; board row blocked")


if __name__ == "__main__":
    main()
