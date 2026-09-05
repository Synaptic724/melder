# Task: Verify the complete ordered-disposal contract

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-end-to-end-validation
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T13:03:07Z

## Objective
Assemble actual evidence that the agreed order survives configuration, binding, compilation,
cleanup, and record/replay, then hand the complete program back for acceptance.

## Ticket Contract
- ENTRY_GATE: All implementation tasks and docs/assets task are verified; board routes here.
- EXECUTION_BOUNDARY: Relevant tests/checks, focused regressions for discovered gaps, and
  ticket/story/epic outcome synchronization. Fixes return to their owning task scope.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md`
- EXIT_GATE: Acceptance criteria have concrete executed evidence or clearly stated platform
  gaps; no unresolved feature regression is presented as complete; owner accepts closure.
- FAILURE_ESCALATION: Route defects to the owning task with a reproduction. Do not skip supported
  platforms or rewrite synchronization to satisfy an unverified test assumption.

## Scope Boundaries
- In scope: feature verification and final review/closure preparation.
- Out of scope: publishing, signing, committing, pushing, unrelated test repairs, coverage guesses.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Runtime, replay, docs, and generated assets are verified; run the current
  CI runtime command locally and reconcile final evidence without publishing.

## Required Reading and Evidence
- All eight preceding task outcomes and their test commands/results.
- `system_docs/tests_architecture.md` and relevant indexed test-component sections.
- Current `.github/workflows/python-publish.yml` for supported interpreter/platform cells.
- `.github/workflows/build-src-assets.yml` and `.github/workflows/build-repo-assets.yml`.
- Current pytest configuration and relevant fixtures before selecting test commands.
- The discovery Validation section explicitly distinguishes the old generic hash probe
  from the failed Melder import under Python 3.13. It is not runtime proof.

## Steps / Checklist
- [ ] Resolve the available 3.14 interpreter and record version/free-threading mode.
- [ ] Collect prior focused evidence; rerun only where new changes or cross-boundary gaps justify it.
- [ ] Exercise real book defaults plus per-spell names, both priority modes, duplicate and missing names.
- [ ] Verify two separately created Spells never inherit each other's explicit list.
- [ ] Exercise actual cleanup through relevant lifetimes and compiler/override/cache families.
- [ ] Verify hash-seed stability using real supported binding and a stable source-defined target.
- [ ] Verify configuration, active/staged replay, and applicable graft outcomes under the recorded policy.
- [ ] Confirm source/repository asset checks and documentation examples remain current.
- [ ] Report supported matrix cells actually run and those unavailable locally; use real CI output
      when available rather than claiming Linux validation from a Windows run.
- [ ] Synchronize story/epic outcomes and patch disposition for explicit owner acceptance.

## Deliverables
One concise evidence-backed acceptance report with exact remaining gaps, if any.

## Files / Paths Impacted
- Existing focused feature tests and an integration regression only if a real gap remains.
- Task/story/epic notes and board state.
- Actual patch artifact disposition after successful validation and owner acceptance.

## Validation
- Not run; ticket only.
- Required outcomes: False/default gives spell-only names then the full book block; True
  gives book block then spell-only names. Book owns overlaps in both modes; matching is setup-time.
- Preserve class-profile matching, creation-time policy, no-disposal behavior, current failure
  handling, and existing scope disposal traversal.
- Existing error/warning output and test totals must be reported accurately; do not imply
  coverage or a platform matrix was measured without actual results.
- Record commands/results in notes and reopen the relevant implementation task on failure.

## Risks / Rollback Notes
Ready tasks are specified work, not completed work. Do not close the epic because the ticket
stack exists or because one focused test ring is green. No remote state changes are authorized.

## Applicable Anti-Patterns
- [ ] No fabricated run/coverage/platform claims or unsupported skips.
- [ ] No closing tasks while acceptance criteria remain unresolved.

## Done Checklist
- [ ] Required behavioral and asset checks documented with actual results.
- [ ] Genuine remaining gaps named with exact next actions.
- [ ] Story/epic state consistent; owner accepts final closure.
- [ ] Artifact dispositions and deterministic board closure sync applied when authorized.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/ordered_disposal_validation_20260905/runtime.xml`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: owner-accepted closure after results are preserved in notes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: contract verification, platform evidence, acceptance
- IF_UNKNOWN: none

## Noting Behavior
Use MEASURE only for checks actually executed; record results before another validation tranche.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Final validation follows all producer, runtime, persistence, and asset work.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:327-339`
  IMPACT: The final report can distinguish proven end-to-end behavior from planning evidence.
  NEXT: Wait for dependency outcomes, then resolve supported interpreter/platform availability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:04:01Z
  TYPE: FACT
  CLAIM: Existing Creations regression tests inject ordered lists directly and assert method
    order, per-object failure behavior, reversed object/bucket order, and reusable clearing.
    They cannot detect producer order loss. The existing book/conjure test compares frozenset
    membership only. Configuration tests pin ordered first-set names, partial key iteration,
    explicit-value preservation, and missing-record backfill reporting.
  EVIDENCE:
  - `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:104-211`
  - `tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py:103-186`
  - `tests/component/melder/spellbook/test_spellbook_component_spellbook.py:548-637`
  - `tests/unit/melder/spellbook/configuration/test_configuration.py:408-457`
  - `tests/unit/melder/spellbook/configuration/test_configuration.py:510-514`
  - `tests/unit/melder/aether/test_configuration_reload_lanes.py:32-89`
  IMPACT: Preserve these existing contract checks and add upstream-to-call-order cases.
    The new eager default intentionally changes partial configuration key iteration; update
    that exact expectation, not the entire test contract. Source inspection is not test
    execution: no new feature tests or platform checks ran in this holistic-reading pass.
  NEXT: After implementation, connect the two priority modes to actual bind/meld/cleanup,
    then verify cache and replay paths without weakening existing lifecycle tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:03:07Z
  TYPE: PLAN
  CLAIM: Final gate uses the current .github/scripts/run_runtime_tests.py, which checks the
    same process's free-threaded state before and after pytest over unit/component/integration.
    Available interpreter is Windows 3.14.0 free-threaded, GIL disabled. Current CI also targets
    Ubuntu 3.14t, which this local run cannot qualify. Prior evidence: runtime 2,807, replay
    864 passed/3 pre-existing xfails, three examples, and both exact asset checks.
  EVIDENCE:
  - `.github/scripts/run_runtime_tests.py:1-46`
  - `.github/workflows/test-runtime.yml:1-44`
  - `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`
  - `tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md`
  IMPACT: Use PYTHON_GIL=0 and a fresh task-local pytest temp directory outside the sandbox
    due its demonstrated Windows ACL failure. Report JUnit evidence, not coverage guesses.
  NEXT: Run the exact CI runtime command, then final asset/diff checks and owner handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
No tests executed for this new feature yet. This is the last task, not a route to jump ahead
of implementation. Use the child tasks' recorded outcomes and report all material gaps honestly.
Final closure is a user decision; no commits, pushes, releases, or unrelated cleanup.
