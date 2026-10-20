"""
Close TASK-2026-10-15-trace_meld_contract_scan_gate, open its successor fix task and route it (melder_1, 2026-10-15).

Usage (from the repository root): python3 <this file> <now>
Edits the investigation task (owner's pick note, steps, validation, checklists, transition, completion block, handoff),
writes the successor task, replaces the attention-board row and detail with the successor route, appends the closed
anchor (dropping the oldest to keep 12), re-points the artifact row at the successor and records the cleared row, and
records in EPIC-2026-10-05-melder_services_and_pools that the owner's direction supersedes its memo plan (decision log,
milestone, story and task lines, a Note, the handoff). The caller moves the closed task with mv -n.
Every replacement asserts one match; nothing is written unless every edit succeeds.
"""
import pathlib
import sys

CC = pathlib.Path("context_compass")
OLD_REL = "tickets/tasks/2026-10-15_trace_meld_contract_scan_gate_task.md"
DONE_REL = "tickets/tasks/completed/2026-10-15_trace_meld_contract_scan_gate_task.md"
NEW_REL = "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
NEW_ID = "TASK-2026-10-15-make_meld_state_checks_follow_spell_state"
EPIC_REL = "tickets/epics/2026-10-05_melder_services_and_pools_epic.md"
FOLDER = "artifacts/meld_contract_scan_20261015/"
PATCH = "system_docs/patches/active/meld_state_gate_2026_10_15/"


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of old with new, or fail."""
    assert text.count(old) == 1, (text.count(old), old[:80])
    return text.replace(old, new, 1)


def width(block: str) -> None:
    """Fail on a line over 120 characters unless it is an evidence path or a table row."""
    for line in block.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/", "|")), (len(line), line)


def line_of(text: str, marker: str) -> int:
    """Return the 1-based line number of the one line that starts with marker."""
    hits = [i for i, line in enumerate(text.split("\n"), 1) if line.startswith(marker)]
    assert len(hits) == 1, (marker, hits)
    return hits[0]


def close_old(text: str, now: str) -> str:
    """Record the owner's pick and close the investigation task."""
    note = f"""- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner's pick (chat 2026-10-15): "thats an issue we need to address ... those spells are meant to be
    unresolvable and are meant to just be observable by nexus so lets figure this out". The question is answered and
    the trace is complete; the fix and its design move to {NEW_ID},
    which takes this task's findings, its probes and its evidence folder. Closed by its assigned agent; no review asked.
  EVIDENCE:
  - {CC}/{NEW_REL}:1-20
  IMPACT: The board routes the successor; this task's Notes are the reference for the fix's design.
  NEXT: None here; the successor reads the code paths the fix touches and proposes the design.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""
    width(note)
    text = one(text, "\n\n## Context / Handoff Summary\n", "\n" + note + "\n## Context / Handoff Summary\n")
    text = one(text, "- Status: in_progress\n", "- Status: done\n")
    start = text.index("- Updated: ")
    end = text.index("\n", start) + 1
    block = (
        f"- Updated: {now}\n\n"
        f"- Completed: {now}\n"
        "- Summary: Investigation only. The meld gate's SpellContract scan is unconditional since 438efc387\n"
        "  (2026-01-28); the Book-wide validation flag clears once every visible spell resolves, but a resolvable=False\n"
        "  definition pins it for good and a late bind until its first meld, and then every meld scans (~21 us of 23).\n"
        f"  The owner directed the fix: successor {NEW_ID}.\n"
    )
    width(block)
    text = text[:start] + block + text[end:]
    assert "- transition_reason: the owner directed the investigation" in text
    j = text.index("\n## Steps / Checklist")
    event = (
        "- from_state: in_progress\n"
        "- to_state: done\n"
        "- transition_reason: the claim is answered from the code, the history and two probes, and the owner picked the\n"
        "  fix (chat 2026-10-15); the successor task carries it.\n"
    )
    width(event)
    text = text[:j] + "\n" + event + text[j:]
    text = one(text, "- [ ] Answer the owner; record his pick.", "- [x] Answer the owner; record his pick.")
    text = one(text, "- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:")
    text = one(text, "- [ ] Record meaningful attributed findings", "- [x] Record meaningful attributed findings")
    validation = (
        f"- Git history read with GIT_OPTIONAL_LOCKS=0; no index lock appeared ({FOLDER}git_*.txt).\n"
        f"- Probes on the live repo, Python 3.14.7t, GIL off and on, in {FOLDER}runs/:\n"
        "  probe_gil0.txt, probe_gil1.txt and probe_flag_recovery_gil0.txt. No test suite run: nothing in src/ changed.\n"
    )
    width(validation)
    text = one(text, "- Not run.\n- Recommended commands:\n", validation + "- Recommended commands:\n")
    for item in (
        "No status transition without evidence-backed transition reason.",
        "No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
        "No closure without delegated acceptance or reserved-owner disposition and board-sync completion.",
    ):
        text = one(text, f"- [ ] {item}", f"- [x] {item}")
    d0 = text.index("## Done Checklist\n")
    d1 = text.index("## Artifact Links (Optional)\n")
    section = text[d0:d1]
    assert section.count("- [ ] ") == 9
    text = text[:d0] + section.replace("- [ ] ", "- [x] ") + text[d1:]
    text = one(text, "- CLEANUP_TRIGGER: decided at closure\n",
               "- CLEANUP_TRIGGER: none - the folder stays rowed under the successor task\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    handoff = (
        f"Done ({now}). The scan, the Book-wide flag that admits it and its history are recorded in Notes, with two\n"
        f"probes. Next: {NEW_ID} (the fix and its design).\n"
    )
    width(handoff)
    return text[:h0] + handoff + text[h1:]


def new_task(now: str, notes_range: str) -> str:
    """Return the successor fix task."""
    return f"""# Task: Keep resolvable=False spells out of the meld gate and run the contract check only when a spell's state calls for it

## Metadata
- Task ID: {NEW_ID}
- Story: none - standalone; follows TASK-2026-10-15-trace_meld_contract_scan_gate (done); supersedes the memo plan
  (STORY-TBD-meld_contract_scan_memo) of EPIC-2026-10-05-melder_services_and_pools
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {now}
- Updated: {now}

## Objective
Two rules from the owner (chat 2026-10-15). Spells bound resolvable=False are deliberate - meant to stay
unresolvable and only observable by Nexus - so they must be excluded from the meld state checks; today RiskManager
counts them, and one such spell keeps the Book-wide validation flag up for the Book's life. And a spell's own state
must decide when the SpellContract check runs: skip fast, no `inspect.signature` on every meld or for every spell.
Design first, with the owner ("lets figure this out"); no `src/` edit before he approves the design.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; the code paths are read whole and recorded; the owner approves the
  design; before any `src/` edit, the patch docs under {PATCH}
  exist and are linked.
- EXECUTION_BOUNDARY: design phase: read-only on `src/`; probes under {FOLDER};
  the patch docs. After approval: the files the approved design names (expected: RiskManager and Meld), their
  tests, system docs, the release note, the notch and the rebuild.
- DEPENDENCIES: TASK-2026-10-15-trace_meld_contract_scan_gate (findings and probes); melder_0's managed_spell_quantity
  lane (no shared file is edited without a handoff).
- EXIT_GATE: no resolvable=False spell holds the flag; a meld of a spell whose state needs no contract check makes no
  signature scan; contract-bearing spells still validate and revalidate when their state calls for it; the suites
  pass with the GIL off and on; the cost is measured; docs, notch, rebuild; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each design choice; CONFLICT if the state machinery cannot express "contract
  validation needed" without a new state.

## Scope Boundaries
- In scope: RiskManager's spell registration and risk sets; the meld gate and its contract check; the state that
  marks contract validation as needed; Nexus visibility of resolvable=False spells (must not change).
- Out of scope: managed_spell_quantity work; the compiler's own contract scans; MelderOps code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the fix (chat 2026-10-15: "thats an issue we need to address ... lets figure
  this out").

## Steps / Checklist
- [ ] Read whole: RiskManager and its callers; SpellSystemStates' contract flags and contract-dirty marking; Phase 1's
      SpellContract classification and what survives conjure; the meld gate methods; Spell.resolvable.
- [ ] Propose the design to the owner; record his picks.
- [ ] Write the patch docs; get the owner's go.
- [ ] Red tests, the change, green suites (GIL off and on), measurement.
- [ ] Docs, release note, notch, rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- An approved design and patch docs; then the change with tests, docs, notch and rebuild.

## Files / Paths Impacted
- context_compass/{NEW_REL}
- context_compass/{PATCH} (patch docs)
- context_compass/{FOLDER} (probes and runs)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - the probes in {FOLDER} (gate entries, scans and microseconds per meld)
  - the meld, conduit, spellbook and dev-ops suites with the GIL off and on

## Risks / Rollback Notes
- The gate guards correctness: a skipped check must be one the spell's state proves unnecessary, never a guess.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - {FOLDER}
  - {PATCH} (once written)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the patch docs are promoted to documentation)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - which spells the meld state checks count, and which state decides the contract check
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket;
  initial revision {now}; the direction is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Starting point, from the predecessor's Notes: the meld enters `Meld._ensure_lineage_resolvable` only while
    the Book-wide `_spellbook_validation_required` flag is up; RiskManager keeps it up while any spell the root sees
    lacks a `valid` resolution verdict, and counts resolvable=False spells, which never get one. Inside the gate,
    `_check_contracts_and_force_revalidation` scans the signature on every call and, for spells with contracts,
    forces a resolution rerun every time. Measured: about 21 us of a 23 us meld while the flag is pinned, 0.7 us
    when it is down.
  EVIDENCE:
  - {CC}/{DONE_REL}:{notes_range}
  IMPACT: The two rules address the two causes: the flag's membership and the check's trigger.
  NEXT: Read RiskManager's callers and the contract state machinery whole, then propose the design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In progress ({now}). Design phase for the owner's two rules; nothing in `src/` changes before he
approves the design. Next: read the code paths whole, propose the design, record his picks.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
"""


def sync_board(text: str, now: str) -> str:
    """Route the work item to the successor and anchor the closed task."""
    i = text.index("| meld_contract_scan | in_progress |")
    j = text.index("\n", i) + 1
    row = (
        "| meld_contract_scan | in_progress | discovery | claude | melder_1 | none | Read RiskManager's callers and the "
        "contract state machinery whole; propose the design to the owner. | resolvable=False spells never hold the "
        "meld gate open; the contract check runs only when the melded spell's state calls for it. | The owner approves "
        "the design and the fix lands with tests, docs, notch and rebuild, or the owner redirects. | "
        f"{NEW_REL} | {now} | REQUIRED |\n"
    )
    text = text[:i] + row + text[j:]
    old_detail = (
        "- WORK_ITEM: meld_contract_scan\n"
        "  SWITCH_TRIGGER: The answer is delivered and the owner picks a fix or redirects.\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {OLD_REL}\n"
    )
    new_detail = (
        "- WORK_ITEM: meld_contract_scan\n"
        "  SWITCH_TRIGGER: The owner approves the design and the fix lands with tests, docs, notch and rebuild, or the"
        " owner redirects.\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {NEW_REL}\n"
    )
    text = one(text, old_detail, new_detail)
    begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    a0 = text.index(begin) + len(begin)
    a1 = text.index("<!-- END USER-DEFINED: closed_anchors -->")
    rows = [r for r in text[a0:a1].split("\n") if r]
    assert len(rows) == 12, len(rows)
    anchor = (
        f"| meld_contract_scan_trace | done | melder_1 | {DONE_REL} | Investigation only: the meld gate's contract scan "
        f"and the flag that admits it traced and measured; successor {NEW_ID}. | {now} |"
    )
    rows = rows[1:] + [anchor]
    return text[:a0] + "\n".join(rows) + "\n" + text[a1:]


def sync_artifacts(text: str, now: str) -> str:
    """Re-point the evidence folder at the successor and record the closed task's cleared row."""
    i = text.index(f"| {OLD_REL} | {FOLDER} |")
    j = text.index("\n", i) + 1
    row = (
        f"| {NEW_REL} | {FOLDER} | investigation_evidence | active | retain_as_reference | Git-history and "
        "ticket-search logs, the gate probes and their runs (the predecessor's trace), and the open and closure "
        f"scripts; the fix lane's probes join them. | {now} | REQUIRED |\n"
    )
    text = text[:i] + row + text[j:]
    marker = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    cleared = (
        f"| {DONE_REL} | {FOLDER} | retain_as_reference | Investigation closed; the folder stays rowed under "
        f"{NEW_ID} as its evidence. | {now} |\n"
    )
    return one(text, marker, marker + cleared)


def note_epic(text: str, now: str, notes_range: str) -> str:
    """Record that the owner's direction supersedes the epic's memo plan."""
    text = one(text, "- Updated: 2026-10-14T00:28:29Z\n", f"- Updated: {now}\n")
    text = one(
        text,
        "- [ ] Milestone 1: Signature-scan memo - lands alone, no behavior change, meld benchmark before/after recorded.\n",
        "- [ ] Milestone 1: Signature-scan memo - superseded 2026-10-15 (the spell's state decides the check instead):\n"
        f"      {NEW_ID}.\n",
    )
    text = one(
        text,
        "- [ ] Story: STORY-TBD-meld_contract_scan_memo - memoize the per-meld SpellContract default scan\n",
        "- [ ] Story: STORY-TBD-meld_contract_scan_memo - superseded 2026-10-15, never drafted; see Milestone 1\n",
    )
    text = one(
        text,
        "- [ ] Task: Complete story STORY-TBD-meld_contract_scan_memo\n",
        "- [ ] Task: Complete story STORY-TBD-meld_contract_scan_memo - superseded 2026-10-15; see Milestone 1\n",
    )
    decision = (
        "- 2026-10-15: the signature-scan memo (Milestone 1, STORY-TBD-meld_contract_scan_memo) is superseded. The owner\n"
        "  wants resolvable=False spells kept out of the meld state checks and the spell's own state deciding when the\n"
        "  SpellContract check runs: \"a spells state should properly manage when this check happens and it shoudl skip\n"
        f"  fast\". {NEW_ID} carries it.\n"
    )
    width(decision)
    text = one(text, "## Decision Log\n", "## Decision Log\n" + decision)
    note = f"""- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The memo plan for the meld's SpellContract scan (Milestone 1, STORY-TBD-meld_contract_scan_memo, never
    drafted) is superseded by the owner's direction of 2026-10-15: resolvable=False spells are excluded from the meld
    state checks, and the spell's own state decides when the contract check runs, instead of caching the scan per
    call target. {NEW_ID} carries it; the
    success metric above (no inspect.signature on a meld of a spell without SpellContract defaults) still applies.
  EVIDENCE:
  - {CC}/{NEW_REL}:1-20
  - {CC}/{DONE_REL}:{notes_range}
  IMPACT: No agent should implement the memo; Milestone 1, its story and its task are marked superseded.
  NEXT: None in this epic for the scan; service methods stay unscheduled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""
    width(note)
    text = one(text, "\n\n## Closure Confirmation\n", "\n\n" + note + "\n## Closure Confirmation\n")
    old_handoff = (
        "which carries the decided plan and the open questions. This epic keeps the per-meld signature-scan memo "
        "(Milestone 1)\nand service methods, both unscheduled, and the history of the pool discussion (Decision Log and "
        "Notes, 2026-10-05 to\n2026-10-13). The kernel-pool elastic retention landed from here (0.2.8234); no other "
        "source changed in this epic.\n"
    )
    new_handoff = (
        "which carries the decided plan and the open questions. This epic keeps service methods, unscheduled, and the\n"
        "history of the pool discussion (Decision Log and Notes, 2026-10-05 to 2026-10-13). The per-meld signature-scan\n"
        "memo (Milestone 1) is superseded by the owner's direction of 2026-10-15, carried by\n"
        f"{NEW_ID} (last Note). The kernel-pool elastic retention\n"
        "landed from here (0.2.8234); no other source changed in this epic.\n"
    )
    width(new_handoff)
    return one(text, old_handoff, new_handoff)


def main() -> None:
    """Compute every edit, then write."""
    now = sys.argv[1]
    old = CC / OLD_REL
    new = CC / NEW_REL
    assert not new.exists() and not (CC / DONE_REL).exists()
    closed = close_old(old.read_text(encoding="utf-8"), now)
    notes_range = f"{line_of(closed, '## Notes')}-{line_of(closed, '## Context / Handoff Summary') - 2}"
    fresh = new_task(now, notes_range)
    width("\n".join(line for line in fresh.splitlines() if not line.startswith("# Task:")))
    board = sync_board((CC / "attention_board.md").read_text(encoding="utf-8"), now)
    arts = sync_artifacts((CC / "artifact_board.md").read_text(encoding="utf-8"), now)
    epic = note_epic((CC / EPIC_REL).read_text(encoding="utf-8"), now, notes_range)
    for path, text in ((old, closed), (new, fresh), (CC / "attention_board.md", board),
                       (CC / "artifact_board.md", arts), (CC / EPIC_REL, epic)):
        path.write_bytes(text.encode("utf-8"))
    print("done", now, "closed-notes", notes_range)


if __name__ == "__main__":
    main()
