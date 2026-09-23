# Task: Capture graduation Book ownership failures with red component regressions

## Metadata
- Completed: 2026-09-22T14:41:23Z
- Summary: Graduation source, hook isolation and shared-frame behavior qualified and turned in; packaging held separately.
- Task ID: TASK-2026-09-22-add-graduation-ownership-red-regressions
- Epic: EPIC-2026-09-22-graduated-conduit-spellbook-ownership-and-configuration
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T10:28:54Z
- Updated: 2026-09-22T14:41:23Z

## Objective and Contract
Add real failing tests for independent graduated bindings, bind hooks and cleanup, across local
and frame-shared configuration. Create the related epic; do not repair runtime code.
- ENTRY_GATE: Owner explicitly requests red regressions; current source trace is available.
- EXECUTION_BOUNDARY: One new component test module, epic/task/boards and run evidence only.
- DEPENDENCIES: Existing Bind hook feature and current dynamic graduation implementation.
- EXIT_GATE: Tests collect and fail on the intended ownership symptoms; test-only mistakes corrected;
  failure evidence retained and epic ready for discussion.
- FAILURE_ESCALATION: Record blocked setup or behavior ambiguity without modifying runtime.

## Scope
- In: Book ownership, post-upgrade registration and Meld/Space lookup, Bind isolation, both teardown
  orders, local/shared configuration setup and parent survival.
- Out: Runtime repair, build assets, optional-argument implementation, unchosen inherited-visibility
  semantics, blanket xfail/skip, broad hook-standardization work.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner requested turn-in after additional regression tests, which now pass.

## Work
- [x] Read suite entrypoints and configuration setup helpers.
- [x] Add component regressions with safe fixture cleanup and both configuration modes.
- [x] Run the selection; prove failures are actual ownership defects.
- [x] Record exact outcomes and leave runtime repair held for discussion.

## Files / Paths Impacted
- tests/component/melder/aether/conduit/test_conduit_graduation_ownership_regression.py
- tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
- This task, attention_board.md, artifact_board.md and task-owned run evidence.

## Validation
Current follow-up: all 32 cases pass after the authorized implementation in
tickets/tasks/completed/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md.
Evidence: artifacts/graduation_configuration_20260922/qualification_final.xml.
The following results preserve the original red-test delivery baseline.

32 regression cases fail at desired-behavior assertions; 3 existing controls pass in the combined run.
Zero setup/teardown errors, skips or final-run warnings. Executed with uv offline/no-sync, .venv_new
and Python -X gil=0. New-file Ruff passes. All 592 runtime Python sources retain their original hashes;
no runtime Python files were added. Plain failing tests are the requested output; no xfail or skip.

## Risks / Mitigations
- Current child cleanup can destroy the parent Book: fixtures must tolerate idempotent teardown
  without suppressing test-body failures or masking expected assertions.
- Do not encode removal of inherited spell visibility as a requirement; only new ownership is settled.
- Shared rich configuration does not imply shared Bind callback storage.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/graduation_ownership_regressions_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-22T10:28:54Z
  TYPE: PLAN
  CLAIM: Add desired-behavior tests for Book/binding/hook/cleanup isolation in both rich-config
    ownership modes. Keep optional upgrade configuration in the epic until its API semantics are
    agreed; do not make an unchosen keyword the cause of every red regression.
  EVIDENCE:
  - Owner's current instruction.
  - src/melder/aether/conduit/conduit.py:1961-2140
  - src/melder/aether/spellbook/spellbook.py:6387-6423
  - tests/component/melder/spellbook/test_bind_lifecycle_hooks.py:520-544
  IMPACT: This is the active test-only lane. No source repair or asset generation is authorized.
  NEXT: Read the configuration helpers and create the focused test fixture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:28:54Z
  TYPE: FACT
  CLAIM: Verified test-document hashes and read component/bootstrap slices plus existing fixtures.
    The frame helper supports explicit local/shared rich-config posture. Book Bind storage is
    independent of configuration. Tests will use real Books, normal/lesser Conduits and managed
    Spaces, with root resets and deterministic teardown. Optional configuration and active-Space
    migration policy remain outside these regressions; new/reused Spaces after upgrade are included.
  EVIDENCE:
  - tests/_frame_posture_test_support.py:93-139
  - tests/component/melder/spellbook/test_bind_lifecycle_hooks.py:39-55
  - tests/component/melder/spellbook/test_bind_lifecycle_hooks.py:520-544
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py:367-443
  - src/melder/aether/spellbook/bind/bind.py:190-223
  IMPACT: Plain red assertions can target real isolation failures in both modes without inventing
    an upgrade keyword or treating shared configuration as shared Bind callback storage.
  NEXT: Add the component tests and run them with retained JUnit evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:35:55Z
  TYPE: MEASURE
  CLAIM: First run collects 32 cases; all fail at the intended ownership assertions, with zero
    setup/teardown errors or skips. Failures cover Book aliasing (2), parent registration (2),
    inherited Bind hooks (6), child registration leaking hooks to parent (6), child clearing parent
    hooks (6), child-cleanup parent retirement (2), parent-cleanup child destruction (2), wrong
    unique disposal ownership (2), and fresh/pooled Space registration isolation (4).
  EVIDENCE:
  - artifacts/graduation_ownership_regressions_20260922/red.log:1-219
  - artifacts/graduation_ownership_regressions_20260922/red.xml
  - tests/component/melder/aether/conduit/test_conduit_graduation_ownership_regression.py:157-365
  IMPACT: Red tests reproduce actual defects in both rich-config modes; no runtime edits were
    needed. Two warnings concern the pre-existing pytest cache directory, not test behavior.
  NEXT: Run existing config/preset controls alongside the red cases with cache writing disabled;
    inspect new-file lint and verify runtime source hashes remain unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:35:55Z
  TYPE: MEASURE
  CLAIM: Combined qualification reports 32 intentional failures and 3 passing existing controls,
    with no warnings. Controls demonstrate preset Bind isolation and correct local/shared rich
    configuration behavior outside graduation. New-file Ruff found only two long imports needing
    multiline formatting; those imports are now formatted without changing test behavior.
  EVIDENCE:
  - artifacts/graduation_ownership_regressions_20260922/red_with_controls.xml
  - artifacts/graduation_ownership_regressions_20260922/red_with_controls.log
  - artifacts/graduation_ownership_regressions_20260922/lint.log
  IMPACT: The regression fixture is not the source of the failures. No xfail/skip or runtime fix
    was added. The source-hash comparison and final lint remain before handoff.
  NEXT: Verify lint and source immutability, then record the complete failure matrix in the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:37:51Z
  TYPE: MEASURE
  CLAIM: Red regression delivery is complete: 32 failing cases across nine test functions, covering
    both local and frame-wide configuration. The combined run has 3 passing pre-existing controls,
    zero errors/skips and no warnings. Final Ruff passes after import formatting. Byte hashes match
    for all 592 src Python files, including generated assets; no source Python files were added.
  EVIDENCE:
  - artifacts/graduation_ownership_regressions_20260922/red_with_controls.xml
  - artifacts/graduation_ownership_regressions_20260922/red_with_controls.log
  - artifacts/graduation_ownership_regressions_20260922/lint_final.log:1-1
  - artifacts/graduation_ownership_regressions_20260922/source_unchanged.json:1-5
  IMPACT: Tests are intentionally left red and ready to drive the later repair. Optional upgrade
    configuration is documented in the epic; it has no speculative signature tests or implementation.
  NEXT: Discuss the epic's local/shared configuration and inherited-definition rules before runtime edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T14:41:23Z
  TYPE: DECISION
  CLAIM: Owner explicitly requested additional hook-isolation tests and graduation epic turn-in.
    The added twelve cases pass within a 157-test focused selection; prior broad qualification
    remains 4118 passes and two existing owner-deferred skips. Source behavior did not change in
    the final test tranche. Graduation source, regressions and canonical documentation are complete.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/hook_isolation_final.log:1-4
  - artifacts/graduation_configuration_20260922/qualification_final.log
  - artifacts/graduation_configuration_20260922/upgrade_review.md
  - artifacts/graduation_configuration_20260922/documentation_preservation.json
  IMPACT: Close the graduation epic and its implementation/red-regression tasks. Retain evidence
    and archive promoted patch contracts. Packaged build generation remains explicitly held in
    TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved; no build runner was invoked.
  NEXT: None for graduation source. The separate packaged-asset task waits for owner authorization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10
## Context / Handoff Summary
CLOSED by owner-requested turn-in after additional hook-isolation qualification. Graduation creates
an independent empty Book, preserves the Conduit/ID/creation stores, and resets old Book-specific
hooks and runtime overlays. Frame-wide rich configuration stays canonical and frame-owned; its
deliberately configured defaults may seed the new Book without sharing runtime registration state.

All twelve added scenarios pass within 157 focused tests. Prior affected qualification: 4118 pass,
two existing owner-deferred skips. Canonical architecture/components, measured ranges and the scoped
graph descriptions are promoted; document indexes validate. Packaged build assets remain untouched.
See artifacts/graduation_configuration_20260922/upgrade_review.md for behavior and concurrency limits.
Only TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved remains queued for packaging.