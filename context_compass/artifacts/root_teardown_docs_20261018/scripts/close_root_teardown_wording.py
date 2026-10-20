"""
Close TASK-2026-10-19-correct_root_teardown_docs_wording and sync the boards (melder_2).

Run from context_compass/ with any Python 3.10+. Every change is computed in memory first, anchored on text that
must occur once; nothing is written unless all anchors hold. Then, in order: the ticket (MEASURE note, completion,
transition, checklists, validation, handoff) at its active path; its move to tickets/tasks/completed/; the mailbox
(M2-27 to melder_0, melder_2 departed); the attention board (the M2-27 alert, the row and detail removed, the
closed anchor added, the oldest anchor dropped at the cap of 12, two of melder_2's older anchors corrected); the
artifact board (the active row cleared as retain_as_reference). Each write is read back.
"""
import datetime
import os
import sys
from pathlib import Path

LANE = Path("artifacts/root_teardown_docs_20261018")
ACTIVE = Path("tickets/tasks/2026-10-19_correct_root_teardown_docs_wording_task.md")
DONE = Path("tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md")
MAILBOX = Path("mailbox_board.md")
ATTENTION = Path("attention_board.md")
ARTIFACTS = Path("artifact_board.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Return text with old replaced by new, refusing unless old occurs exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: anchor must occur once, found {count}: {old[:90]!r}")
    return text.replace(old, new, 1)


def write_checked(path: Path, text: str) -> None:
    """Write through a sibling temp file and os.replace, then read back."""
    tmp = path.with_name(path.name + ".m2tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    if path.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{path}: read-back differs")


def lines_of(path: Path) -> int:
    """Return the line count of a run file, for exact evidence ranges."""
    return len(path.read_text(encoding="utf-8").splitlines())


def ticket_text(ts: str) -> str:
    """Return the closed ticket's text."""
    t = ACTIVE.read_text(encoding="utf-8")
    runs = LANE / "runs"
    note = (
        f"- DATETIME: {ts}\n"
        "  AUTHOR: melder_2\n"
        "  AUTHOR_ROLE: synaptic_python_developer\n"
        "  TYPE: MEASURE\n"
        "  CLAIM: Applied and checked. correct_root_teardown_wording.py replaced the ten blocks on their exact text after\n"
        "    both documents matched their indexes: src_architecture 5418 -> 5422 lines (41 lines out, 45 in; sha256\n"
        "    b9309496bd48...), src_components 12324 -> 12325 (23 out, 24 in; 91e699b54b6d...); the multiset check found\n"
        "    no other non-blank line changed, and every new line is within 120 characters. Both indexes regenerated (62\n"
        "    sections over 5422 lines; 155 over 12325) and --check OK. \"open with the owner\", \"Known, not fixed (open\"\n"
        "    and \"two places\" occur nowhere in either document; the tooling-path leak grep finds 0 lines before and\n"
        "    after; the citation recipe reports the same two pre-existing MISSING lines (bare file names in an older\n"
        "    handoff entry, one line lower) and nothing new. Every touched block re-read in place. Not run: tests\n"
        "    (documentation only).\n"
        "  EVIDENCE:\n"
        f"  - context_compass/artifacts/root_teardown_docs_20261018/runs/preservation_correction.txt:1-{lines_of(runs / 'preservation_correction.txt')}\n"
        f"  - context_compass/artifacts/root_teardown_docs_20261018/runs/index_checks_correction.txt:1-{lines_of(runs / 'index_checks_correction.txt')}\n"
        f"  - context_compass/artifacts/root_teardown_docs_20261018/runs/leak_and_framing_correction.txt:1-{lines_of(runs / 'leak_and_framing_correction.txt')}\n"
        f"  - context_compass/artifacts/root_teardown_docs_20261018/runs/citation_recipe_correction.txt:1-{lines_of(runs / 'citation_recipe_correction.txt')}\n"
        "  - context_compass/system_docs/src_architecture.md:1159-1180\n"
        "  - context_compass/system_docs/src_components.md:3946-3953\n"
        "  IMPACT: The exit gate is met; melder_0's rebuild can carry both documents.\n"
        "  NEXT: none; M2-27 tells melder_0, and the ticket closes.\n"
        "  REREAD: HELPFUL\n"
        "  SCORE_0_TO_10: 8\n"
    )
    t = replace_once(t, "\n## Context / Handoff Summary\n", "\n" + note + "\n## Context / Handoff Summary\n", "ticket note slot")
    t = replace_once(t, "- Status: in_progress\n", "- Status: done\n", "ticket status")
    updated_start = t.index("- Updated: ")
    updated_end = t.index("\n", updated_start) + 1
    t = t[:updated_start] + (
        f"- Updated: {ts}\n"
        f"- Completed: {ts}\n"
        "- Summary: src_architecture and src_components now say a root's teardown cleans only what the root holds - its\n"
        "  stores' records and what its pools keep, the children recorded for objects still out included - and report a\n"
        "  disposal method that raises like any other; the \"open with the owner\" framing is gone. Both indexes\n"
        "  regenerated, --check OK; no src change, no notch, no release-note entry.\n"
    ) + t[updated_end:]
    t = replace_once(
        t,
        "## State Transition Event\n"
        "- from_state: ready\n"
        "- to_state: in_progress\n"
        "- transition_reason: the owner's review in chat (recorded below) showed the closed task's \"open with the owner\"\n"
        "  framing wrong; the correction is part of delivering the owner's \"update the system docs please\".\n",
        "## State Transition Event\n"
        "- from_state: in_progress\n"
        "- to_state: done\n"
        "- transition_reason: exit gate met - no \"open with the owner\" framing left in either document's teardown text;\n"
        "  both indexes regenerated, --check OK; leak grep clean; preservation: only the ten blocks changed (MEASURE\n"
        "  note); melder_0 told (M2-27). Routine closure by the assigned agent; the owner's review settled that no code\n"
        "  change is needed. Earlier: ready -> in_progress at 2026-10-19T00:23:27Z after the owner's review in chat.\n",
        "ticket transition",
    )
    t = replace_once(
        t,
        "## Validation\n- Not run.\n",
        "## Validation\n"
        "- Run: both index `--check` OK (62 sections over 5422 lines; 155 over 12325); tooling-path leak grep 0 lines;\n"
        "  preservation multiset check: only the ten blocks' lines changed; citation bounds: the 2 pre-existing MISSING,\n"
        "  none from this task (MEASURE note).\n"
        "- Not run: tests (documentation only).\n",
        "ticket validation",
    )
    if t.count("\n- [ ] ") != 12:
        raise SystemExit(f"ticket: expected 12 open checkboxes, found {t.count(chr(10) + '- [ ] ')}")
    t = t.replace("\n- [ ] ", "\n- [x] ")
    handoff_start = t.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    handoff_end = t.index("\n## Project-Specific Additions\n")
    t = t[:handoff_start] + (
        "Scope: correct the closed task's teardown framing in src_architecture and src_components. State: done at\n"
        f"{ts} - both documents say a root's teardown cleans what it holds, the children of out objects included, and\n"
        "that a disposal method raising during teardown is reported; both indexes regenerated and checked; melder_0's\n"
        "rebuild carries it (M2-27). Nothing owed.\n"
    ) + t[handoff_end:]
    return t


def main() -> None:
    """Compute every change, then write in order."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if DONE.exists():
        raise SystemExit(f"{DONE} exists; nothing applied.")
    new_ticket = ticket_text(ts)

    mailbox = MAILBOX.read_text(encoding="utf-8")
    roster_start = mailbox.index("| melder_2 | claude | 2026-10-18T21:07:02Z | ")
    roster_end = mailbox.index("\n", roster_start) + 1
    if not mailbox[roster_start:roster_end].endswith("| active |\n"):
        raise SystemExit("roster row is not active")
    mailbox = mailbox[:roster_start] + f"| melder_2 | claude | 2026-10-18T21:07:02Z | {ts} | departed |\n" + mailbox[roster_end:]
    m2_27 = (
        "- TO: melder_0\n"
        "  FROM: melder_2\n"
        f"  DATETIME: {ts}\n"
        "  TYPE: NOTICE\n"
        "  CLAIM: M2-27, re M2-26: the correction is on the tree and your rebuild may run whenever your turn-in reaches\n"
        "    it. src_architecture 5422 lines (b9309496bd48...), src_components 12325 lines (91e699b54b6d...), both indexes\n"
        "    regenerated and --check OK; only my teardown text changed (preservation checked), no other file of yours.\n"
        "    My lane is closed and I am checking out.\n"
        "  EVIDENCE: context_compass/tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md\n"
        "  ACK_REQUESTED: false\n"
    )
    mailbox = replace_once(mailbox, "<!-- END USER-DEFINED: messages -->\n", m2_27 + "<!-- END USER-DEFINED: messages -->\n",
                           "messages end")

    attention = ATTENTION.read_text(encoding="utf-8")
    attention = replace_once(attention, "<!-- END USER-DEFINED: alerts -->\n",
                             f"- NEW MESSAGE for melder_0 (from melder_2, {ts})\n<!-- END USER-DEFINED: alerts -->\n", "alerts end")
    row_start = attention.index("| root_teardown_wording | in_progress | implementation | claude | melder_2 |")
    row_end = attention.index("\n", row_start) + 1
    attention = attention[:row_start] + attention[row_end:]
    attention = replace_once(
        attention,
        "- WORK_ITEM: root_teardown_wording\n"
        "  SWITCH_TRIGGER: Both indexes --check OK, leak check clean, melder_0 told its rebuild may run.\n"
        "  RESUME_HIERARCHY:\n"
        "    - tickets/tasks/2026-10-19_correct_root_teardown_docs_wording_task.md\n",
        "", "detail entry")
    attention = replace_once(
        attention,
        "src_architecture and src_components state the owner's rule that a root's teardown cleans only what it holds, "
        "today's order and two places open with the owner. Next: the owner's call on the two code changes. |",
        "src_architecture and src_components state the owner's rule that a root's teardown cleans only what it holds and "
        "today's order (its \"open with the owner\" framing corrected by TASK-2026-10-19-correct_root_teardown_docs_wording). "
        "Next: none. |",
        "old anchor note")
    attention = replace_once(
        attention,
        "Next: the owner's answer on the root-held consumer teardown order. |",
        "Next: none (the owner answered: a root's teardown cleans only what it holds). |",
        "epic anchor note")
    anchor = ("| root_teardown_wording | done | melder_2 | tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md "
              "| Documentation only, no src change: after the owner's review both documents say a root's teardown cleans what "
              "it holds (the children of out objects included) and that a raising disposal method is reported; the \"open "
              f"with the owner\" framing is gone. Next: none. | {ts} |\n")
    attention = replace_once(attention, "<!-- END USER-DEFINED: closed_anchors -->\n",
                             anchor + "<!-- END USER-DEFINED: closed_anchors -->\n", "anchors end")
    region_start = attention.index("<!-- BEGIN USER-DEFINED: closed_anchors -->\n") + len("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")
    region_end = attention.index("<!-- END USER-DEFINED: closed_anchors -->\n")
    rows = attention[region_start:region_end].splitlines(keepends=True)
    while len(rows) > 12:
        oldest = min(rows, key=lambda r: r.rstrip("\n").rstrip(" |").rsplit("| ", 1)[-1].strip())
        rows.remove(oldest)
        sys.stdout.write("dropped anchor: " + oldest.split("|")[1].strip() + "\n")
    attention = attention[:region_start] + "".join(rows) + attention[region_end:]

    artifacts = ARTIFACTS.read_text(encoding="utf-8")
    art_start = artifacts.index("| tickets/tasks/2026-10-19_correct_root_teardown_docs_wording_task.md | artifacts/root_teardown_docs_20261018/ |")
    art_end = artifacts.index("\n", art_start) + 1
    artifacts = artifacts[:art_start] + artifacts[art_end:]
    cleared = ("| tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md | artifacts/root_teardown_docs_20261018/ "
               "| retain_as_reference | Task closed (documentation only): the routing, correction and closure scripts, the "
               "before-copies (before_correction/) and the preservation, index, leak and citation checks (runs/*_correction.txt) "
               f"join the closed task's evidence. | {ts} |\n")
    artifacts = replace_once(artifacts, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                             "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "cleared start")

    write_checked(ACTIVE, new_ticket)
    os.replace(ACTIVE, DONE)
    if ACTIVE.exists() or DONE.read_text(encoding="utf-8") != new_ticket:
        raise SystemExit("ticket move failed")
    write_checked(MAILBOX, mailbox)
    write_checked(ATTENTION, attention)
    write_checked(ARTIFACTS, artifacts)
    sys.stdout.write(f"closed at {ts}\n")


if __name__ == "__main__":
    main()
