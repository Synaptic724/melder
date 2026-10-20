"""Route TASK-2026-10-16-stamp_test_boots_its_own_aether out of the backlog (owner's go-ahead, chat 2026-10-16).

Run from context_compass/ AFTER `mv -n` has moved the ticket from tickets/tasks/backlog/ to tickets/tasks/:
    python artifacts/spell_id_wording_20261016/scripts/route_stamp_task.py <NOW>
Sets the ticket in progress for melder_0, appends the routing note, adds the board row and its detail entry, and
repoints the artifact-board row at the routed path.
"""
import pathlib
import subprocess
import sys

NOW = sys.argv[1]
OLD = "tickets/tasks/backlog/2026-10-16_stamp_test_boots_its_own_aether_task.md"
NEW = "tickets/tasks/2026-10-16_stamp_test_boots_its_own_aether_task.md"
EXIT = "The stamp test passes after the frame tests in both GIL modes, or the owner redirects."


def edit_ticket() -> None:
    """Metadata, transition and the routing note."""
    ticket = pathlib.Path(NEW)
    text = ticket.read_text(encoding="utf-8")
    pairs = [
        ("- Status: draft\n", "- Status: in_progress\n"),
        ("- Agent Name: unassigned\n", "- Agent Name: melder_0\n"),
        ("- Agent Role: UNKNOWN\n", "- Agent Role: synaptic_python_developer\n"),
        ("- from_state: draft\n- to_state: draft\n", "- from_state: draft\n- to_state: in_progress\n"),
        ("- transition_reason: created as a draft from the spell_id_wording lane's unit runs (\"if you found more bugs "
         "just add\n  tickets\", owner, 2026-10-16); test-only, parked until scheduled.\n",
         "- transition_reason: the owner's go-ahead (chat 2026-10-16, \"please go ahead and do your thing\", answering "
         "whether to\n  fix the stamp test while the wording lane waits); melder_0 takes it (PLAN note).\n"),
        ("- State: draft in backlog, not routed; found by TASK-2026-10-16-spell_id_wording_near_spell_index.\n",
         "- State: in_progress (melder_0) since " + NOW + "; found by\n  "
         "TASK-2026-10-16-spell_id_wording_near_spell_index.\n"),
        ("- Next: route it, rerun the reproducer, add the fixture, run both GIL modes.\n",
         "- Next: rerun the reproducer, add the fixture, run both GIL modes, then close (no src: no notch, no "
         "rebuild).\n"),
    ]
    for old, new in pairs:
        assert text.count(old) == 1, old[:70]
        text = text.replace(old, new, 1)
    assert all(len(line) <= 120 for line in text.splitlines()), [l for l in text.splitlines() if len(l) > 120]
    ticket.write_text(text, encoding="utf-8")
    note = pathlib.Path("artifacts/spell_id_wording_20261016/notes/note_stamp_routed.txt")
    subprocess.run([sys.executable, "artifacts/spell_id_wording_20261016/scripts/append_note.py", NOW, str(note), NEW],
                   check=True)


def edit_boards() -> None:
    """Add the active row and its detail entry; repoint the artifact row."""
    board = pathlib.Path("attention_board.md")
    text = board.read_text(encoding="utf-8")
    end_rows = "<!-- END USER-DEFINED: active_items -->"
    end_details = "<!-- END USER-DEFINED: active_attention_details -->"
    assert text.count(end_rows) == 1 and text.count(end_details) == 1 and "| stamp_test_aether |" not in text
    row = ("| stamp_test_aether | in_progress | implementation | claude | melder_0 | none | Rerun the reproducer, then "
           "add the fresh-Aether fixture to the stamp test file. | test_spell_managed_quantity_stamp.py installs the "
           "Aether it needs, so it passes in any order. | " + EXIT + " | " + NEW + " | " + NOW + " | REQUIRED |\n")
    detail = ("- WORK_ITEM: stamp_test_aether\n  SWITCH_TRIGGER: " + EXIT + "\n  RESUME_HIERARCHY:\n    - " + NEW
              + "\n")
    text = text.replace(end_rows, row + end_rows, 1).replace(end_details, detail + end_details, 1)
    board.write_text(text, encoding="utf-8")
    art = pathlib.Path("artifact_board.md")
    atext = art.read_text(encoding="utf-8")
    old_cell = "| " + OLD + " | artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt | defect_reproducer | backlog |"
    new_cell = "| " + NEW + " | artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt | defect_reproducer | active |"
    assert atext.count(old_cell) == 1
    art.write_text(atext.replace(old_cell, new_cell, 1), encoding="utf-8")


def main() -> None:
    """Route the task."""
    assert pathlib.Path(NEW).exists() and not pathlib.Path(OLD).exists(), "move the ticket with mv -n first"
    edit_ticket()
    edit_boards()
    print("routed", NEW, NOW)


if __name__ == "__main__":
    main()
