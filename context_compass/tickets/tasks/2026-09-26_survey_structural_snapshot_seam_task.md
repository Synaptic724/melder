# Task: Survey the structural-snapshot seam: cache mechanics, key, invalidation, summary

## Metadata
- Task ID: TASK-2026-09-26-survey-structural-snapshot-seam
- Story: STORY-2026-08-03-phase-pipeline-survey
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T00:53:12Z
- Updated: 2026-09-26T07:34:07Z

## Objective
Close discovery done criteria D3 (key composition), D4 (cache mechanics) and D5 (invalidation
surface) from source, then consolidate D1-D6 into `summary.md` so the structural snapshot can be
designed and implemented without re-reading the compiler (discovery steps S9-S11 in the epic).

## Ticket Contract
- ENTRY_GATE: task 2 in review (S6-S8 done) and the active board row routed here.
- EXECUTION_BOUNDARY: Read-only over `src/melder/utilities/caching_system/caching_system.py`, the
  capture and hash functions in `phases/shared_compiler_executions.py`,
  `spellbook_creation_system.py` `_build_conjure_cache_state`, the change-control transaction
  families and the `spell_system_states.py` gated/dirty transition methods, and the crystallizer
  restore path only as far as it calls conjure. Writes limited to this ticket, the story, the epic's
  strategy table and Milestone 1, and `artifacts/ir_phase_survey_20260925/`.
- DEPENDENCIES: tasks 1 and 2 records; the epic's DISCOVERY STRATEGY AND RECOVERY section.
- EXIT_GATE: `cache_seam.md`, `invalidation.md` and `summary.md` exist; summary.md carries D1-D6 with
  `path:start-end`; story exit gate satisfied; status review; owner acceptance requested.
- FAILURE_ESCALATION: BLOCKER if behavior cannot be established from source; DECISION_REQUEST when
  the key or invalidation set needs an owner ruling; CONFLICT when source contradicts the maps.

## Scope Boundaries
- In scope: `caching_system.py` (618, two chunks); `capture_phase2_5_codegen_ir`,
  `hash_codegen_signature` and the executor-signature inputs (re-verify ranges);
  `_build_conjure_cache_state`; the transaction-strategy family listing and the transaction type
  vocabulary; the `SpellSystemStates` methods that mark lineage gated, dirty, disabled or valid
  (whole methods); `RestoreEngine` only where it conjures.
- Out of scope: the meld runtime, Creations, phases 8-11 internals, any edit under `src/` or
  `tests/`, any snapshot code.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created by fable_0 under the owner's 2026-09-26 discovery strategy; opens when
  task 2 reaches review.
- from_state: ready
- to_state: in_progress
- transition_reason: Task 2 reached review at 2026-09-26T07:23:03Z; owner's standing direction to continue discovery
  ("go ahead and research some more"); S9 begins.
- from_state: in_progress
- to_state: review
- transition_reason: S9-S11 complete with cache_seam.md, invalidation.md and summary.md (2026-09-26);
  exit gate met; awaiting owner acceptance.

## Steps / Checklist
- [x] S9: read `caching_system.py` whole (1-500, 501-618) and re-verify the capture and hash inputs;
      write `cache_seam.md` (D3 key composition with evidence; D4 envelope write, admission,
      rejection, generation; shared envelope vs sidecar). (2026-09-26, COMPLETE)
- [x] S10: enumerate the transaction families and the gated/dirty transition methods; write
      `invalidation.md` (D5: event -> code that marks validity -> what a snapshot must do). (2026-09-26, COMPLETE)
- [x] S11: write `summary.md` (D1 object-bound points 1-7 with verdicts; D2 hydrate obligations table;
      D3-D6 sections); mark Milestone 1; move the story to review; request owner acceptance.
      (2026-09-26, COMPLETE; Milestone 1 awaits owner acceptance)
- [x] Update the epic's strategy table status for S9, S10, S11 as each closes. (2026-09-26)
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/ir_phase_survey_20260925/cache_seam.md, invalidation.md, summary.md
- Story exit and epic Milestone 1 evidence.

## Files / Paths Impacted
- None under `src/` or `tests/`. This ticket, the story, the epic, and the artifact directory only.

## Validation
- Not run.
- Recommended commands:
  - none for this read-only task.

## Risks / Rollback Notes
- `spell_system_states.py` (1514) and `change_control_manager.py` (1679) are read by method, never
  whole; the crystallizer is read only at the conjure call.
- The cache format moved to generation 10 on 2026-09-25 (per-slot build guards); cite the current
  source, not earlier notes that say generation 9.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No design decision recorded as FACT; candidates for the key and the invalidation set are
      listed with evidence and decided by the owner.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/ir_phase_survey_20260925/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure; summary.md promotes into the snapshot patch docs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: snapshot key; .melc envelope; invalidation events; hydrate obligations.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:53:12Z
  TYPE: PLAN
  CLAIM: Steps S9-S11 of the epic's discovery strategy: cache mechanics and key composition first,
    invalidation surface second, consolidation last. summary.md is the hand-off into implementation
    (patch docs for the snapshot draw from it).
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
  - src/melder/utilities/caching_system/caching_system.py:1-618
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-376
  IMPACT: Without D3-D5 the snapshot would be designed on the cache classification alone, which keys
    on spell-id sets and says nothing about posture, flags or index mutations.
  NEXT: Wait for task 2 review; then S9 chunk 1 of caching_system.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T07:27:50Z
  TYPE: DECISION
  CLAIM: Expansion recorded before the read: one file outside `spell_compiler/**`, `bind/bind.py`
    (`sha256_profile`, the spell id), because D3 cannot state what invalidates a per-spell row without
    the id's composition. No other subsystem is entered; the meld door stays closed. Also recorded: the
    working tree under `spell_compiler/**` is being edited by melder_0 (missing_dependency_sockets); a
    `git diff -w` check shows `shared_compiler_executions.py` content hunks only at :875-1263 and
    line-ending-only changes elsewhere, so the ranges this survey cites are unaffected today.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:890-994
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-377
  IMPACT: Keeps the expansion gate honest and dates the citation validity against a moving lane.
  NEXT: Write cache_seam.md from the caching system, the classification and the id composition.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T07:27:50Z
  TYPE: FACT
  CLAIM: cache_seam.md COMPLETE (D3, D4). D4: one `.melc` per (frame, conduit name), a marshal envelope
    of version 10, Melder release, Python cache tag, frame and conduit names, and per-spell nested-marshal
    bytes; admission at construction is exact-match on all four stamps plus bytes-typed payloads, else a
    logged cold reset; emit is temp-file plus atomic replace preserving the accepted release; adding a
    snapshot section is a generation bump that cold-resets every bundle once. Classification keys on the
    live resolvable non-existing id set only; posture is echoed, not used. D3: the spell id hashes the
    constructor signature text, annotation names, MRO, method names, frame string, names, existence,
    disposal order and resolvable, so the sorted visible id set determines phase 3's pool projection
    except object identity; per-conduit rows add the owned set, posture, contracted spells, `_is_broken`
    and the runtime conduit/frame ids. The dormant phase 2-5 signature is a per-spell content digest of
    outputs (and reads artifacts the reset nulls), so it is a verification stamp, not a lookup key; its
    parts are tuples of primitives, so driver.md's hash hazards do not reach it.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:159-218
  - src/melder/utilities/caching_system/caching_system.py:470-489
  - src/melder/utilities/caching_system/caching_system.py:491-585
  - src/melder/utilities/caching_system/caching_system.py:587-618
  - src/melder/aether/spellbook/spellbook_creation_system.py:449-487
  - src/melder/aether/spellbook/bind/bind.py:890-994
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-376
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:60-137
  - artifacts/ir_phase_survey_20260925/cache_seam.md:1-127
  IMPACT: The snapshot key has a source-backed composition per tier and a placement decision for the
    owner (envelope section with a generation bump vs sidecar with its own stamps). One new RISK for
    the design story: a type moving module while keeping its rendered name keeps the spell id.
  NEXT: S10: enumerate the transaction families (transaction_type.py, strategy_builder.py) and read the
    `SpellSystemStates` gated/dirty/disabled/valid transition methods whole; write invalidation.md (D5).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:31:49Z
  TYPE: FACT
  CLAIM: invalidation.md COMPLETE (D5). Every writer of structural validity goes through
    `SpellSystemState.set_validity` (RiskManager fan-out on change); the gating helpers are called by:
    bind/rebind (`register_index`: gated `register_or_rebind`), post-conjure bind and the commit-side
    `_default_dirty_marker` (collection dependents `dependencies_changed`; contract dependents
    `contract_unvalidated`), notch (`register_index` + `Spell.invalidate_spell`), index destroy and
    spell cleanup (`unregister_index` -> impact closure, transitively gated), link/unlink and contract
    add/remove via `ConduitWard._invalidate_contract_consumers`, and transfer (`disabled` +
    `transfer_in_progress`, structural change, impact closure, and the ONLY production
    `mark_conduit_dirty`). Cluster and leader transactions write nothing into the registry (grep).
    Posture is a key input, not an event (frozen). Restore re-mints index ULIDs, so rows must not
    carry raw index ids (phase-5 nodes do). Rule for the snapshot: capture only from a pass that
    ended valid and clean, hydrate by replaying the registry writes, key tier 2 on (visible ids,
    owned ids, posture, contracted keys); the existing events then invalidate correctly unchanged.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-417
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:517-666
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:299-352
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:573-651
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:743-800
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1108-1260
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:837-873
  - src/melder/aether/spellbook/spell.py:1324-1390
  - src/melder/aether/spellbook/spellbook.py:3785-3810
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2531-2585
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:687-750
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:846-882
  - artifacts/ir_phase_survey_20260925/invalidation.md:1-87
  IMPACT: D5 closed with a per-event table; the snapshot needs no new invalidation hooks, only correct
    keys and registry-replay hydration. New design constraint: no raw index ULIDs in rows.
  NEXT: S11: write summary.md (D1 object-bound points 1-7 with verdicts; D2 hydrate-obligation table;
    D3-D6 sections; CONFLICT list; UNKNOWN list; implementation entry); mark Milestone 1; story ->
    review; request owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:34:07Z
  TYPE: FACT
  CLAIM: summary.md COMPLETE: D1 object-bound table for phases 1-7 with verdicts (two identity-bearing
    items: custom-`__eq__` frames; index ULIDs inside phase-5 rows), D2 hydrate-obligation table (every
    runtime write of 1-7 with value shape, ordering and replayability), D3-D6 sections citing the
    records, a four-item CONFLICT list, the remaining UNKNOWNs with file:symbol, and the I-0/I-1
    hand-over with the owner decisions I-1 needs (custom-`__eq__` frames, envelope vs sidecar, module
    fingerprint in the per-spell key, whether the CCM dirty-root loop is public API). Task 3 exit gate
    met; story exit gate met pending owner acceptance and Milestone 1.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  - artifacts/ir_phase_survey_20260925/cache_seam.md:1-127
  - artifacts/ir_phase_survey_20260925/invalidation.md:1-87
  - artifacts/ir_phase_survey_20260925/resolution_driver.md:1-131
  IMPACT: Discovery has its implementation-ready basis; the survey can be accepted or redirected on one
    file. Validation: Not run (read-only story).
  NEXT: Owner reviews summary.md (and the records it cites), answers the four decisions, and accepts or
    redirects; on acceptance fable_0 checks Milestone 1, closes the three tasks and the story per the
    closure sync, and opens I-0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T00:53:12Z: not started. Opens when task 2 (S6-S8) reaches review. Resume at S9:
`caching_system.py` 1-500.
STATE 2026-09-26T07:23:03Z: in progress. Resume at S9: `caching_system.py` 1-500, then 501-618; then re-verify
`capture_phase2_5_codegen_ir` and `hash_codegen_signature` inputs in shared_compiler_executions.py; write
cache_seam.md.
STATE 2026-09-26T07:27:50Z: S9 done (cache_seam.md). Resume at S10: grep the transaction families
(`aetheric_mediator/transaction_type.py`, `change_control_manager/transaction_manager/strategies/`) and the
`spell_system_states.py` / `spell_system_state.py` methods that set validity gated, dirty, disabled or valid;
read each method whole; write invalidation.md (D5).
STATE 2026-09-26T07:31:49Z: S10 done (invalidation.md). Resume at S11: write summary.md from the nine records
(driver, phase_01-07, structural_driver, resolution_driver, cache_seam, invalidation); then Milestone 1 on the
epic, story -> review, owner acceptance request.
STATE 2026-09-26T07:34:07Z: S11 done (summary.md). Task 3 in REVIEW; story in REVIEW. Nothing further to read;
the survey waits on owner acceptance of summary.md and the four decisions listed in its last section.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
