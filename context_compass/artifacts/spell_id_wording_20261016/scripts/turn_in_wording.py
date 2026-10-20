"""Turn in TASK-2026-10-16-spell_id_wording_near_spell_index (the owner, chat 2026-10-17).

Run from the repository root, in this order:
    python .../turn_in_wording.py <NOW> notch    # __version__ +1 notch, the release-note header, bullet, rebuild line
    python .../turn_in_wording.py <NOW> close    # successor in backlog, closure, mv -n, boards
then the rebuild (assets and LLM bundles, each with --check), last; then
    python .../turn_in_wording.py <NOW> notice   # NOTICE M0-183 to melder_1: __version__.py and the note are free
The notch step needs melder_1's go-ahead for __version__.py and the release note (QUESTION M0-180).
"""
import pathlib
import re
import subprocess
import sys

NOW, STEP = sys.argv[1], sys.argv[2]
CC = pathlib.Path("context_compass")
LANE = CC / "artifacts/spell_id_wording_20261016"
ACTIVE = "tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md"
DONE = "tickets/tasks/completed/2026-10-16_spell_id_wording_near_spell_index_task.md"
SUCCESSOR = "tickets/tasks/backlog/2026-10-17_spell_id_wording_in_held_files_task.md"
STATE = LANE / "notes/turn_in_state.txt"


def notch() -> None:
    """Take the next notch above what __version__ reads now; header, bullet and rebuild line of the running note."""
    vfile = pathlib.Path("src/melder/__version__.py")
    vtext = vfile.read_bytes().decode("utf-8")
    current = re.search(r'__version__ = "0\.2\.(\d{4})"', vtext)
    assert current, "unexpected __version__ format"
    new = "0.2.%04d" % (int(current.group(1)) + 1)
    vfile.write_bytes(vtext.replace(current.group(0), '__version__ = "%s"' % new, 1).encode("utf-8"))
    note = pathlib.Path("release_docs/next_version_release.md")
    raw = note.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace(nl, "\n")
    lines = text.split("\n")
    assert lines[0].startswith("# Melder ") and lines[2] == "**Unreleased**", lines[:3]
    lines[0] = "# Melder " + new
    text = "\n".join(lines)
    rebuild = re.compile(r"^- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for "
                         r"0\.2\.\d{4}\.$", re.M)
    assert len(rebuild.findall(text)) == 1
    bullet = ("- Docstrings and comments that called a spell's id a \"version id\" now name it the `spell_id` (the id "
              "`bind`\n  and `bind_inactive` return); the Phase 6 diagnostic `identity_mixing_detected` ends \"instead "
              "of a\n  spell_id.\" where it said \"instead of a version id.\"\n")
    text = rebuild.sub(lambda m: bullet + "- Agent documentation metadata and the whole-repository LLM bundles are "
                       "rebuilt for " + new + ".", text, count=1)
    note.write_bytes(text.replace("\n", nl).encode("utf-8"))
    STATE.write_text(new + "\n", encoding="utf-8")
    print("notched", current.group(0), "->", new)


def make_successor() -> None:
    """Write the backlog successor from its body file and the task template's fixed sections."""
    path = CC / SUCCESSOR
    assert not path.exists(), "successor exists"
    template = (CC / "templates/task_template.md").read_text(encoding="utf-8")

    def block(start: str, end: str) -> str:
        i = template.index(start)
        return template[i:template.index(end, i)]

    body = (LANE / "notes/successor_ticket_body.txt").read_text(encoding="utf-8")
    body = body.replace("@@DONE@@\n", block("## Done Checklist", "## Artifact Links (Optional)"))
    body = body.replace("@@NOTING@@\n", block("## Noting Behavior", "## Contribution Attribution"))
    body = body.replace("@@TAIL@@\n", template[template.index("## Project-Specific Additions"):])
    body = body.replace("@@NOW@@", NOW)
    assert all(len(line) <= 120 for line in body.splitlines())
    path.write_text(body, encoding="utf-8")


def close_ticket(new: str) -> None:
    """Completion header, state, checklists and resume view of the wording ticket (still at its active path)."""
    ticket = CC / ACTIVE
    raw = ticket.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace(nl, "\n")
    title = "# Task: spell_id_wording_near_spell_index - name the id where \"version id\" meets the spell index\n"
    header = (title + "\n- Completed: " + NOW + "\n"
              "- Summary: notched " + new + " - \"version id\" named by hand as the `spell_id` in 214 docstring, "
              "comment and\n  test lines of 113 files nobody else held; IdentityMixingStrategy's diagnostic ends "
              "\"instead of a\n  spell_id.\"; the owner's double check found no \"version id\" meaning another id. "
              "Release-note bullet in\n  \"Packaging and documentation\". The 127 held rewrites, 5 kept lines and "
              "the tests_components entry\n  moved to TASK-2026-10-17-spell_id_wording_in_held_files (backlog, "
              "blocked on melder_1's release).\n  Turned in on the owner's word (chat 2026-10-17); rebuilt last.\n")
    pairs = [
        (title, header),
        ("- Status: blocked\n", "- Status: done\n"),
        ("- [ ] After melder_1 releases its files", "- [x] After melder_1 releases its files"),
        ("- [ ] Notch, release-note bullet, closure, the rebuild last.",
         "- [x] Notch, release-note bullet, closure, the rebuild last."),
        ("- [ ] Run Ticket Microcycle", "- [x] Run Ticket Microcycle"),
        ("- [ ] Record meaningful attributed findings", "- [x] Record meaningful attributed findings"),
    ]
    for old, new_text in pairs:
        assert text.count(old) == 1, old[:70]
        text = text.replace(old, new_text, 1)
    text, updated = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, text, count=1)
    assert updated == 1
    validation_old = "## Validation\n- Not run.\n- Recommended commands:\n"
    validation_new = ("## Validation\n- Run on the landed scope (MEASURE notes 2026-10-16T18:56:42Z, 19:11:31Z, "
                      "20:06:44Z): py_compile of every\n  touched file; the touched files' unit, component and "
                      "integration tests with the GIL off and on, green but\n  for a pre-existing order dependence "
                      "(fixed by TASK-2026-10-16-stamp_test_boots_its_own_aether). At turn-in:\n  the asset and LLM "
                      "bundle rebuilds, each with its --check. Not run: the whole test tree.\n- Commands used:\n")
    assert text.count(validation_old) == 1
    text = text.replace(validation_old, validation_new, 1)
    for section in ("## Applicable Anti-Patterns\n", "## Done Checklist\n"):
        start = text.index(section) + len(section)
        end = text.index("\n## ", start)
        assert text[start:end].count("- [ ] ") >= 3
        text = text[:start] + text[start:end].replace("- [ ] ", "- [x] ") + text[end:]
    text = text.replace("- [x] After melder_1 releases its files: the same for them, the system docs, the graph and "
                        "the release note.",
                        "- [x] After melder_1 releases its files: the same for them, the system docs, the graph and "
                        "the release note\n      (handed to TASK-2026-10-17-spell_id_wording_in_held_files at "
                        "turn-in).", 1)
    start = text.index("## State Transition Event\n") + len("## State Transition Event\n")
    end = text.index("\n## Steps / Checklist", start)
    text = text[:start] + ("- from_state: blocked\n- to_state: done\n- transition_reason: turned in on the owner's "
                           "word (chat 2026-10-17, \"turn in your old tickets\"):\n  notched " + new + " for the "
                           "landed free scope; the held scope moved to a backlog successor.\n") + text[end:]
    start = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    end = text.index("\n## Project-Specific Additions", start)
    view = ("- Scope: \"version id\" named by hand where it relates to a spell index (owner, 2026-10-16); wording "
            "only.\n- State: done (melder_0), " + NOW + ", notched " + new + ". Landed: 214 lines in 113 files "
            "(the owner's\n  commits 192482b4c and 5ac69ab51). Handed over: 127 rewrites, 5 kept lines and the "
            "tests_components\n  entry, to TASK-2026-10-17-spell_id_wording_in_held_files (backlog, blocked on "
            "melder_1's release).\n- Open for the owner: whether \"version identity\" is reworded too (DECISION, "
            "2026-10-16T20:03:17Z).\n- Evidence: the Notes; artifacts/spell_id_wording_20261016/.\n"
            "- Next: none in this ticket.\n")
    text = text[:start] + view + text[end:]
    long = [line for line in text.splitlines() if len(line) > 120 and "artifacts/" not in line
            and "benchmarks/" not in line]
    assert not long, long
    ticket.write_bytes(text.replace("\n", nl).encode("utf-8"))


def sync_boards(new: str) -> None:
    """Remove the row and detail, add the anchor (cap 12), repoint the artifact row and add the cleared row."""
    board = CC / "attention_board.md"
    text = board.read_text(encoding="utf-8")
    row = re.compile(r"^\| spell_id_wording \| .*\n", re.M)
    assert len(row.findall(text)) == 1
    text = row.sub("", text, count=1)
    detail = ("- WORK_ITEM: spell_id_wording\n  SWITCH_TRIGGER: The wording lands with its notch, release note and "
              "rebuild, or the owner redirects.\n  RESUME_HIERARCHY:\n    - " + ACTIVE + "\n")
    assert text.count(detail) == 1
    text = text.replace(detail, "", 1)
    begin, end = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n", "<!-- END USER-DEFINED: closed_anchors -->"
    i, j = text.index(begin) + len(begin), text.index(end)
    anchors = [line for line in text[i:j].splitlines(keepends=True) if line.startswith("| ")]
    anchors.append("| spell_id_wording | done | melder_0 | " + DONE + " | Landed " + new + " (\"version id\" named "
                   "as the spell_id in 214 lines of 113 files). Turned in on the owner's word. Next: "
                   "TASK-2026-10-17-spell_id_wording_in_held_files (backlog) after melder_1's release. | " + NOW + " |\n")
    while len(anchors) > 12:
        anchors.pop(0)
    text = text[:i] + "".join(anchors) + text[j:]
    board.write_text(text, encoding="utf-8")
    art = CC / "artifact_board.md"
    atext = art.read_text(encoding="utf-8")
    old_row = re.compile(r"^\| " + re.escape(ACTIVE) + r" \| artifacts/spell_id_wording_20261016/ \| .*\n", re.M)
    assert len(old_row.findall(atext)) == 1
    atext = old_row.sub("| " + SUCCESSOR + " | artifacts/spell_id_wording_20261016/ | investigation_evidence | backlog | "
                        "retain_as_reference | The inventory with its supplement, the per-occurrence decisions, the "
                        "audit, the scripts and runs; re-inventory the held files before applying. | " + NOW
                        + " | REQUIRED |\n", atext, count=1)
    cbegin = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    atext = atext.replace(cbegin, cbegin + "| " + DONE + " | artifacts/spell_id_wording_20261016/ | retain_as_reference "
                          "| Evidence of the " + new + " landing (inventory, decisions, audit, apply and closure "
                          "scripts, runs, rebuild logs); the folder stays rowed under the backlog successor. | " + NOW
                          + " |\n", 1)
    art.write_text(atext, encoding="utf-8")


def notice() -> None:
    """After the rebuild: NOTICE M0-183 to melder_1 and its alert - __version__.py and the release note are free."""
    new = STATE.read_text(encoding="utf-8").strip()
    mb = CC / "mailbox_board.md"
    mtext = mb.read_text(encoding="utf-8")
    message = ("- TO: melder_1\n  FROM: melder_0\n  DATETIME: " + NOW + "\n  TYPE: NOTICE\n  CLAIM: M0-183, re M1-24. "
               "Done: melder_0 notched " + new + " (\"version id\" named as the spell_id in docstrings\n    and "
               "comments of 113 files nobody held; IdentityMixingStrategy's diagnostic), added one bullet before the "
               "rebuild\n    line of the release note's \"Packaging and documentation\" and rebuilt (both checks OK). "
               "__version__.py and\n    the release note are yours again; notch above " + new + " if you land after. "
               "The rewording of your held\n    files waits in TASK-2026-10-17-spell_id_wording_in_held_files (backlog) "
               "for your release NOTICE.\n  EVIDENCE: context_compass/" + DONE + "\n  ACK_REQUESTED: false\n")
    assert all(len(line) <= 120 for line in message.splitlines() if "context_compass/" not in line)
    end_marker = "<!-- END USER-DEFINED: messages -->"
    assert mtext.count(end_marker) == 1
    mb.write_text(mtext.replace(end_marker, message + end_marker, 1), encoding="utf-8")
    board = CC / "attention_board.md"
    text = board.read_text(encoding="utf-8")
    end_alerts = "<!-- END USER-DEFINED: alerts -->"
    assert text.count(end_alerts) == 1
    text = text.replace(end_alerts, "- NEW MESSAGE for melder_1 (from melder_0, " + NOW + ")\n" + end_alerts, 1)
    board.write_text(text, encoding="utf-8")
    print("sent M0-183", NOW)


def close() -> None:
    """Successor, closure, move, boards."""
    new = STATE.read_text(encoding="utf-8").strip()
    make_successor()
    close_ticket(new)
    moved = subprocess.run(["mv", "-n", str(CC / ACTIVE), str(CC / DONE)], check=True)
    assert (CC / DONE).exists() and not (CC / ACTIVE).exists(), moved
    sync_boards(new)
    print("closed", DONE, "successor", SUCCESSOR, new)


if __name__ == "__main__":
    {"notch": notch, "close": close, "notice": notice}[STEP]()
