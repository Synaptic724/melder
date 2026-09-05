# Task: Verify the complete ordered-disposal contract

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-end-to-end-validation
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/completed/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Verified full Windows CI runtime: 11359 passed, 28 skipped, 15 xfailed, 1 xpassed; asset and hygiene checks passed.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

## Objective
Assemble actual evidence that the agreed order survives configuration, binding, compilation,
cleanup, and record/replay, then hand the complete program back for acceptance.

## Ticket Contract
- ENTRY_GATE: All implementation tasks and docs/assets task are verified; board routes here.
- EXECUTION_BOUNDARY: Relevant tests/checks, focused regressions for discovered gaps, and
  ticket/story/epic outcome synchronization. Fixes return to their owning task scope.
- DEPENDENCIES:
  `tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  `tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
  `tickets/tasks/completed/2026-09-04_ordered_disposal_crystal_replay_task.md`
  `tickets/tasks/completed/2026-09-04_ordered_disposal_docs_assets_task.md`
- EXIT_GATE: Acceptance criteria have concrete executed evidence or clearly stated platform
  gaps; no unresolved feature regression is presented as complete; owner accepts closure.
- FAILURE_ESCALATION: Route defects to the owning task with a reproduction. Do not skip supported
  platforms or rewrite synchronization to satisfy an unverified test assumption.

## Scope Boundaries
- In scope: feature verification and final review/closure preparation.
- Out of scope: publishing, signing, committing, pushing, unrelated test repairs, coverage guesses.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

## Required Reading and Evidence
- All eight preceding task outcomes and their test commands/results.
- `system_docs/tests_architecture.md` and relevant indexed test-component sections.
- Current `.github/workflows/python-publish.yml` for supported interpreter/platform cells.
- `.github/workflows/build-src-assets.yml` and `.github/workflows/build-repo-assets.yml`.
- Current pytest configuration and relevant fixtures before selecting test commands.
- The discovery Validation section explicitly distinguishes the old generic hash probe
  from the failed Melder import under Python 3.13. It is not runtime proof.

## Steps / Checklist
- [x] Resolve the available 3.14 interpreter and record version/free-threading mode.
- [x] Collect prior focused evidence; rerun only where new changes or cross-boundary gaps justify it.
- [x] Exercise real book defaults plus per-spell names, both priority modes, duplicate and missing names.
- [x] Verify two separately created Spells never inherit each other's explicit list.
- [x] Exercise actual cleanup through relevant lifetimes and compiler/override/cache families.
- [x] Verify hash-seed stability using real supported binding and a stable source-defined target.
- [x] Verify configuration, active/staged replay, and applicable graft outcomes under the recorded policy.
- [x] Confirm source/repository asset checks and documentation examples remain current.
- [x] Report supported matrix cells actually run and those unavailable locally; use real CI output
      when available rather than claiming Linux validation from a Windows run.
- [x] Synchronize story/epic outcomes and patch disposition for explicit owner acceptance.

## Deliverables
One concise evidence-backed acceptance report with exact remaining gaps, if any.

## Files / Paths Impacted
- Existing focused feature tests and an integration regression only if a real gap remains.
- Task/story/epic notes and board state.
- Actual patch artifact disposition after successful validation and owner acceptance.

## Validation
- Full CI runtime command: 11,359 passed, 28 skipped, 15 xfailed, 1 xpassed in 278.44s, exit 0.
- Windows Python 3.14.0 free-threaded with PYTHON_GIL=0; runner verifies mode before/after pytest.
- Ubuntu/other Python builds and coverage measurement: Not run locally.
- Existing unawaited coroutine warning remains; no unrelated coroutine/locking repair was made.
- Source and repository assets, canonical indexes/graph, three examples, and hygiene pass.
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
- [x] No fabricated run/coverage/platform claims or unsupported skips.
- [x] No closing tasks while acceptance criteria remain unresolved.

## Done Checklist
- [x] Required behavioral and asset checks documented with actual results.
- [x] Genuine remaining gaps named with exact next actions.
- [x] Story/epic state consistent; owner accepts final closure.
- [x] Artifact dispositions and deterministic board closure sync applied when authorized.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false (closed)
- ARTIFACT_PATHS: none active
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure 2026-09-05T14:22:02Z
- Durable contracts: source architecture/components, source docstrings, README, configuration guide,
  and committed regression tests. Temporary patches/probes/validation scratch are removed at closure.
- Historical artifact citations in Notes are retained; tracked patches are recoverable from Git history.

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
  - `context_compass/tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:327-339`
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
  - `tickets/tasks/completed/2026-09-04_ordered_disposal_crystal_replay_task.md`
  - `tickets/tasks/completed/2026-09-04_ordered_disposal_docs_assets_task.md`
  IMPACT: Use PYTHON_GIL=0 and a fresh task-local pytest temp directory outside the sandbox
    due its demonstrated Windows ACL failure. Report JUnit evidence, not coverage guesses.
  NEXT: Run the exact CI runtime command, then final asset/diff checks and owner handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:21:33Z
  TYPE: MEASURE
  CLAIM: The full current CI runtime command passes on Windows 3.14.0 free-threaded with
    PYTHON_GIL=0: 11,359 passed, 28 skipped, 15 xfailed, 1 xpassed in 278.44s, exit 0.
    The runner verifies the actual process's free-threaded/GIL state before and after pytest.
    The existing unawaited coroutine warning remains. No skip/xfail was added by this feature.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe .github/scripts/run_runtime_tests.py --report context_compass/artifacts/ordered_disposal_validation_20260905/runtime.xml
  - Environment: PYTHON_GIL=0; PYTHONPATH=src plus checkout; PYTEST_ADDOPTS=-p no:cacheprovider --tb=short --basetemp=context_compass/artifacts/ordered_disposal_validation_20260905/runtime_all
  - `artifacts/ordered_disposal_validation_20260905/runtime.xml`
  IMPACT: Ordered binding, compiler/Creations, transport, capture/replay, and existing runtime
    contracts have executed full-tier evidence. This is not a Linux run or a coverage measurement.
  NEXT: Owner reviews the completed feature and accepts ticket/patch closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:21:33Z
  TYPE: MEASURE
  CLAIM: Final canonical source indexes, graph assembly --check, repository hygiene, and
    both source/corpus freshness commands pass. Corpora remain unchanged across the full runtime
    run. Current version is 0.2.3; the agent did not bump it, commit, or push. Public examples
    executed with their existing source-tree import setup and both priorities produce exact order.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check
  - Command: .venv_new/Scripts/python.exe llm_support/_builder.py --check
  - Command: .venv_new/Scripts/python.exe .github/scripts/ci_policy.py hygiene
  - `tickets/tasks/completed/2026-09-04_ordered_disposal_docs_assets_task.md`
  IMPACT: No ordered-disposal implementation remains. Ubuntu CI, separate RTD hosting/UI
    qualification, and owner acceptance are not represented as locally completed work.
  NEXT: Hand off for review; retain artifacts until owner-approved closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Verified full Windows CI runtime: 11359 passed, 28 skipped, 15 xfailed, 1 xpassed; asset and hygiene checks passed.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-05T14:22:02Z
  TYPE: FACT
  CLAIM: Consumed codex_2 notices from 13:18:03, 13:38:36, and 13:43:00 UTC. Its separate RTD
    qualification and PDF wrapping/maintenance changes remain owned by that lane; it will refresh
    the other corpus after its final prose change. Ordered-disposal runtime source is unchanged.
  EVIDENCE: tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md
  IMPACT: No unrelated RTD or workflow ticket is closed or overwritten by this action.
  NEXT: none for this closed lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Separate Findings (Not Patched)
- Pre-conjure configure_aether_frame freezes/locks configuration before the dynamic hint;
  later conjure skips its book-twin emission. The existing recorded-world configuration path works.
- Fresh graft's initial human-name lookup failed before notch in the diagnostic; explicit bind-ID
  resolution works. This is outside disposal ordering and has not received a separate source repair.
- Evidence and reproduction context are in the crystal/replay task notes. Do not silently fix these
  through new locks, recorder sweeps, or Meld fallbacks under the disposal epic.

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Verified full Windows CI runtime: 11359 passed, 28 skipped, 15 xfailed, 1 xpassed; asset and hygiene checks passed.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
IMPLEMENTED AND VERIFIED, awaiting owner review/closure. Full CI runtime result: 11,359 passed,
28 skipped, 15 xfailed, 1 xpassed on Windows 3.14t. No new skip/xfail or coverage claim.
Source/repository assets at existing v0.2.3, examples, canonical indexes/graph, and hygiene pass.
All three feature phases are complete; detailed implementation evidence stays in their tasks.
Ubuntu CI and independent RTD hosting/UI qualification remain external checks, not local evidence.
Two unrelated existing recording/name-lookup findings are recorded above, untouched.
No commit/push. Temporary patch/validation artifacts remain until owner accepts closure.
