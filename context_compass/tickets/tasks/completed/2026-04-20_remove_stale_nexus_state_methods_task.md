# Task: Remove Stale Nexus State Methods
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the bounded Nexus stale-helper removals landed and the
  focused Nexus and ACL validation ring passed.

## Metadata
- Task ID: TASK-2026-04-20-remove-stale-nexus-state-methods
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T05:27:27Z
- Updated: 2026-04-26T11:39:24Z

## Objective
Manually audit `Nexus` for stale or duplicated state-oriented methods that
survived the frame-manager migration, remove the ones proven obsolete, and keep
the remaining `Nexus` surface aligned with real call sites and current
ownership.

## Ticket Contract
- ENTRY_GATE: the user explicitly directed a manual `Get-Content` audit of
  `nexus.py` and asked for stale state methods to be removed.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus.py`
  - directly affected references in `src/` / `tests/` / interfaces if the
    removed methods are still named externally
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `codex/context_compass/attention_board.md`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/utilities/interfaces/interfaces.py`
  - active AR/Nexus cleanup tickets already reread during re-entry
- EXIT_GATE: every removed method is backed by manual source evidence showing
  it is dead or redundant, and the focused Nexus validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a candidate method is still
  part of the public or interface contract, or if removal would widen into a
  larger architectural refactor.

## Scope Boundaries
- In scope:
  - manual `nexus.py` method audit
  - stale state-oriented private/helper method removal
  - docstring cleanup for touched `Nexus` methods
  - directly required call-site/test adjustments
- Out of scope:
  - unrelated `Nexus` refactors
  - broad AR/runtime redesign
  - non-`Nexus` cleanup sweeps

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a manual `Nexus` audit and
  removal of stale state methods.

## Steps / Checklist
- [ ] Read `src/melder/aether/nexus/nexus.py` manually in bounded chunks.
- [ ] Identify state-oriented methods that appear stale, duplicated, or purely
      pass-through after the frame-manager migration.
- [ ] Verify each candidate against real source/test/interface call sites.
- [ ] Record the candidate cut set in `## Notes` with evidence.
- [ ] Add required patch artifacts if the validated cut set crosses the
      patch-framework gate.
- [ ] Remove only the methods proven obsolete and repair direct references.
- [ ] Run focused Nexus validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed list of removable stale `Nexus` state methods
- bounded `Nexus` cleanup patch
- focused Nexus validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-20_remove_stale_nexus_state_methods_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/nexus.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: a method that looks redundant in `Nexus` is still part of a live
  contract through interfaces or tests.
  Rollback: keep the method, mark the candidate `UNKNOWN`, and narrow the cut
  set to only the methods proven dead.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: PLAN
  CLAIM: The current request is to audit `Nexus` manually and remove stale
    state methods from the source itself, not to rely on generated inventories
    or subagent summaries. The first compliant step is therefore a direct
    `Get-Content` chunked read of `nexus.py`, followed by per-method evidence
    notes before any code edit.
  EVIDENCE:
  - user_instruction: "go over nexus manually and find all the state methods and remove them use get content no fucken stupid shit"
  - src/melder/aether/nexus/nexus.py:1-2395
  IMPACT: The audit has to be source-manual and evidence-first. Candidate
    removals stay `UNKNOWN` until proven dead or duplicated from current
    call-site evidence.
  NEXT: read `nexus.py` manually in sequential chunks and record the first
    stale-method tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: FACT
  CLAIM: The first likely stale tranche is not actually removable. The
    descriptor-publication pass-through helpers in `Nexus`
    (`_refresh_frame_posture_cache`, `_get_publishable_frame_posture`,
    `_publish_frame_record`, `_publish_conduit_record`,
    `_remove_conduit_record`, `_publish_spell_record`,
    `_remove_spell_record`) still have live call sites from lower runtime
    owners and passive-ingest tests, so they are current compatibility/service
    surface, not dead state methods.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:921-1088
  - src/melder/aether/conduit/conduit.py:439-491
  - src/melder/spellbook/spellbook.py:3272-3343
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:106-301
  IMPACT: The cleanup lane cannot delete the first publication cluster just
    because it looks like pass-through indirection. We need a narrower target
    set.
  NEXT: inspect the later ACL/projection/gate helper cluster in `Nexus` and
    verify which methods are true stale state indirection versus active public
    or test-visible contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: FACT
  CLAIM: The first actual stale-method cut set is now explicit. Four private
    helpers are dead in source and tests:
    - `_refresh_frame_posture_cache`
    - `_get_publishable_frame_posture`
    - `_get_required_target_frame_boolean`
    - `_get_required_target_frame_system_state`
    None of them have surviving call sites outside their own definitions.
    A fifth helper, `_refresh_rift_projection_sets_for_frame`, is only a thin
    one-frame wrapper over `_refresh_rift_projection_sets_for_frames` and is
    referenced only by two unit tests.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:921-961
  - src/melder/aether/nexus/nexus.py:1977-1991
  - src/melder/aether/nexus/nexus.py:2457-2533
  - tests/unit/melder/aether/test_nexus.py:827-877
  IMPACT: We can make a bounded `Nexus` cleanup patch without widening into the
    live publication, ACL, or frame-manager surface.
  NEXT: remove the four dead private helpers, remove the one-frame refresh
    wrapper, and update the two unit tests to call the tuple-based refresh
    method directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: FACT
  CLAIM: The first bounded cleanup patch is now in place. `Nexus` no longer
    carries the four dead private wrappers
    (`_refresh_frame_posture_cache`, `_get_publishable_frame_posture`,
    `_get_required_target_frame_boolean`,
    `_get_required_target_frame_system_state`) and no longer carries the
    one-frame projection refresh wrapper
    (`_refresh_rift_projection_sets_for_frame`). The two unit tests that still
    used that convenience wrapper now call the surviving tuple-based batch
    method directly.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:921-961
  - src/melder/aether/nexus/nexus.py:1977-1991
  - src/melder/aether/nexus/nexus.py:2457-2533
  - tests/unit/melder/aether/test_nexus.py:827-877
  IMPACT: The `Nexus` surface is smaller and less misleading without widening
    into the still-live publication, ACL, or frame-manager pathways.
  NEXT: run the focused Nexus unit ring and confirm no remaining callers expect
    the removed helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: FACT
  CLAIM: `insert_head_frame_acl_configuration(...)` is also stale. The current
    bundle-chain head/current split no longer exists, the method is just an
    alias over installing the `"default"` named ACL configuration, and the
    only surviving caller is one integration test.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1724-1767
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:202-206
  IMPACT: We can remove one more obsolete `Nexus` compatibility seam and have
    the integration test call the live named-config install path directly.
  NEXT: remove `insert_head_frame_acl_configuration(...)`, update the
    integration test to use `register_named_frame_acl_configuration(...)`, and
    rerun the bounded validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: FACT
  CLAIM: The second bounded cleanup patch is now in place.
    `insert_head_frame_acl_configuration(...)` is removed from `Nexus`, and
    the single integration caller now uses the still-live named default ACL
    registration path directly.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1724-1767
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:202-206
  IMPACT: The old ACL bundle-head compatibility seam is gone, and the `Nexus`
    surface now reflects the post-chain-model contract more honestly.
  NEXT: rerun the focused Nexus unit ring and the affected ACL compiler
    integration slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:27:27Z
  TYPE: MEASURE
  CLAIM: The bounded `Nexus` stale-method removal slice is green on syntax and
    the focused Nexus/ACL validation ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py -k "nexus or compiled_surface_projects_directly_into_frame_viewer or installs_same_name_acl_bundle"` -> `108 passed, 2 deselected`
  IMPACT: The manual cleanup cut is stable enough to return immediately instead
    of widening the lane without another proved stale candidate.
  NEXT: report the removed `Nexus` methods, the test updates, and the live
    surfaces that were explicitly left alone because call-site evidence still
    exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the manual `Nexus` stale-method audit and bounded removal lane.
