# Story: notch_back_keeps_outgoing_dependencies - a notch back leaves the old version's dependencies on the lineage

## Metadata
- Story ID: STORY-2026-10-19-notch_back_keeps_outgoing_dependencies
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-19T12:13:16Z
- Updated: 2026-10-19T12:37:39Z

## User Narrative
As an agent notching an index back to a version I used before, I want the lineage to describe the version that is
active again - its own dependencies, not those of the version I notched away from - so that a borrower's consumer of
the index builds the restored version instead of being refused for a provider that version does not need.

## Value / MRP Alignment
Which dependencies a lineage has is structure, and borrowers follow a notch (owner rulings: structure is the
contract; a notch only moves which version is active). Today a notch to a version that was compiled before runs no
Phase 3, so the lineage keeps the dependencies the outgoing version registered. A borrower that cannot see one of
them has its consumer refused with an error that blames the active version for a dependency it does not have, and
the refusal stays after the lender's own meld has put the lineage right: structure that is wrong, then stuck.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; an active board row; patch docs for the notch's
  lineage registration (architecture and component; code-description if the fix changes the meld gate or the
  verdict handling).
- EXECUTION_BOUNDARY: `Spellbook._apply_notch` (re-register the lineage's dependencies for a version no Phase 3 will
  run for at the notch), or the meld gate's catch-up and the borrower's verdict handling - the patch picks;
  symptom-named regression tests; the system documents with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (S8: its reversal restores the lineage's dependencies
  for a refused notch only - the same registration on one path).
- EXIT_GATE: probe H3 and H4 end with the borrower's Speaker melding "hello" after the notch back, before and after
  the lender's meld; H1 and H2 unchanged; right after the notch back the lineage reads the restored version's
  dependencies; regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT while spellbook.py or meld.py is held by another lane; DECISION_REQUEST if the fix
  needs a choice between registering at the notch and refreshing at the meld that the patch cannot settle.

## Requirements (Functional)
- After a notch to a version that runs no Phase 3 at its commit, the lineage's direct dependencies (and the reverse
  edges `update_dependencies` keeps) are those of the version now active, before any meld runs.
- A borrower's consumer of the index that melds first after such a notch builds the active version, with no
  visibility error for a dependency that version does not have.
- A consumer refused only because the lineage named such a dependency is not left refused once the lineage is right.

## Requirements (Non-Functional)
- No new lock or lock-order edge; the warm meld path untouched; a notch pays at most one registry write more.

## Scope Boundaries
- In scope: a notch, away or back, to a version that runs no Phase 3 at its commit (one with a Phase-5 root
  blueprint), and what a borrower's consumer meets afterwards.
- Out of scope: a notch whose incoming version fails its check (S8); melds in flight during a notch's fan-out
  (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout); a lent consumer's Book-local provider loss
  (TASK-2026-10-16-investigate_lent_consumer_provider_loss).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8260 by a probe with the GIL off and on and its code path read
  whole (FACT note); filed by melder_1 from S8's HYPOTHESIS note; no open question.

## Dependencies / Related Work
- STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers: its reversal restores the dependencies and topology a
  refused version's check registered; this story is the same staleness after a notch that stands.
- TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (completed; rule 2, D2): the meld's catch-up
  walks the melded spell's recorded topology, which is why a consumer that melded before the notches is not hit.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's scheduling and assignment; patch docs for the notch's lineage registration.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- English (no dependencies) active; French, which needs Accent, staged on its index; Accent bound only in the
  lender's Book; a borrower links, contracts the index and binds Speaker(greeter: Greeter) without melding it. After a
  notch to French and a notch back to English the lineage reads no dependencies, and the borrower's first and later
  melds of Speaker return English's "hello" - whether or not the lender melded French in between (H3, H4).
- A consumer that melded before the notches (H1) and a lender that melds first (H2) behave as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_notch_back_leaves_the_lineage_with_the_restored_dependencies`
  and `test_a_borrowers_consumer_melds_the_restored_version_after_a_notch_back`; GIL off and on; the probe re-run.
  Not run: no fix exists yet.

## UX / API / Data Notes
- Visible today: the borrower's `meld(spell_id=<Speaker>)` raises SpellbookValidationError "Spell 'English' depends
  on spells this Spellbook cannot see (spell id <Accent>). Bind them in this Spellbook, or give this conduit access to
  them. [visibility_gap_dependency_filtered]", and every later meld "Broken spells: Speaker ... No validation error
  was recorded for this spell; its validity is invalid, gated or disabled." - the first blames English for French's
  dependency, the second gives no reason at all.

## Risks / Mitigations
- Registering at the notch needs the restored version's own dependency ids. Its recorded topology
  (`get_local_topology_by_id`) names its socket targets; whether every compiled version keeps it, and what a version
  restored from the structural snapshot keeps, is UNKNOWN until the patch reads those writers.
- Any visibility failure pins a consumer's verdict `invalid` with nothing to re-gate it; the patch says whether the
  fix covers only this cause or the stuck verdict in general.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None on the defect; the mechanism (register at the notch, or refresh at the meld) is the patch's.

## Decision Log
- 2026-10-19T12:13:16Z: filed under EPIC-2026-10-17-correctness_defects from S8's HYPOTHESIS note (FACT note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py (cases H1-H4)
  - artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt
  - artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a notch to a compiled version and the lineage's registered dependencies
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence (the probe and its runs); filed
  2026-10-19T12:13:16Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-19T12:13:16Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8260 (the git index's src). `Spellbook._apply_notch` re-registers
    the lineage (`register_index`: the current spell id, the flags, gated) and never writes its direct dependencies;
    only Phase 3 (`update_dependencies` from `CompilerPhase3`) and the structural snapshot's replay do. A notch to a
    version compiled before runs no Phase 3: the commit's structural validator skips a notched member that carries
    a Phase-5 root blueprint. So the lineage keeps the outgoing version's dependencies until the restored version's
    next structural rerun - its own meld in its lender's Book. A borrower's consumer that melds first compiles
    against the stale lineage: the meld's catch-up (`_refresh_stale_dependencies`) walks only what the consumer's
    recorded topology names, and Speaker's was recorded at its conjure, before the link (greeter an UNRESOLVED_INPUT
    socket), so English is not refreshed; the structural rerun then resolves greeter to English, and the target
    pass's `VisibilityGapStrategy` compares the lineage's dependencies ([Accent]) with what the borrower sees and
    refuses. The failed pass leaves Speaker's verdict `invalid`, `_ensure_resolution_resolvable` raises for an
    invalid verdict without a rerun, and nothing re-gates it when the lender's meld puts the lineage right. Probe,
    GIL off and on: H3 (French melded by the lender) and H4 (only notched to and back) are refused and stay refused
    on every later meld; H1 (Speaker melded before the notches) and H2 (the lender melds first) return "hello".
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4002-4157
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:336-500
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:757-814
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1203-1212
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - src/melder/aether/conduit/meld/meld.py:944-1021
  - src/melder/aether/conduit/meld/meld.py:1290-1351
  - src/melder/aether/conduit/meld/meld.py:1426-1482
  - src/melder/aether/conduit/meld/meld.py:1484-1553
  - src/melder/aether/spellbook/spell_compiler/system/validation/visibility_gap_strategy.py:43-117
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py:1-114
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:1-55
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil1.txt:1-71
  IMPACT: After an ordinary notch back a borrower's consumer can be refused for good, against "borrowers follow";
    the refusal names the wrong spell, then no reason.
  NEXT: The owner's scheduling; then patch docs for the notch's lineage registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:37:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner on this story (chat 2026-10-19), shown the H3 run: "Remember notch is meant to trigger
    revalidation", "Thats the point", "It flags the state and the cascade on next meld and maybe that revaluation
    should be serialized as well by the mediator in the frame", "What you found isn't a bug dependencies of the spell
    should be outdated after your notch", then "S11 not my call does my logic make sense?". melder_1's answer: it
    does - a lineage's dependencies are outdated after a notch, the notch flags it gated, and the next meld
    revalidates. The one gap is what this story records: the borrower's Speaker reads English's outdated list in its
    own check without revalidating English first (the catch-up walks only what Speaker's recorded topology names),
    fails, and is left `invalid`, which refuses every later meld with no re-run, where `gated` would re-check. A
    mediator serializing the cascade orders melds that run at once; H3 runs on one thread, so a fix would
    revalidate a gated dependency before its list is read, or leave the consumer gated. melder_1 had said it would
    withdraw the story as not a bug; it holds the story ready until the owner decides.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:944-1021
  - src/melder/aether/conduit/meld/meld.py:1290-1351
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:29-42
  IMPACT: Whether this is a defect is open with the owner; his serialization idea is recorded for the cascade.
  NEXT: The owner's decision: keep the story ready, or withdraw it as not a defect.
  REREAD: REQUIRED
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
- Scope: a notch to a version compiled before leaves the outgoing version's dependencies on the lineage; a
  borrower's consumer melding first is refused for good (Notes; probe in Artifact Links).
- State: ready, unassigned; filed by melder_1 on 2026-10-19 from S8's HYPOTHESIS note; no fix lane open.
- Next: (1) the owner schedules and assigns it; (2) patch docs for the notch's lineage registration; (3) the fix with
  regression tests, docs, notch and the rebuild.

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
