"""Close TASK-2026-10-16-stamp_test_boots_its_own_aether (tests only: no notch, no release note, no rebuild).

Run from context_compass/:  python artifacts/spell_id_wording_20261016/scripts/close_stamp_task.py <NOW> notes
    then:  mv -n tickets/tasks/2026-10-16_stamp_test_boots_its_own_aether_task.md tickets/tasks/completed/
    then:  python artifacts/spell_id_wording_20261016/scripts/close_stamp_task.py <NOW> boards
"""
import pathlib
import re
import subprocess
import sys

NOW, STEP = sys.argv[1], sys.argv[2]
ACTIVE = "tickets/tasks/2026-10-16_stamp_test_boots_its_own_aether_task.md"
DONE = "tickets/tasks/completed/2026-10-16_stamp_test_boots_its_own_aether_task.md"
RUN = "artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt"


def close_ticket() -> None:
    """Append the closing notes and write the completion header, state, checklists and resume view."""
    ticket = pathlib.Path(ACTIVE)
    marker = "- DATETIME: " + NOW + "\n  AUTHOR: melder_0\n  AUTHOR_ROLE: synaptic_python_developer\n  TYPE: MEASURE"
    if marker not in ticket.read_text(encoding="utf-8"):
        subprocess.run([sys.executable, "artifacts/spell_id_wording_20261016/scripts/append_note.py", NOW,
                        "artifacts/spell_id_wording_20261016/notes/note_stamp_measure.txt", ACTIVE], check=True)
    text = ticket.read_text(encoding="utf-8")
    title = "# Task: stamp_test_boots_its_own_aether - the managed stamp test installs the Aether it needs\n"
    header = (title + "\n- Completed: " + NOW + "\n"
              "- Summary: tests only, no notch - test_spell_managed_quantity_stamp.py installs a fresh Aether around\n"
              "  each test (autouse `fresh_aether_world`), so it passes after the frame tests: red 1 failed / 39 "
              "passed,\n  green 40 passed, with the GIL off and on. The unit tree passes in both modes apart from the "
              "asset-stamp\n  test (assets 0.2.8249, package 0.2.8250, melder_1's rebuild to come). No release-note "
              "entry, no rebuild;\n  the tests_components code-map entry rides TASK-2026-10-16-spell_id_wording_near_"
              "spell_index.\n")
    reason = ("- transition_reason: the fixture is in and green in both GIL modes (MEASURE, " + NOW + "); a "
              "routine\n  test-only change closed by its assignee under the owner's go-ahead (DECISION, " + NOW
              + ").\n")
    pairs = [
        (title, header),
        ("- Status: in_progress\n", "- Status: done\n"),
        ("- from_state: draft\n- to_state: in_progress\n", "- from_state: in_progress\n- to_state: done\n"),
        ("- transition_reason: the owner's go-ahead (chat 2026-10-16, \"please go ahead and do your thing\", answering "
         "whether to\n  fix the stamp test while the wording lane waits); melder_0 takes it (PLAN note).\n", reason),
        ("- [ ] Rerun the reproducer", "- [x] Rerun the reproducer"),
        ("- [ ] Add the fixture to the stamp file", "- [x] Add the fixture to the stamp file"),
        ("- [ ] Run Ticket Microcycle", "- [x] Run Ticket Microcycle"),
        ("- [ ] Record meaningful attributed findings", "- [x] Record meaningful attributed findings"),
        ("- [ ] Steps complete and checked off", "- [x] Steps complete and checked off"),
        ("- [ ] Deliverables produced and linked", "- [x] Deliverables produced and linked"),
        ("- [ ] Documentation updated (if needed)",
         "- [x] Documentation updated (if needed): the module docstring; tests_components rides the wording lane"),
        ("- [ ] Validation status recorded", "- [x] Validation status recorded"),
        ("- [ ] Unknown-first discipline followed", "- [x] Unknown-first discipline followed"),
        ("- [ ] Notes quality maintained", "- [x] Notes quality maintained"),
        ("- [ ] Applicable anti-pattern checks", "- [x] Applicable anti-pattern checks"),
        ("- [ ] Criteria, required tests/reviews", "- [x] Criteria, required tests/reviews"),
        ("- [ ] Board sync completed", "- [x] Board sync completed"),
        ("- [ ] No status transition without", "- [x] No status transition without"),
        ("- [ ] No implementation/validation from", "- [x] No implementation/validation from"),
        ("- [ ] No closure without", "- [x] No closure without"),
        ("- Not run (no fix written yet). The reproducer was run; see Notes.\n",
         "- Run (MEASURE note): the reproducer red then green, the file alone and the unit tree, GIL off and on.\n"),
        ("- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created",
         "- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, test (the fixture,\n"
         "  tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:29-50);\n  created"),
    ]
    for old, new in pairs:
        assert text.count(old) == 1, old[:70]
        text = text.replace(old, new, 1)
    start = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    end = text.index("\n## Project-Specific Additions", start)
    view = ("- Scope: test-only - the managed stamp test installs the Aether it needs; no src change, no notch.\n"
            "- State: done (melder_0), " + NOW + ". Red then green in both GIL modes; the unit tree green apart from "
            "the\n  asset-stamp test, which waits for melder_1's rebuild.\n"
            "- Follow-up: tests_components.md's code-map entry for the file, carried by\n"
            "  TASK-2026-10-16-spell_id_wording_near_spell_index after melder_1 releases the system docs.\n"
            "- Evidence: the Notes; the runs under artifacts/spell_id_wording_20261016/runs/ (stamp_*).\n"
            "- Next: none in this task.\n")
    text = text[:start] + view + text[end:]
    long = [line for line in text.splitlines() if len(line) > 120 and "artifacts/" not in line]
    assert not long, long
    ticket.write_text(text, encoding="utf-8")


def sync_boards() -> None:
    """Remove the active row and detail, add the anchor (cap 12, oldest first out), clear the artifact row."""
    assert pathlib.Path(DONE).exists() and not pathlib.Path(ACTIVE).exists(), "move the ticket first"
    board = pathlib.Path("attention_board.md")
    text = board.read_text(encoding="utf-8")
    row = re.compile(r"^\| stamp_test_aether \| .*\n", re.M)
    assert len(row.findall(text)) == 1
    text = row.sub("", text, count=1)
    detail = ("- WORK_ITEM: stamp_test_aether\n  SWITCH_TRIGGER: The stamp test passes after the frame tests in both GIL "
              "modes, or the owner redirects.\n  RESUME_HIERARCHY:\n    - " + ACTIVE + "\n")
    assert text.count(detail) == 1
    text = text.replace(detail, "", 1)
    begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    end = "<!-- END USER-DEFINED: closed_anchors -->"
    i, j = text.index(begin) + len(begin), text.index(end)
    anchors = [line for line in text[i:j].splitlines(keepends=True) if line.startswith("| ")]
    anchors.append("| stamp_test_aether | done | melder_0 | " + DONE + " | Tests only, no notch: the managed stamp "
                   "test installs a fresh Aether per test and passes after the frame tests (GIL off and on). Next: "
                   "its tests_components entry rides the wording lane. | " + NOW + " |\n")
    while len(anchors) > 12:
        anchors.pop(0)
    text = text[:i] + "".join(anchors) + text[j:]
    board.write_text(text, encoding="utf-8")
    art = pathlib.Path("artifact_board.md")
    atext = art.read_text(encoding="utf-8")
    arow = re.compile(r"^\| " + re.escape(ACTIVE) + r" \| " + re.escape(RUN) + r" \| .*\n", re.M)
    assert len(arow.findall(atext)) == 1
    atext = arow.sub("", atext, count=1)
    cbegin = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    cleared = ("| " + DONE + " | " + RUN + " | retain_as_reference | The frame-then-stamp reproducer, its GIL-on twin and "
               "the red, green and unit-tree runs (stamp_*); kept in the wording lane's folder as this task's "
               "evidence. | " + NOW + " |\n")
    assert atext.count(cbegin) == 1
    art.write_text(atext.replace(cbegin, cbegin + cleared, 1), encoding="utf-8")


if __name__ == "__main__":
    {"notes": close_ticket, "boards": sync_boards}[STEP]()
    print("done:", STEP, NOW)
