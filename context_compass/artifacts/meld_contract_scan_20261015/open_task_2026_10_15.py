"""
Open TASK-2026-10-15-trace_meld_contract_scan_gate and route it (melder_1, 2026-10-15).

Usage (from the repository root): python3 <this file> <created_at>
Writes the new task from the task template's shape, adds its attention-board row and detail entry, and adds the
artifact-board row. Refuses to overwrite an existing ticket; every replacement asserts one match; nothing is written
unless all three edits succeed.
"""
import pathlib
import sys

CC = pathlib.Path("context_compass")
REL = "tickets/tasks/2026-10-15_trace_meld_contract_scan_gate_task.md"
TASK = CC / REL
BOARD = CC / "attention_board.md"
ARTS = CC / "artifact_board.md"
FOLDER = "artifacts/meld_contract_scan_20261015/"


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence of old with new, or fail."""
    assert text.count(old) == 1, (text.count(old), old[:80])
    return text.replace(old, new, 1)


def ticket(now: str) -> str:
    """Return the full task text."""
    return f"""# Task: Trace why Meld._ensure_lineage_resolvable scans SpellContract defaults on every gated meld

## Metadata
- Task ID: TASK-2026-10-15-trace_meld_contract_scan_gate
- Story: none - standalone; owner-directed (chat 2026-10-15); the same scan was measured on 2026-10-05 in
  EPIC-2026-10-05-melder_services_and_pools
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {now}
- Updated: {now}

## Objective
A MelderOps agent reported that every meld of its Task runs `inspect.signature` through
`Meld._ensure_lineage_resolvable` -> `_check_contracts_and_force_revalidation` -> `_iter_spell_contract_defaults`.
The owner read the code (chat 2026-10-15): the check is too strict - a spell's state should decide when it runs, it
should skip fast, and it should not do a deep lookup on every meld or for every spell. Trace the method through the
git history and the tickets: when the contract check and its placement arrived, and why. Investigation only: no
`src/` change until the owner picks the fix.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; findings are recorded in Notes before the answer.
- EXECUTION_BOUNDARY: read-only on `src/`, git history (read-only commands with GIT_OPTIONAL_LOCKS=0) and tickets;
  logs under {FOLDER}; this ticket and the boards.
- DEPENDENCIES: EPIC-2026-10-05-melder_services_and_pools (the 2026-10-05 measurement and its memo plan).
- EXIT_GATE: the claim answered point by point from the code; the history of the gate and the contract check traced
  to commits and tickets; the owner picks the fix or redirects.
- FAILURE_ESCALATION: DECISION_REQUEST for the fix approach; BLOCKER if the history cannot be read safely.

## Scope Boundaries
- In scope: `Meld._ensure_lineage_resolvable`, `_check_contracts_and_force_revalidation`,
  `_iter_spell_contract_defaults`, `_force_resolution_revalidation`, the Spellbook validation flag (RiskManager),
  the ConduitMeld and SpellSpaceMeld gate calls, their git history and the related tickets.
- Out of scope: any fix; MelderOps code; melder_0's managed_spell_quantity lane.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the investigation (chat 2026-10-15: "go look this up in dynamic mode", then
  "trace this method ... look up the git history and look up the tickets related to it").

## Steps / Checklist
- [x] Read the gate path in the code (ConduitMeld.meld step 3, Meld._ensure_lineage_resolvable,
      _check_contracts_and_force_revalidation, _iter_spell_contract_defaults, RiskManager's flag).
- [ ] Trace the git history of the method and the contract check.
- [ ] Find the related tickets and what they decided.
- [ ] Answer the owner; record his pick.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- A point-by-point answer with code, commit and ticket evidence.

## Files / Paths Impacted
- context_compass/{REL}
- context_compass/{FOLDER} (git and grep logs)
- context_compass/attention_board.md, context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - GIT_OPTIONAL_LOCKS=0 git log -L (read-only), with .git/index.lock checked before and after

## Risks / Rollback Notes
- Read-only investigation; nothing in `src/` changes.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - when a meld runs the SpellContract scan, and how it came to run unconditionally
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
  CLAIM: The gate path as the code stands. `ConduitMeld.meld` and `SpellSpaceMeld.meld` call
    `_ensure_lineage_resolvable` only while the Spellbook's `_spellbook_validation_required` flag is set, not on
    every meld. That flag is Book-wide: RiskManager sets it whenever any lineage the conduit sees is not `valid`,
    structurally or in that conduit, and clears it only when none is. Inside the method the structural rerun is
    guarded by the spell's own state, but `_check_contracts_and_force_revalidation` runs unconditionally after it,
    and it starts with `_iter_spell_contract_defaults`, which calls `inspect.signature(..., FORWARDREF)` with no
    cache and no state check; a spell without SpellContract defaults gets [] every time. For a spell whose contracts
    resolve, it then gates the spell's resolution validity, so `_ensure_resolution_resolvable` reruns its resolution
    phases. Dynamic spells never mint a fast-door entry (they run `_execute_admitted`), so every dynamic meld
    reaches the flag check. So the scan runs on every meld of every spell in a Book while any one lineage there is
    risky, for spells whose own state is valid. The compiler scans the same defaults at compile time (Phase 8
    analyzer, Phase 9 contract processor).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:576-580
  - src/melder/aether/conduit/meld/conduit_meld.py:589-640
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-526
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:624-655
  - src/melder/aether/conduit/meld/meld.py:933-987
  - src/melder/aether/conduit/meld/meld.py:1311-1380
  - src/melder/aether/conduit/meld/meld.py:1382-1427
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1054-1083
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-300
  IMPACT: The MelderOps claim is right about the scan and its missing cache, but the trigger is the Book-wide flag
    rather than every meld; the cost lands on every spell whenever any spell in the Book is risky. The owner calls
    this too strict: a spell's state should decide when the check runs.
  NEXT: Trace the git history of the method and the contract check, then the related tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
In progress ({now}). Owner-directed investigation of the SpellContract scan in the meld gate: the code
facts are recorded (Notes); the git history and the related tickets are next, then the answer and the owner's
pick of a fix. No `src/` change in this task.

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


def main() -> None:
    """Compute the three edits, then write them."""
    now = sys.argv[1]
    assert not TASK.exists(), "ticket exists"
    text = ticket(now)
    for line in text.splitlines():
        assert len(line) <= 120 or line.startswith("  - src/"), (len(line), line)
    board = BOARD.read_text(encoding="utf-8")
    row = (
        "| meld_contract_scan | in_progress | discovery | claude | melder_1 | none | Trace the git history of "
        "_ensure_lineage_resolvable and its contract check, then the related tickets. | The owner's question answered "
        "from the code, the history and the tickets; the owner picks the fix. | The answer is delivered and the owner "
        f"picks a fix or redirects. | {REL} | {now} | REQUIRED |\n"
    )
    board = one(board, "<!-- END USER-DEFINED: active_items -->", row + "<!-- END USER-DEFINED: active_items -->")
    detail = (
        "- WORK_ITEM: meld_contract_scan\n"
        "  SWITCH_TRIGGER: The answer is delivered and the owner picks a fix or redirects.\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {REL}\n"
    )
    board = one(
        board,
        "<!-- END USER-DEFINED: active_attention_details -->",
        detail + "<!-- END USER-DEFINED: active_attention_details -->",
    )
    arts = ARTS.read_text(encoding="utf-8")
    arow = (
        f"| {REL} | {FOLDER} | investigation_evidence | active | retain_as_reference | Git-history and ticket-search "
        f"logs behind the trace of the meld gate's SpellContract scan, and the open script. | {now} | REQUIRED |\n"
    )
    arts = one(arts, "<!-- END USER-DEFINED: active_artifacts -->", arow + "<!-- END USER-DEFINED: active_artifacts -->")
    TASK.write_text(text, encoding="utf-8")
    BOARD.write_text(board, encoding="utf-8")
    ARTS.write_text(arts, encoding="utf-8")
    print("opened", now)


if __name__ == "__main__":
    main()
