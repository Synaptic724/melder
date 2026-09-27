# Task: Invalidation and restore parity of the structural snapshot (D5 events, two processes, crystallizer restore)

## Metadata
- Task ID: TASK-2026-09-26-structural-snapshot-parity
- Story: STORY-2026-09-26-structural-snapshot
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T18:30:06Z
- Updated: 2026-09-26T18:42:06Z

## Objective
Pin that the world after a hydrated conjure behaves like the world after a cold one: the D5 invalidation events a
conjured book can see (bind after conjure, notch, spell removal, contract grant, transfer) leave the same registry
state and meld outcome; rows captured by another process hydrate this one (value-only key and stamp); a
crystallizer restore (fresh index ULIDs, same spell ids and posture) hydrates. Fix what the parity run proves
broken when it is small and source-evidenced; record what is outside the lane.

## Ticket Contract
- ENTRY_GATE: tasks 3-4 done (owner-run suites green, accepted 18:18:08Z); the owner's standing go for the lane;
  the active board row routes here.
- EXECUTION_BOUNDARY: one component test file for the parity contracts plus an importable mock class module
  (`tests/mocks/spellbook/structural_snapshot_classes.py`); a fix in `aetheric_frame.py` only if the restore
  parity run proves the frame drops recorded caching posture (it did: see Notes); patch docs at review. NOT in
  scope: the notch runtime defect found on the way (outside the lane; reported), measurement, promotion.
- DEPENDENCIES: tasks 3-4 (capture + hydrate); the D5 survey table
  (artifacts/ir_phase_survey_20260925/invalidation.md); crystallizer record/restore round trip.
- EXIT_GATE: worktree suites green; edits on the device tree byte-identical; owner-run suites green; task in review.
- FAILURE_ESCALATION: DECISION_REQUEST for any fix outside the lane's files; BLOCKER if a parity case shows a
  hydrated verdict the cold world never reaches (none found).

## Scope Boundaries
- In scope: the parity test file, the mock module, the frame caching-posture copy fix and its unit test.
- Out of scope: the notch defect (dependent melded first time after a provider notch), measurement, promotion.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's standing go after tasks 3-4 closed (2026-09-26T18:30:06Z); the parity
  contracts were proven in the VM worktree before this ticket was written (recorded below), so it opens at the
  device-tree step.
- from_state: in_progress
- to_state: review
- transition_reason: Parity tests, mock module and the frame caching-posture fix landed on the device tree after green
  worktree runs; docs and release note aligned (2026-09-26T18:31:52Z). Owner-run suites (P4) and acceptance remain.
- from_state: review
- to_state: done
- transition_reason: Owner ran the recommended suites and accepted ("running good ... it's faster for sure",
  2026-09-26T18:42:06Z); closure sync run with the promotion task.

## Steps / Checklist
- [x] P1: parity events as tests (bind after conjure, notch, remove, transfer, contract grant) cold vs hydrated;
  two-process contract; crystallizer restore contract. Worktree green.
- [x] P2: restore parity exposed `AethericFrame.bind_frame_configuration` dropping the caching posture; fixed
  with a unit test (worktree green across the aether/crystallizer/spellbook trees).
- [x] P3: apply to the device tree; cmp; notes; patch docs; release note line for the frame fix.
- [x] P4: owner-run suites; "Not run." until then.
- [x] Run Ticket Microcycle during execution:
  - Note before the next tranche; `SCORE_0_TO_10` >= 7; evidence as `path:start-end`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Parity test file (7 contracts), the mock module, the frame fix + unit test, the notch finding for the owner.

## Files / Paths Impacted
- tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py (new, 7 tests)
- tests/mocks/spellbook/structural_snapshot_classes.py (new)
- src/melder/aether/aetheric_frame/aetheric_frame.py (`bind_frame_configuration` copies the caching posture)
- tests/unit/melder/aether/test_aether.py (+1 test)
- release_docs/next_version_release.md (bullet: Restored worlds keep their recorded cache posture)
- system_docs/patches/active/structural_snapshot_2026_09_26/ (parity marked LANDED)

## Validation
- Owner-run suites: green (owner, 2026-09-26T18:42:06Z; the recommended command below, run from .venv_new).
- Worktree (VM, 3.14.7t): aether/crystallizer/conduit trees 6920 passed; spellbook trees 4417 passed;
  crystallizer/mutation/multithreading/live_sim/top-level 842 passed (all after the frame fix).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether tests/unit/melder/spellbook tests/component/melder/spellbook tests/integration/melder/spellbook tests/integration/melder/crystallizer`

## Risks / Rollback Notes
- The frame fix changes what a restored (or re-bound) frame inherits: the recorded caching flag and cache root
  instead of the defaults. That is the recorded truth; a world that never set them is unaffected (defaults
  recorded). Rollback: drop the two `with_` calls and the unit test.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No parity assertion on index ULIDs (dependents are compared by spell id).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
  - artifacts/ir_phase_survey_20260925/invalidation.md
- DISPOSITION: promote_to_documentation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: invalidation parity; two-process key; restore parity; frame caching posture.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T18:30:06Z
  TYPE: FACT
  CLAIM: P1 in the worktree. Parity contracts (one file, 7 tests): for each of bind-after-conjure (a new consumer
    of two pre-existing providers), notch (meld Car, stage EngineAlternative into Engine's index, notch, meld the
    member and Car), remove (Car) and transfer (Radio to a second conduit) the cold world (structural path miss)
    and the hydrated world (full_hit, no structural run) end with the same event outcome and the same registry
    snapshot (dependencies, direct dependencies, dependents by spell id, validity, flags, socket rows); a
    SpellContract consumer without a provider hydrates the recorded gated + contract_unvalidated verdict and the
    later contract grant melds the same objects; a child process (subprocess, same dotted mock module) conjures
    cold and this process classifies full_hit with no structural run and melds; all green. Mock classes live in
    `tests/mocks/spellbook/structural_snapshot_classes.py` so both processes render the same (module, qualname)
    annotation refs.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py:173-343
  - tests/mocks/spellbook/structural_snapshot_classes.py:1-30
  IMPACT: Every registry-writing invalidation event behaves identically after a replay, as the design predicted
    (they write through the registry, not the phases).
  NEXT: restore parity (crystallizer round trip).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:30:06Z
  TYPE: FACT
  CLAIM: Runtime defect found on the way, OUTSIDE this lane (not fixed): after a provider notch (Engine ->
    EngineAlternative via bind_inactive + notch_spell), the FIRST meld of a dependent (Car) fails with
    "generalized manifest references unknown spell_id <old Engine id>" - identical with caching on or off, cold or
    hydrated; when Car was melded once before the notch, the later meld succeeds and returns the old unique Engine
    instance. Reproduced with a 20-line probe (VM home); the parity notch case uses the supported order.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_binding_resolver.py:225-232
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py:173-190
  IMPACT: Not a snapshot parity issue (cold and hydrated agree); reported to the owner for routing (notch lane).
  NEXT: restore parity.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:30:06Z
  TYPE: FACT
  CLAIM: P2. Restore parity first FAILED (restored world classified miss): the recorded frame twin carries
    `system_caching_enabled` and `system_cache_root_path` (describe_posture -> AethericFrameCrystal;
    from_recorded_posture rebuilds them), but `AethericFrame.bind_frame_configuration` copies every posture field
    into the frame-owned object EXCEPT those two, so a restored frame silently conjures against the default cache
    root - the executor tier never hit after a restore either. Fixed by copying the two fields in the same block
    (aetheric_frame.py) with a unit test; the restore contract then hydrates: record -> checkpoint -> flush ->
    fresh boot -> reload -> load_checkpoint conjures the recorded root with path full_hit and no structural run,
    and the restored conduit melds Car. Worktree: unit aether+crystallizer, component aether+utilities,
    integration aether+conduit 6920 passed; spellbook trees 4417 passed; crystallizer/mutation/multithreading/
    live_sim/top-level 842 passed.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:693-707
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1293-1345
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:2025-2033
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py:345-390
  - tests/unit/melder/aether/test_aether.py:931-948
  IMPACT: Restore parity holds; a restored world now keeps its recorded caching posture (behavior change, the
    recorded truth). The fix sits outside the lane's original file list - flagged to the owner with the report.
  NEXT: P3 - device tree, docs, release note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:31:52Z
  TYPE: FACT
  CLAIM: P3 done: the four files are on the device tree byte-identical to the tested worktree (cmp); patch docs
    mark parity LANDED (migration step 4, validation items) with the frame fix noted; release note gains
    "Restored worlds keep their recorded cache posture". Task to review; owner-run suites are the gate.
  EVIDENCE:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:137-140
  - release_docs/next_version_release.md:112-114
  IMPACT: The lane's remaining items are measurement (owner-run) and promotion into the canonical maps.
  NEXT: owner report (notch defect routed; frame fix flagged as outside the original file list).
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T18:30:06Z: IN_PROGRESS. P1-P2 proven in the worktree; P3 (device tree, docs) next; owner-run suites
after.
STATE 2026-09-26T18:31:52Z: REVIEW. P1-P3 done; owner-run suites pending; the notch defect is reported for routing; the
frame fix is flagged to the owner. Successors: measurement (owner-run) and promotion.
STATE 2026-09-26T18:42:06Z: DONE. Owner-run suites green and accepted (frame fix kept); moved to completed/. Lane
successors: the promotion task closes in the same pass; measurement stays owner-run.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
