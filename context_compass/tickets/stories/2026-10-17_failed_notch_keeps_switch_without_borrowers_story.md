# Story: failed_notch_keeps_switch_without_borrowers - a notch that fails its commit leaves no half-made switch

## Metadata
- Story ID: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T21:32:09Z
- Updated: 2026-10-17T21:41:33Z

## User Narrative
As an agent notching to a version I staged, I want a notch that raises to leave the structure the way the exception
says it is - the lender and every borrower on one version - so that a failed notch never leaves the lender on the
new version and its borrowers on the old one.

## Value / MRP Alignment
Which version an index selects, and that its borrowers follow a notch, are structure (owner rulings: a notch only
moves which version is active; borrowers follow). Today a notch whose commit validation fails raises
SpellbookValidationError after the switch was made and before the borrowers were told: the lender's index selects
the broken version, the borrowers keep the old one, and the lender can meld neither by address nor the old version
by its spell_id until someone notches back. The structure is wrong after an operation that reported failure.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent;
  the holder of conduit.py and spellbook.py (melder_1, until its rule-2 closure) releases them or carries the fix;
  an active board row; patch docs for the notch's commit path (architecture, component and code-description: the
  change is in error and rollback semantics).
- EXECUTION_BOUNDARY: `Conduit.notch_spell` (its commit and its fan-out) and whatever the answer needs around the
  seam - a structural check of the incoming version before `_apply_notch` runs, rollback actions that undo the seam
  when the commit fails, or a fan-out that runs whatever the commit raises; regression tests; the system documents
  (the SpellIndex Mutation Entry sequence, a failure mode) with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking (the seam's own failure, inside the window);
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the frame claim an undo must give back).
- EXIT_GATE: probe N2 ends with the lender and its borrower on one version, as the answer says, and the exception
  saying which; N1 and N3 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with
  both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT while conduit.py or spellbook.py is held, or
  if the seam task lands first with another order of checks.

## Requirements (Functional)
- A notch that raises from its commit leaves the lender and every linked borrower selecting the same version.
- Answer (a): nothing moves - the index still selects the outgoing version, the incoming one stays parked, the frame
  claim and the Nexus record name the outgoing version, the lender melds it by address and by spell_id, and the
  borrowers are untouched; the error says the notch did not happen and names the broken version.
- Answer (b): the switch stands and the borrower fan-out runs before the error propagates, so the borrowers follow
  the lender; the error says the broken version is now active and that a notch back restores the previous one.

## Requirements (Non-Functional)
- No new lock or lock-order edge; the warm meld path untouched. A notch whose commit succeeds pays nothing new
  beyond what the answer needs (under (a), a check that runs only for a version never compiled - the case the
  commit validator already compiles today).

## Scope Boundaries
- In scope: a notch whose transaction commit raises (phases 1-4 of a never-compiled incoming version failing in the
  change-control structural validator).
- Out of scope: a seam that raises inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking);
  melds in flight while a notch fans out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout); a
  bind whose commit fails (the same validator; not probed here).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question
  for the owner.

## Dependencies / Related Work
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog): the same seam; a check moved ahead of the park
  there and a structural check ahead of the switch here would sit side by side.
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the seam's frame-claim step, which an undo reverses.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question.
- [ ] Task: patch docs for the notch's commit path; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active, a borrower index-linked to its index and a staged version whose structure is broken (a
  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the
  borrower select the same version - English under (a), the broken version under (b); under (a) the lender melds
  English by address and by its spell_id.
- A notch to a sound version (N1) and a notch back (N3) behave as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_notch_refused_at_commit_leaves_the_old_version_active` and
  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Not
  run: no fix exists yet.

## UX / API / Data Notes
- Visible today: `notch_spell` raises SpellbookValidationError "Spellbook validation failed. Broken spells: <name>.",
  then the lender's `meld(spellframe=..., binding_name=...)` raises the same error and `meld(spell_id=<old>)` raises
  KeyError "[MELD] No spell found with spell_id: ..." while the borrower holds the old version active. Under (a) the
  exception keeps its meaning and the world keeps working; under (b) the exception reports a notch that happened.

## Risks / Mitigations
- An undo after the seam must reverse every step `_apply_notch` takes (park, promote, index pointer, frame claim,
  lineage registration and verdicts, Nexus record); a check before the seam needs none, but must run phases 1-4 on a
  version that is still parked - UNKNOWN until the patch reads the phase runner for a parked spell.
- The seam journals the promotion and emits the index crystal inside the window; whichever answer is chosen, the
  research journal and the record should end up telling what happened.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- When a notch's commit validation fails, should the notch (a) be refused with nothing moved - the incoming version
  checked before the switch, or the switch undone; the patch picks the mechanism - so the error means it did not
  happen (recommended: the structural validator fails "instead of accepting a broken staged mutation", and
  notch_spell's other refusals change nothing), or (b) stand, with the borrowers moved to the broken version before
  the error propagates?

## Decision Log
- 2026-10-17T21:32:09Z: filed under EPIC-2026-10-17-correctness_defects from sweep A9 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py (cases N1-N3)
  - artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_broken_late_bind.py (cases B2-B3: the bind precedent; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a notch whose transaction commit fails after its seam ran
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:32:09Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:32:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `Conduit.notch_spell` runs the seam inside its transaction
    (`_notch_spell` -> `_apply_notch`: park the outgoing version and clean its creation context, promote the incoming
    one, repoint the index and the frame claim, emit the index crystal, journal the promotion, re-register the lineage
    gated, mark its dependents, publish the incoming version to Nexus, gate its verdicts), then calls
    `end_transaction(success=True)` outside its `try`. The commit runs the change-control commit validator: for a
    notch to a version never compiled, phases 1-4 (`_default_structural_validator`, which fails "instead of accepting
    a broken staged mutation"). When they fail, the orchestrator's abort hook is unset, the session holds no abort
    hook or rollback action (no caller of `register_rollback_action`, `register_abort_hook` or
    `ChangeControlManager.set_abort_hook` exists in src/melder), and the mediator re-raises: every change of the seam
    stays, and `notch_spell` exits before its borrower fan-out (`_deactivate_borrowed_spell`,
    `_activate_borrowed_spell`, `_emit_index_notch`). Probe N2 (English active, an index-linked borrower, SelfMade
    staged with a constructor that takes its own class): `notch_spell` raises SpellbookValidationError "Broken
    spells: SelfMade.", yet the lender's index selects SelfMade, active, with English parked; the borrower holds
    English active and SelfMade parked; the lender's meld by address raises that error and `meld(spell_id=English)`
    KeyError. N3: a notch back to English restores both sides. N1 (a sound version): owner and borrower follow.
    Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5759
  - src/melder/aether/spellbook/spellbook.py:3851-3904
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1091
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:452-530
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:562-586
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:614-641
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:463-526
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py:1-171
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:1-34
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil1.txt:1-34
  IMPACT: After an operation that reported failure the lender selects the new version and its borrowers the old one,
    against "borrowers follow", and the lender cannot meld the index by address until a notch back.
  NEXT: The owner's answer on the open question, then patch docs for the notch's commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:41:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Evidence for the open question (sweep A11, probe B2-B3). A late `bind` whose commit validation fails keeps
    its spell registered and active with every meld refused - documented ("refused at that bind and at its melds",
    0.2.8224) - so option (b) has a precedent in bind. The difference: a failed late bind displaces nothing, while a
    failed notch displaces the working version (probe N2: the lender cannot meld the index by address afterwards),
    which is why (a) stays recommended. Whichever answer lands, `_stage_spell_for_structural_phases`'s docstring
    ("Notch does NOT stage ... runs the structural phases directly via `_run_post_conjure_structural_phases`") is
    stale: the validator runs phases 1-4 for a notch at its commit (its docstring, `_notch_spell`'s comment, probe
    N2), and the fix should correct it.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4937-4958
  - src/melder/aether/spellbook/spellbook.py:3851-3904
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - context_compass/system_docs/src_architecture.md:2490-2502
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil0.txt:9-37
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:10-18
  IMPACT: The owner has both precedents in front of him; the fix lane has one more line to correct.
  NEXT: The owner's answer on the open question.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: a notch whose commit fails leaves the lender and its borrowers on one version (Requirements). Defect proven
  on 0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in conduit.py and spellbook.py, which melder_1 holds.
- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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
