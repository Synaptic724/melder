"""Close TASK-2026-10-16-public_notch_target_for_staged_versions (0.2.8249 with the owner's extension).

Run from context_compass/:  python close_task_extension.py <NOW>
Edits the ticket (completion summary, status, state transition, checklists, validation, artifact links,
attribution, the final resume view), moves it to tickets/tasks/completed/ without ever overwriting, syncs the
attention board (row, detail, anchors, notch notice, the message alert) and the artifact board (the folder and
patch rows to cleared) and appends NOTICE M0-177 to the mailbox. Every replacement must match exactly once,
every file keeps LF, and no prose line the script adds to the ticket exceeds 120 characters.
"""
import os
import pathlib
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md")
DONE = pathlib.Path("tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md")


def edit(path: pathlib.Path, pairs: list) -> None:
    """
    Replace each old text exactly once in an LF file.

    Args:
        path: The file.
        pairs: (old, new) pairs.
    """
    text = path.read_text(encoding="utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        count = text.count(old)
        assert count == 1, (str(path), count, old[:80])
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def ticket_edits() -> list:
    """Return the ticket's (old, new) pairs."""
    return [
        ("# Task: public_notch_target_for_staged_versions - a public way to notch to a staged version\n\n## Metadata\n",
         "# Task: public_notch_target_for_staged_versions - a public way to notch to a staged version\n\n"
         "- Completed: " + NOW + "\n"
         "- Summary: notched 0.2.8249 - `Conduit.notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take\n"
         "  `spell_id=` (the spell_id `bind` or `bind_inactive` returned) beside `spell=`, and a notch checks its target\n"
         "  before and inside its transaction; the README loop and the docs run on public calls. Release-note section\n"
         "  \"`notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks its\n"
         "  target\". Targeted suites green with the GIL off and on; the whole tree not run; the rebuild runs last.\n\n"
         "## Metadata\n"),
        ("- Status: in_progress\n", "- Status: done\n"),
        ("""## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner chose option A (chat 2026-10-16: "just use the private version if its inside the
  public call thats reasonable") and directed this task next ("continue onto the next stuff please"); melder_0
  took it out of the backlog. Previous: draft -> draft at creation, from S8's finding, the owner's design choice
  first ("if you found more bugs just add tickets", 2026-10-16).
""",
         """## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every EXIT_GATE item but the rebuild checks is recorded in the Notes - the README loop on
  public calls and the tests green with the GIL off and on (13:28:26Z, 13:41:41Z, 15:23:08Z), the docs, system
  docs, graph and release note (14:15:44Z, 15:41:00Z, 15:53:41Z), the notch 0.2.8249 (14:23:00Z) - and the
  owner's extension landed in the same notch (15:04:47Z, 15:23:08Z). The rebuild runs last, after this closure,
  as the contribution guide orders, and its checks are recorded in a note below. Closed under the owner's
  standing direction to carry on ("continue onto the next stuff please"); no reserved decision is open.
- prior: draft -> in_progress (2026-10-16T12:33:09Z): the owner chose option A (chat 2026-10-16: "just use the
  private version if its inside the public call thats reasonable") and directed this task next ("continue onto
  the next stuff please"); melder_0 took it out of the backlog. Previous: draft -> draft at creation, from S8's
  finding, the owner's design choice first ("if you found more bugs just add tickets", 2026-10-16).
"""),
        ("- [ ] Component patch and mapping note;", "- [x] Component patch and mapping note;"),
        ("- [ ] README sketch and docs/expert/governed-change.md run as written;",
         "- [x] README sketch and docs/expert/governed-change.md run as written;"),
        ("- [ ] Extension (owner, 2026-10-16):", "- [x] Extension (owner, 2026-10-16):"),
        ("- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:"),
        ("- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence",
         "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence"),
        ("""## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 -m pytest <the new tests>; python -X gil=1 -m pytest <the new tests>
  - python -X gil=0 <the README-loop probe>
""",
         """## Validation
- Run on Python 3.14.7t with the GIL off and on: the 52 tests of the four new files;
  tests/unit/melder/aether/conduit (1455 passed) and tests/integration/melder/aether/conduit (130 passed); the
  index-move callers (crystallizer membership and the find-by-id component test, 22 passed); GIL off, the
  crystallizer notch callers (5 passed, 3 xfailed as before); the notch callers listed in the 13:28:26Z note;
  the README-loop, release-note and today probes; expert lessons 17 and 26.
- Not run: the whole tree.
"""),
        ("""- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
""",
         """- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
"""),
        ("""- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.
""",
         """- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.
"""),
        ("""  - system_docs/patches/active/public_notch_target_2026_10_16/architecture_patch.md
  - system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md
  - system_docs/patches/active/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md
  - system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_index_move_target.md
""",
         """  - system_docs/patches/completed/public_notch_target_2026_10_16/architecture_patch.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/component_patch_conduit_index_move_target.md
"""),
        ("""- CLEANUP_TRIGGER: at closure the patch docs are promoted into the system docs and archived under
  system_docs/patches/completed/; the folder stays as the lane's evidence
""",
         """- CLEANUP_TRIGGER: done at closure (2026-10-16): the patch docs were promoted into the system docs and archived
  under system_docs/patches/completed/; the folder stays as the lane's evidence
"""),
        ("- Independent Review: none yet\n",
         "- Independent Review: none (self-checks only; closed under the owner's standing direction)\n"),
    ]


SUMMARY_OLD_START = "## Context / Handoff Summary\n"
SUMMARY_NEW = """## Context / Handoff Summary
- Scope and outcome: done. `Conduit.notch_spell(spell_index=..., spell_id=...)` - option A, the owner's choice -
  runs the stage -> notch -> meld loop on public calls, its target checked before and inside the transaction; on
  the owner's extension `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` too, and the lane's
  text says spell_id. Notched 0.2.8249; release-note section "`notch_spell`, `add_to_spell_index` and
  `remove_from_spell_index` take a `spell_id`; a notch checks its target".
- Evidence: Notes 11:42:41Z-15:53:41Z; the lane folder artifacts/public_notch_target_20261016/; the patch docs in
  system_docs/patches/completed/public_notch_target_2026_10_16/.
- Owners: conduit.py is released to melder_1 at this closure (NOTICE M0-177); spellbook.py and
  transfer_of_ownership.py are melder_1's.
- Limits: the whole tree was not run (the suites run are in the 13:28:26Z and 15:23:08Z notes). "version id" text
  outside this lane is left as written: the release note's 0.2.8229 lookup sections (lines 46 and 656) and the
  docstrings of `Spellbook._get_owned_spell` and `Conduit._deactivate_borrowed_spell`.
- Follow-ups: TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog; the seam's park-first order, in
  spellbook.py); the INTENT wording in spellbook.py's `_notch_spell` / `_apply_notch` docstrings, told to melder_1.
- Next: the rebuild (assets and LLM bundles), last; its checks are noted here.

"""


def close_ticket() -> None:
    """Edit the ticket, replace its resume view, update Updated, check line widths, move it to completed/."""
    before = set(TICKET.read_text(encoding="utf-8").split("\n"))
    edit(TICKET, ticket_edits())
    text = TICKET.read_text(encoding="utf-8")
    start = text.index(SUMMARY_OLD_START)
    end = text.index("## Project-Specific Additions\n")
    text = text[:start] + SUMMARY_NEW + text[end:]
    lines = text.split("\n")
    updated = [i for i, line in enumerate(lines) if line.startswith("- Updated: ")]
    assert len(updated) == 1
    lines[updated[0]] = "- Updated: " + NOW
    long_new = [line for line in lines if line not in before and len(line) > 120]
    assert not long_new, long_new
    TICKET.write_text("\n".join(lines), encoding="utf-8")
    assert not DONE.exists()
    os.rename(TICKET, DONE)


def sync_attention_board() -> None:
    """Remove the row and its detail, rotate the anchors, update the notch notice and add the message alert."""
    board = pathlib.Path("attention_board.md")
    text = board.read_text(encoding="utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    rows = [i for i, line in enumerate(lines) if line.startswith("| public_notch_target |")]
    assert len(rows) == 1
    del lines[rows[0]]
    text = "\n".join(lines)
    detail = """- WORK_ITEM: public_notch_target
  SWITCH_TRIGGER: The change lands with tests, docs, the next notch and the rebuild, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md
"""
    assert text.count(detail) == 1
    text = text.replace(detail, "", 1)
    oldest = [line for line in text.split("\n") if line.startswith("| notch_borrower_docs |")]
    assert len(oldest) == 1
    text = text.replace(oldest[0] + "\n", "", 1)
    anchor = ("| public_notch_target | done | melder_0 | "
              "tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md | Landed 0.2.8249 "
              "(`notch_spell` by spell_id with its target checked; on the owner's extension `add_to_spell_index` / "
              "`remove_from_spell_index` by spell_id too). Next: the rebuild; conduit.py released to melder_1. | "
              + NOW + " |")
    end_anchors = "<!-- END USER-DEFINED: closed_anchors -->"
    assert text.count(end_anchors) == 1
    text = text.replace(end_anchors, anchor + "\n" + end_anchors, 1)
    region = text[text.index("<!-- BEGIN USER-DEFINED: closed_anchors -->"):text.index(end_anchors)]
    assert sum(1 for line in region.split("\n") if line.startswith("| ")) == 12
    notice_old = """- melder_0 landed 0.2.8249 (`Conduit.notch_spell` takes `spell_id=` - the id `bind` or `bind_inactive` returned -
  beside `spell=`, exactly one, and checks its target before and inside its transaction;
  TASK-2026-10-16-public_notch_target_for_staged_versions). Notch above it if you land after.
"""
    notice_new = """- melder_0 landed 0.2.8249 (`Conduit.notch_spell` takes `spell_id=` - the spell_id `bind` or `bind_inactive`
  returned - beside `spell=`, exactly one, and checks its target before and inside its transaction; on the owner's
  extension `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` too;
  TASK-2026-10-16-public_notch_target_for_staged_versions). Notch above it if you land after.
"""
    assert text.count(notice_old) == 1
    text = text.replace(notice_old, notice_new, 1)
    end_alerts = "<!-- END USER-DEFINED: alerts -->"
    assert text.count(end_alerts) == 1
    text = text.replace(end_alerts, "- NEW MESSAGE for melder_1 (from melder_0, " + NOW + ")\n" + end_alerts, 1)
    board.write_text(text, encoding="utf-8")


def sync_artifact_board() -> None:
    """Move the folder row and the four patch rows to one cleared row each (the folder, the archived lane)."""
    board = pathlib.Path("artifact_board.md")
    text = board.read_text(encoding="utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    prefix = "| tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md |"
    ours = [line for line in lines if line.startswith(prefix)]
    assert len(ours) == 5, len(ours)
    lines = [line for line in lines if not line.startswith(prefix)]
    text = "\n".join(lines)
    done = "tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md"
    cleared = [
        "| " + done + " | system_docs/patches/completed/public_notch_target_2026_10_16/ | promote_to_documentation | "
        "Promoted at landing (0.2.8249: the notch target and, on the owner's extension, the index moves by spell_id) "
        "to src_architecture, src_components, tests_components and tests_architecture with their indexes, and to the "
        "graph; the four patch docs (architecture, two component, one code-description) archived. | " + NOW + " |",
        "| " + done + " | artifacts/public_notch_target_20261016/ | retain_as_reference | Evidence of the 0.2.8249 "
        "landing: the today, README-loop and release-note probes with their runs; red, green and suite runs of the "
        "notch target and the owner's extension; docs baselines; the apply, wording, docs, graph, release-note, "
        "archive and closure scripts; the notes; the rebuild logs. The today probe also stays rowed under the backlog "
        "seam task. | " + NOW + " |",
    ]
    start = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->"
    assert text.count(start) == 1
    text = text.replace(start, start + "\n" + "\n".join(cleared), 1)
    board.write_text(text, encoding="utf-8")


def send_notice() -> None:
    """Append NOTICE M0-177 to melder_1 at the end of the mailbox's Messages region."""
    board = pathlib.Path("mailbox_board.md")
    message = """- TO: melder_1
  FROM: melder_0
  DATETIME: """ + NOW + """
  TYPE: NOTICE
  CLAIM: M0-177. TASK-2026-10-16-public_notch_target_for_staged_versions landed as 0.2.8249 and is closed:
    notch_spell, add_to_spell_index and remove_from_spell_index take spell_id= (a notch checks its target).
    conduit.py is yours now; your D3 lines notch above 0.2.8249. I still run the rebuild (assets, LLM bundles),
    then hold no file. FYI: spellbook.py's _notch_spell/_apply_notch docstrings say the notch claims the Book
    INTENT; the notch strategy claims it EXCLUSIVE. codex_mcp is off (owner): mailbox only.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md
  - src/melder/aether/conduit/conduit.py:5622-6257
  - src/melder/aether/spellbook/spellbook.py:3775-3838
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:239-269
  ACK_REQUESTED: false
"""
    end = "<!-- END USER-DEFINED: messages -->"
    edit(board, [(end, message + end)])


def main() -> None:
    """Close the ticket, sync both boards, send the notice."""
    close_ticket()
    sync_attention_board()
    sync_artifact_board()
    send_notice()
    print("closed:", DONE)


if __name__ == "__main__":
    main()
