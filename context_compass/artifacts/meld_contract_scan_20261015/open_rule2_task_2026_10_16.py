"""Open TASK-2026-10-16-recheck_contract_consumers_when_provider_changes from the task template (melder_1).

usage (from the repository root): python <this script> <UTC now> [--check]
The successor of TASK-2026-10-15-make_meld_state_checks_follow_spell_state, carrying its rule 2 by the owner's
direction of 2026-10-16. Refuses an existing target; cites the predecessor's Notes by their ranges in the completed
file; lines within 120 characters and ASCII; --check writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TARGET = pathlib.Path("context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
PRED = "context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015/"
PATCH = "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"

pred_lines = pathlib.Path(PRED).read_text(encoding="ascii").split("\n")


def note_range(claim_start):
    """Line range of the predecessor Note whose CLAIM begins with `claim_start`."""
    claim = next(i for i, l in enumerate(pred_lines, 1) if l.startswith("  CLAIM: " + claim_start))
    start = max(i for i, l in enumerate(pred_lines[:claim], 1) if l.startswith("- DATETIME:"))
    end = next(i for i, l in enumerate(pred_lines, 1) if i > claim and l.startswith("  SCORE_0_TO_10:"))
    return f"{PRED}:{start}-{end}"


R_STATE = note_range("The contract state already exists")
R_PROBE = note_range("Design probe (live repo")
R_REQUEST = note_range("Proposed design, for the owner.")
R_DIRECTION = note_range("Owner direction on rule 2")
R_ACCEPT = note_range("Owner acceptance (chat 2026-10-16)")

TEXT = f"""# Task: Recheck SpellContract consumers when their provider changes, instead of on every gated meld

## Metadata
- Task ID: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes
- Story: none - standalone; successor of TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done, rule 1
  landed as 0.2.8247), carrying its rule 2 by the owner's direction of 2026-10-16
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {NOW}
- Updated: {NOW}

## Objective
Rule 2 of the owner's 2026-10-15 direction, settled in principle on 2026-10-16: a spell's own state decides when the
SpellContract check runs. A satisfied contract is not checked again on every meld; a change of the provider a
consumer resolves - a notch above all, because a notched version's `__init__` may differ - marks that consumer for a
recheck, and its next meld re-validates the contract and rebuilds against the version now active, or fails with the
error a first meld would give. Objects already built keep their provider (mark only). Design first: patch docs for
the owner's approval, and no `src/` edit before it.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; the contract check and every path that changes a borrower Book's active
  contracted copy are read whole on today's tree and recorded; the patch docs under
  {PATCH} exist, are linked and are
  approved by the owner before any `src/` edit; melder_0 hands over spellbook.py before it is edited.
- EXECUTION_BOUNDARY: design phase: read-only on `src/`; probes under artifacts/meld_contract_scan_20261015/; the
  patch docs. After approval: the files the approved design names (expected: Meld's gate, the borrower Book's
  contracted-map mutators, the contract marking in SpellSystemStates), their tests, system docs, the release note,
  the notch and the rebuild.
- DEPENDENCIES: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done: its findings, probes and rule 1);
  melder_0's lanes (spellbook.py and transfer_of_ownership.py are its files: no edit without a handoff).
- EXIT_GATE: a meld of a spell whose state needs no contract check makes no signature scan and forces no rebuild; a
  contract consumer follows its lender's notch (notch back, park, reactivate and destroy included) by a recheck at
  its next meld and fails with the first-meld error when the new version cannot be resolved for it; objects already
  built keep their provider; the suites pass with the GIL off and on; the cost is measured; docs, notch, rebuild;
  the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each design choice the owner has not made; CONFLICT if a provider change
  cannot reach its consumers' state without a new state or a hot-path read; BLOCKER while spellbook.py is not handed
  over.

## Scope Boundaries
- In scope: `Meld._ensure_lineage_resolvable` and its contract check; the producers of a contract consumer's `gated`
  + `contract_unvalidated` state; every path that changes a borrower Book's active contracted copy (a lender's notch
  and notch back, parking and reactivating a version-anchored copy, add, remove and destroy).
- Out of scope: rule 1 (done, 0.2.8247); the compiler's own contract scans; dropping stored consumer objects on a
  notch (owner: mark only); managed_spell_quantity work; MelderOps code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner split rule 2 off TASK-2026-10-15-make_meld_state_checks_follow_spell_state and
  directed this successor (chat 2026-10-16: "yees sure thats good" to opening it on the settled story, design docs
  first).

## Steps / Checklist
- [ ] Re-read whole on today's tree: the meld gate's contract check, Phase 4's contract presence check, the contract
      marking (`mark_contract_dependents_dirty`) and its callers, a lender notch's fan-out to borrowers and the
      borrower Book's contracted-map mutators; record what reaches a consumer's state and what does not.
- [ ] Write the patch docs; get the owner's approval; get melder_0's handoff of spellbook.py.
- [ ] Red tests, the change, green suites (GIL off and on), measurement.
- [ ] Docs, release note, notch, rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Approved patch docs; then the change with tests, docs, notch and rebuild.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md
- context_compass/{PATCH} (patch docs)
- context_compass/artifacts/meld_contract_scan_20261015/ (probes and runs, shared with the predecessor)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - artifacts/meld_contract_scan_20261015/probe_design_baseline.py (the borrower contract consumer: gate entries,
    scans and microseconds per meld) and a probe that notches the lender and melds the consumer
  - the meld, conduit, spellbook and dev-ops suites with the GIL off and on

## Risks / Rollback Notes
- Today the per-meld scan hides the missing marking: removed alone, a consumer kept getting the old version after
  its lender notched (measured 2026-10-15). The marking lands with the removal, never after it.
- A consumer plan built for one provider version must not run against another; the recheck is that guard, so every
  path that changes the borrower's active copy must mark.

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
  - artifacts/meld_contract_scan_20261015/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the patch docs, once written, are promoted to documentation)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - which provider changes must mark a SpellContract consumer, and how the meld check reads that state
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket;
  initial revision {NOW}; the direction is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Starting point, as read and measured on 2026-10-15 (the predecessor's Notes; not yet re-read on today's
    tree, so no design claim rests on it yet). Phase 3 records each SpellContract socket per Book (key ->
    consumer lineages); Phase 4 marks a consumer `gated` + `contract_unvalidated` while its provider is missing
    and clears the flag when present; link, grant, uncontract, sever and remove-all gate the key's consumers.
    Phase 9 bakes the provider's spell id into the consumer's plan. A lender's notch, or parking a
    version-anchored copy, ends in the borrower Book's contracted-map mutators, which mark nobody; the meld's
    unconditional scan forces a 5-11 rebuild of every contract consumer on every gated meld and so hides that.
    Measured then: a borrower contract consumer 2663 / 2354 us a meld (GIL off / on), 2.0 / 1.9 us with the scan
    removed, and with the scan removed alone the consumer kept getting version A after its lender notched to B.
  EVIDENCE:
  - {R_STATE}
  - {R_PROBE}
  - {A}runs/probe_design_baseline_gil0.txt:1-21
  IMPACT: The marking is the precondition of the removal; the two land together.
  NEXT: Re-read the gate's contract check and every path that changes a borrower's active contracted copy, whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-16), recorded in the predecessor: a satisfied SpellContract needs no
    per-meld check; a notch "should be rechecked"; mark only ("marking makes sense thats the point we want to make
    sure we can still resolve it because the init might change for a notched spell"). He accepted rule 1 and
    directed this successor, design docs first ("yees sure thats good").
  EVIDENCE:
  - {R_REQUEST}
  - {R_DIRECTION}
  - {R_ACCEPT}
  IMPACT: The story is settled; the patch docs carry its mechanics for his approval, and no `src/` changes before.
  NEXT: The first checklist step: the code reads, recorded as Notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
In progress ({NOW}): design phase; no `src/` change before the owner approves the patch docs.
The story (owner, 2026-10-16): a satisfied SpellContract is not checked on every meld; a change of the provider
a consumer resolves - a lender's notch above all, since a notched version's `__init__` may differ - marks the
key's consumers `gated` + `contract_unvalidated`, so their next meld re-validates the contract and rebuilds
against the version now active, or fails with the first-meld error; objects already built keep their provider.
Starting evidence: the predecessor's Notes and probes (artifacts/meld_contract_scan_20261015/). Holds:
spellbook.py is melder_0's (handoff before the build).
Next: (1) re-read the code paths whole on today's tree and record them; (2) the patch docs under
{PATCH} for the owner's approval;
(3) melder_0's handoff of spellbook.py, then the build.

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

assert not TARGET.exists(), TARGET
too_long = [l for l in TEXT.split("\n") if len(l) > 120]
assert not too_long, too_long
TEXT.encode("ascii")
if not CHECK:
    TARGET.write_bytes(TEXT.encode("ascii"))
print("checked" if CHECK else "written", TARGET, len(TEXT.split("\n")) - 1, "lines")
print(R_STATE, R_PROBE, R_REQUEST, R_DIRECTION, R_ACCEPT, sep="\n")
