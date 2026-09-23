# Task: Implement Spellbook bind lifecycle hooks and recording

- Completed: 2026-09-22T18:47:41Z
- Summary: Book/Conduit Bind controls, stage execution, recording and 729-test qualification accepted;
  canonical documentation promoted and original patch contracts archived. Packaged generation remains held.

## Metadata
- Task ID: TASK-2026-09-21-implement-bind-lifecycle-hooks
- Epic: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-21T10:52:00Z
- Updated: 2026-09-22T18:47:41Z

## Objective
Implement the researched pre-bind reference checks, actual-Spell activation and post-bind hooks,
configured directly on Spellbook. Include recording, lifecycle and compatibility tests. Hold all
generated/build assets until the owner reviews and approves the code.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorized all feature code after reviewing the expanded epic.
  Required patch contracts must be recorded and consumed before runtime edits.
- EXECUTION_BOUNDARY: Book/Bind APIs, matching Conduit facades, lifecycle, book-twin marker wiring, focused tests and
  authored documentation. No build-asset runner, graph/index regeneration, wheel or publication.
- DEPENDENCIES: Parent epic's Cross-Component Impact Map and discovery task/evidence.
- EXIT_GATE: Implementation and focused qualification pass; source ready for owner code review;
  generated artifacts remain held.
- FAILURE_ESCALATION: Record source contradictions or failures before the next tranche. Ask only
  when a material design choice cannot be resolved within the approved feature scope.

## Scope Boundaries
- In scope: direct Book hook registration; Bind pre/activation; active/inactive post; cleanup,
  recording markers and updates; existing wrappers and generic persistence compatibility tests.
- Out of scope: arbitrary callback serialization, automatic restore code reattachment, mutation/
  rehash frameworks, lesser bind enablement, unrelated ownership work and generated assets.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner requested turn-in; canonical documentation promoted and separate asset hold preserved.

## Steps / Checklist
- [x] Read current implementations and record/consume patch contracts; stale graph bypassed via source.
- [x] Implement registration, dispatch, cleanup and marker emission.
- [x] Qualify callback stages, failures, scopes, wrappers and recording/replay compatibility.
- [x] Review changes and leave code ready for owner approval with assets held.
- [x] Add Conduit registration/clearing facades and qualify owner delegation, admission and recording.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/configuration/spellbook_configuration.py
- src/melder/utilities/custom_exceptions/hook_execution_error.py (bind/Meld documentation)
- Focused tests in tests/unit, tests/component and tests/integration for these owners.
- Parent epic, patch contracts and task-linked evidence.

## Validation
729 passed in 21.78 seconds using .venv_new through uv offline/no-sync and Python -X gil=0.
Includes 58 new cases: 45 lifecycle/component and 13 recording/replay/graft integration checks.
New tests pass policy-compatible Ruff; fatal checks pass on all touched code. Full legacy-file lint
has 253 recorded findings; no broad reformat. Coverage/performance comparisons were not measured.
Build-asset hold verified: 15 Python files match their before hashes; no generators were run.

## Risks / Rollback Notes
Keep callback execution distinct from application-object Meld hooks. New-Spell activation occurs
before lookup collision checks. Unpublished cleanup must avoid registered-world removal. Post-bind
must describe per-binding registration completion rather than an outer transaction commit.

## Applicable Anti-Patterns
- No callback field whitelist, new cache lifecycle or callable serialization.
- No generated assets before explicit owner code approval.
- No broad defensive guards, unrelated refactors or hidden module-owned state.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/
  - artifacts/bind_hooks_implementation_20260921/
  - artifacts/bind_hooks_turn_in_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Notes
- DATETIME: 2026-09-22T18:32:58Z
  TYPE: DECISION
  CLAIM: Owner requests turn-in of the current bind-hook epic after accepting its examples and
    release notes. Close this implementation task, its discovery task, the intermediate/expert
    documentation task and the parent epic. Promote the accepted contract into canonical source
    documentation and archive its temporary patches; preserve the separate packaged-asset hold.
  EVIDENCE:
  - Owner's current instruction: "turn in this epic seems done".
  - tickets/tasks/completed/2026-09-22_add_bind_hook_intermediate_and_expert_examples_task.md
  - tickets/tasks/completed/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md
  IMPACT: User acceptance is supplied; no further confirmation is required for this closure set.
    Other epics, including the narrower pool-hook epic, retain their existing status.
  NEXT: Promote the bind-hook documentation delta, then archive and synchronize the four tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T10:52:00Z
  TYPE: DECISION
  CLAIM: Owner authorized all code for the bind-hook feature and explicitly withheld build-asset
    generation until code review. Implement the epic's recommended scope, including marker-only
    persistence and honest restore shortfalls; automatic callback reattachment was conditional extra
    work, not the proposed default. Existing owner certification and role authorization persist.
  EVIDENCE:
  - Owner's implementation request following the expanded impact review.
  - tickets/epics/completed/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md:148-348
  IMPACT: Runtime changes and focused tests are authorized. Asset/codegen delivery remains held.
  NEXT: Read source and wiring for the exact edit units, then record the patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:02:42Z
  TYPE: DECISION
  CLAIM: Consumed the architecture, binding, recording and control-flow patch contracts. Public
    add_bind_hooks appends ordered sequences; clear_bind_hooks clears all stages. Pre rejects by
    raising; activation/post receive Spell; return values are ignored. One immutable registry tuple
    is retained per bind so reentrant/concurrent updates affect later binds. User callbacks run
    outside the Bind construction lock. Registry updates and Book marker refresh serialize on Bind.
  EVIDENCE:
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/architecture_patch.md
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/component_patch_binding.md
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/component_patch_recording.md
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/code_description_patch_bind_hooks.md
  - src/melder/aether/spellbook/bind/bind.py:183-551
  - src/melder/aether/spellbook/spellbook.py:4753-4964
  IMPACT: Patch mapping is core -> stage/snapshot/cleanup tests; recording -> marker/restore/graft
    compatibility tests; delivery -> source review with all generators held. The graph hash/line
    verification refused, so relevant source was read directly without regenerating the graph.
  NEXT: Implement the Bind owner and Book/recording wiring, then run the focused regression suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:14:00Z
  TYPE: FACT
  CLAIM: Initial source edits now add Book add_bind_hooks/clear_bind_hooks, immutable Bind callback
    sets, pre/activation/post dispatch, local failed-activation cleanup and book-twin marker plumbing.
    They have not been tested yet. Owner interrupted to ask whether existing Meld hooks can be cleared.
    Existing configuration hooks reject changes after freeze; public Conduit registration adds local
    Meld hooks but does not clear them. Per-Spell replacement and Meld map replacement exist internally,
    with no matching public clear-hooks method. The new clear_bind_hooks is an additive API choice.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:247-440
  - src/melder/aether/spellbook/spellbook.py:4758-4858
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:692-762
  - src/melder/aether/conduit/conduit.py:1656-1710
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  - src/melder/aether/spellbook/spell.py:638-682
  IMPACT: Answer the API-consistency question before further implementation. Current source changes
    remain unqualified; no tests or assets were generated during the interrupted implementation.
  NEXT: Resolve owner direction on the added clear API, then finish documentation and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:16:51Z
  TYPE: DECISION
  CLAIM: Owner approved clear_bind_hooks and directed completion of the bind-hook implementation.
    Clearing/re-registering Conduit and Meld hooks is a separate investigation after this feature;
    do not expand current runtime edits into those systems. Initial implementation is ready for
    focused regression work; documentation and qualification remain outstanding.
  EVIDENCE:
  - Owner's approval to proceed with clearing and finish bind hooks before investigating other hooks.
  - src/melder/aether/spellbook/spellbook.py:4758-4858
  IMPACT: Continue with the selected additive API; there is no open approval gate on clear behavior.
    Build assets remain held until the finished source receives owner review.
  NEXT: Add focused lifecycle and recording regressions, run them, and repair only evidenced failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:16:51Z
  TYPE: MEASURE
  CLAIM: Initial compatibility selection passes 238 tests: existing Bind unit tests, the earlier
    bind characterization and creation-hook integration. Core registration, dispatch, cleanup and
    marker wiring are present. New-feature regression tests and recording qualification are next.
  EVIDENCE:
  - artifacts/bind_hooks_implementation_20260921/initial_compatibility.log:1-5
  IMPACT: Existing native Bind behavior and current Meld hooks remain compatible in this selection.
    This is not yet complete new-feature qualification; generators remain unrun.
  NEXT: Add and run the focused lifecycle and persistence regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-21T11:23:53Z
  TYPE: MEASURE
  CLAIM: The first 15 new lifecycle tests pass. Expanded cases found a real cleanup gap: a native
    collision after activation leaves the rejected, callback-visible Spell alive. Two other failures
    are test call-site mistakes (scan permissions and notch arguments), confirmed against signatures.
  EVIDENCE:
  - artifacts/bind_hooks_implementation_20260921/lifecycle_first.log:1-2
  - artifacts/bind_hooks_implementation_20260921/lifecycle_expanded.log:1-22
  - src/melder/aether/spellbook/bind/scan.py:145-241
  - src/melder/aether/conduit/conduit.py:4562-4656
  IMPACT: Track publication start in each Book bind path and locally retire only unregistered failed
    allocations. Preserve already-published state on post failures and existing target indexes.
  NEXT: Patch the unpublished failure boundary and correct the two test calls, then rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:41:40Z
  TYPE: MEASURE
  CLAIM: Recording plus lifecycle and Book unit qualification passes 193 tests. Real recorder cases
    cover initial/re-freeze markers, late clear/re-add, whole-twin replacement, checkpoint JSON,
    formations, external emission tap, recorder gates, missing callback code during full restore,
    legacy absence, receiving-book active/staged graft and activation-before-capture ordering.
    Earlier four Book unit failures were outdated doubles and are corrected. New test files pass
    Ruff with UP007/UP045 excluded to honor the role's Optional/Union policy. Full legacy-file Ruff
    reports 253 findings, including existing style issues and policy-conflicting union suggestions;
    no blanket reformat or suppression was applied.
  EVIDENCE:
  - artifacts/bind_hooks_implementation_20260921/recording_first.log:1-4
  - artifacts/bind_hooks_implementation_20260921/new_test_lint.log:1-1
  - artifacts/bind_hooks_implementation_20260921/lint_first.log
  - tests/integration/melder/crystallizer/test_bind_hook_recording.py
  IMPACT: New behavior works across recording/replay without a serializer or loader extension.
    Local duplicate IDs are now refused before map publication; rejected activated Spells retire.
    Remaining work is the consolidated compatibility run and source/asset-hold review.
  NEXT: Run the final scoped selection and compare held build-asset hashes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:45:14Z
  TYPE: MEASURE
  CLAIM: Final selected compatibility run passes all 716 tests with zero failures/errors/skips.
    New behavior has 45 regressions. Source readback covers the public API, immutable operation set,
    callback error/cleanup boundaries and complete marker emission. Fatal checks and new-test lint
    pass. All 15 build-asset Python sources retain their original hashes.
  EVIDENCE:
  - artifacts/bind_hooks_implementation_20260921/final.log:1-11
  - artifacts/bind_hooks_implementation_20260921/final.xml
  - artifacts/bind_hooks_implementation_20260921/fatal_lint.log:1-1
  - artifacts/bind_hooks_implementation_20260921/new_test_lint.log:1-1
  - artifacts/bind_hooks_implementation_20260921/asset_hold.log:1-1
  - artifacts/bind_hooks_implementation_20260921/code_review.md
  IMPACT: Source is ready for owner review. No runtime feature work remains in this tranche;
    documentation promotion and all generators remain held for explicit code approval.
  NEXT: Owner reviews the completed source; proceed with assets only after approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T11:58:24Z
  TYPE: DECISION
  CLAIM: Owner requires a matching Conduit facade for every new public Spellbook API. Add
    add_bind_hooks and clear_bind_hooks forwarding to the same owning Book registry. Preserve
    cleaned/normal ownership guards so lessers cannot modify borrowed book policy. Hook setup follows
    the Book's live-update contract; actual bind retains its separate frame-posture admission rules.
  EVIDENCE:
  - Owner's explicit Conduit facade request.
  - src/melder/aether/conduit/conduit.py:3095-3297
  - src/melder/aether/spellbook/spellbook.py:4758-4858
  IMPACT: Reopen the same implementation task for this missing public surface. No duplicate registry,
    extra bind transaction or change to normal Conduit/Meld runtime-hook systems. Assets stay held.
  NEXT: Implement the two thin facades and regression tests through the public Conduit surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T12:06:32Z
  TYPE: MEASURE
  CLAIM: Both Conduit facades are implemented with normal/liveness guards and direct Book
    delegation. The new facade selection passed 69 cases; one test reused the same unqualified class
    name across post-conjure registrations and hit native DUPLICATE_SPELL_NAME validation. Corrected
    that fixture to use distinct class targets. Source fatal checks and new-test Ruff both pass.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3096-3182
  - artifacts/bind_hooks_implementation_20260921/conduit_facades.log
  - tests/component/melder/spellbook/test_bind_lifecycle_hooks.py
  - tests/integration/melder/crystallizer/test_bind_hook_recording.py
  IMPACT: Delegation, lesser/cleaned refusals, automatic posture parity and recorded clear/re-add
    are covered. Existing runtime-hook registries were not changed and assets remain held.
  NEXT: Run the consolidated compatibility selection with the corrected fixture and hand off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T12:10:10Z
  TYPE: MEASURE
  CLAIM: The consolidated selection passes 729 tests after adding both Conduit facades. Thirteen
    added facade cases cover active/inactive/direct-Book delegation, owner-wide clearing/re-add,
    lesser and cleaned refusal, automatic-mode setup without bypassing actual bind admission,
    invalid callback forwarding and recorded marker replacement. All 15 build-asset sources remain
    unchanged. Source readback confirms thin delegation with no new registry or transaction.
  EVIDENCE:
  - artifacts/bind_hooks_implementation_20260921/final_with_conduit.log:1-12
  - artifacts/bind_hooks_implementation_20260921/final_with_conduit.xml
  - artifacts/bind_hooks_implementation_20260921/asset_hold_with_conduit.log:1-1
  - src/melder/aether/conduit/conduit.py:3098-3182
  IMPACT: Both new public Spellbook APIs are available through the normal Conduit facade. Source
    is ready for owner review; all generators remain held until explicit approval.
  NEXT: Owner reviews source and approves or requests changes before asset generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Follow-up Requested
After bind hooks are complete, investigate public clearing/re-registration for Conduit and Meld hooks,
including their shared/configured and local behavior. This is deferred investigation, not current edits.

- DATETIME: 2026-09-22T18:38:00Z
  TYPE: DECISION
  CLAIM: Closure consumes all five bind-hook patch contracts. Promote Book/Bind stage ownership,
    immutable capture, normal-Conduit delegation, failure boundaries and value-only recording into
    canonical source maps and five existing graph descriptors. Preserve current configuration seed
    semantics already promoted by graduation. Correct the two source-confirmed stale component
    claims: hook names are validated, and Crystallizer activation catches up root policy only.
  EVIDENCE:
  - system_docs/patches/completed/bind_lifecycle_hooks_2026_09_21/architecture_patch.md
  - src/melder/aether/spellbook/bind/bind.py:266-438
  - src/melder/aether/spellbook/spellbook.py:4763-4864
  - src/melder/crystallizer/crystallizer.py:605-694
  IMPACT: This is accepted documentation closeout, not runtime work or a repository-wide audit.
    Canonical before-images preserve replaced text. Refresh documentation indexes/assembly only;
    defer packaged/LLM generation to the existing separate blocked task.
  NEXT: Apply the bounded canonical prose and descriptor changes and verify their indexing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T18:41:00Z
  TYPE: FACT
  CLAIM: Canonical bind-stage, facade, cleanup and recording prose is promoted. The bounded
    descriptor refresh reports existing SEMANTICS_STALE stamps for large classes whose source moved
    since previous authoring. Preserve those honest stamps rather than marking whole classes reviewed.
  EVIDENCE:
  - artifacts/bind_hooks_turn_in_20260922/refresh_bind_documentation.py
  - system_docs/src_architecture.md
  - system_docs/src_components.md
  IMPACT: Mechanical hashes/positions can refresh without falsely accepting unrelated semantic prose.
    No runtime code or package assets changed. Native unknowns and the separate broad audit remain.
  NEXT: Assemble/check documentation indexes, then archive accepted tickets and patches.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T18:42:54Z
  TYPE: DECISION
  CLAIM: Owner-accepted source and documentation are complete. Promoted Bind stage/recording/facade
    contracts into both canonical source maps and five descriptors. Rebuilt and checked only their
    documentation indexes/graph; recorded historical text and mechanical source lengths. Archive all
    five original patch files and close this task with its discovery/tutorial siblings and epic.
  EVIDENCE:
  - artifacts/bind_hooks_turn_in_20260922/documentation_check.log
  - artifacts/bind_hooks_turn_in_20260922/documentation_receipt.json
  - docs/intermediate/hooks.md
  - docs/expert/bind-hooks.md
  IMPACT: No remaining implementation work in this epic. Packaged/LLM generation stays visibly
    deferred on its existing blocked task; no runtime suite rerun is needed for metadata-only closure.
  NEXT: none; await the separately tracked build authorization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed by owner instruction. Source/API/tests/tutorials/release notes are accepted; canonical
contracts and graph wiring are promoted, and temporary patch records are archived. Evidence is in
bind_hooks_implementation_20260921, bind_hook_examples_20260922 and bind_hooks_turn_in_20260922.
Pending packaging belongs to TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved.

Historical review handoff:
Code complete, including Conduit.add_bind_hooks and Conduit.clear_bind_hooks. All 729 selected tests
pass, including 58 new lifecycle/recording/facade cases. Read
artifacts/bind_hooks_implementation_20260921/code_review.md for the API and review map. Public
add_bind_hooks appends all three stages; owner-approved clear_bind_hooks clears future bindings.
Both have matching normal-Conduit facades to the same Book registry. Lessers cannot change borrowed
Book policy; hook setup leaves actual bind admission rules intact.
Captured immutable tuples keep an in-flight operation stable. Callback code is not serialized;
generic restore shortfalls and receiving-book graft behavior are qualified. Native local duplicates
now refuse before map publication and rejected activated allocations retire safely.
No generators ran; all 15 build-asset Python files are unchanged. Await code approval before docs/
asset promotion. The separate runtime-hook clearing investigation is ready in its linked task.

## Noting Behavior
Record implementation decisions, source findings and test results before continuing each tranche.
