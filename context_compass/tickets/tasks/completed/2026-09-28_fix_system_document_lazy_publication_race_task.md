# Task: Fix partial publication of the lazy system-document index

## Metadata
- Task ID: TASK-2026-09-28-fix-system-document-lazy-publication-race
- Status: done
- Owner: codex
- Agent Name: workflows_0
- Created: 2026-09-28T09:26:26Z
- Updated: 2026-09-28T09:50:15Z
- Completed: 2026-09-28T09:47:24Z
- Summary: Fixed lazy index publication ordering; eight deterministic red regressions now pass,
  128 focused tests pass and the original 16-worker case passes 200 consecutive runs. Notched
  0.2.8207; release section "Fixed: concurrent first reads of system documents". Asset and LLM checks pass.

## Objective
Fix the Windows free-threaded CI failure where SystemDocumentView.section receives a None key map
from the lazy index. Demonstrate the race in a regression before changing production behavior.

## Ticket Contract
- ENTRY_GATE: Owner supplies the CI failure and explicitly requests a fix; existing onboarding valid.
- EXECUTION_BOUNDARY: SystemDocumentView lazy-load publication and related graph view dependencies,
  regression tests, affected documentation/graph, release/version and generated assets.
- DEPENDENCIES: Python 3.14 free-threaded; current document-view and contention tests.
- EXIT_GATE: Deterministic regression fails before the fix and passes after; existing related and
  contention suites pass; docs/release/assets reflect the final change.
- FAILURE_ESCALATION: Preserve other work, isolate any separate defect, and never mask a partial load
  with a None fallback or weaken the contention assertion.

## Scope Boundaries
- In scope: atomic visibility of lazy index/text/adjacency readiness, with minimal locking changes.
- Out of scope: document content redesign, unrelated coroutine warning, wheel/deployment changes.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Authorized fix, red/green regressions, stress qualification and documentation complete;
  canonical asset builders/checks are the mandatory post-turn-in finalization step.

## Steps
- [x] Trace all related lazy-load readiness/publication paths and ownership.
- [x] Add a deterministic failing regression for the observed partial state.
- [x] Fix publication and validate focused concurrency suites.
- [x] Update docs/release and notch the source change.
- [x] Finalize generated assets after turn-in and verify both checks before delivery.

## Validation
- User CI: one failure in test_racing_every_lazy_load_at_once_is_consistent; by_key was None.
- Before fix: 8 deterministic failures, all matching the reported NoneType error.
- After fix: 128 focused query/carrier/concurrency tests passed on Python 3.14.7 free-threaded.
- Original mixed-lazy-load contention case: 200 consecutive calls, 16 workers per call, GIL disabled.
- Source/test/release diff check and all three edited document indexes pass.
- Final asset runner regenerated all three families at 0.2.8207; all checks OK.
- LLM builder regenerated src/tests/other and verified matching output proofs.
- Repeated the focused tests against the rebuilt payloads: 128 passed.
- Full repository suite and coverage: Not run; focused regression and stress qualification used.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/system_document_publication_race_20260928/
  - system_docs/patches/completed/document_index_publication_2026_09_28/architecture_patch.md
  - system_docs/patches/completed/document_index_publication_2026_09_28/component_patch_document_view.md
  - system_docs/patches/completed/document_index_publication_2026_09_28/code_description_patch_document_view.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain red/green and contention evidence after turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T09:26:26Z
  TYPE: HYPOTHESIS
  CLAIM: The traceback suggests a lazy-load ready sentinel becomes visible before its companion
    key map, allowing another free-threaded reader to return incomplete index state.
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_system_document_view.py:173-190
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:717-736
  IMPACT: Asset rebuild integrity does not establish runtime lazy-load thread safety.
  NEXT: Read the complete affected implementation and contention test to identify the publication boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T09:28:36Z
  TYPE: FACT
  CLAIM: _index uses _sections as its ready sentinel but assigns _sections before constructing and
    publishing _by_key. A second reader skips initialization in that window and returns None as its
    map. This exactly explains section's TypeError. The test module incorrectly calls separate
    assignments benign/atomic. _doc publishes a fully constructed carrier through one reference;
    _graph publishes the completed imported module through one reference. Neither uses this split sentinel.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:349-411
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:1007-1021
  - tests/integration/melder/multithreading/test_multithreading_system_document_view.py:12-34
  IMPACT: Fix index publication rather than regenerating data, adding a None fallback or weakening the test.
  NEXT: Force a reader to enter while the mapping constructor is paused, then preserve the ready sentinel
    until both immutable index values are complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T09:28:36Z
  TYPE: PLAN
  CLAIM: Use the minimal readiness-last fix: construct/publish _by_key before assigning _sections.
    Keep the existing two fields, signatures and lock-free reads. Stage concurrency patch contracts.
    Regression seam is the stdlib mapping constructor: pause the first loader there, let a second
    public lookup run, then release/join. A second test injects a construction failure and checks retry.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:349-377
  - context_compass/system_docs/patches/active/document_index_publication_2026_09_28/architecture_patch.md:1-26
  IMPACT: Proves the exact interleaving and exception-poisoning variant without scheduling sleeps or
    weakening the public result assertions. Avoid an unrelated cache-field/schema refactor.
  NEXT: Read staged patch contracts, add the two regressions for all four document views and capture red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T09:33:00Z
  TYPE: MEASURE
  CLAIM: Read all three staged contracts before adding regressions. Mapping: ready-last invariant ->
    _index assignment ordering -> paused-constructor lookup; failed construction -> no ready marker ->
    successful retry. All eight parameterized regressions fail on unchanged runtime source with the
    exact NoneType error in section; 11 existing contention tests were deselected for this red run.
    Interpreter is Python 3.14.7 free-threaded with -X gil=0.
  EVIDENCE:
  - context_compass/artifacts/system_document_publication_race_20260928/regressions_red.log:1-76
  - tests/integration/melder/multithreading/test_multithreading_system_document_view.py:125-189
  IMPACT: The CI race and cache-poisoning variant are deterministic reproductions, not probabilistic failures.
  NEXT: Publish the map before the section marker and run the regression plus related query/concurrency suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T09:34:43Z
  TYPE: MEASURE
  CLAIM: Readiness-last ordering makes all focused query/carrier/concurrency tests pass: 128 passed.
    The eight deterministic regressions previously failed with the reported NoneType error. The
    original mixed-lazy-load test also completed 200 consecutive calls, 16 workers each, in a
    Python 3.14.7 free-threaded process with the GIL disabled. The focused diff whitespace check passes.
  EVIDENCE:
  - context_compass/artifacts/system_document_publication_race_20260928/focused_green.log:1-3
  - context_compass/artifacts/system_document_publication_race_20260928/mixed_load_stress.log:1-2
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:353-389
  IMPACT: The exact race and failure/retry variant are repaired without adding locks or changing public APIs.
  NEXT: Promote the publication contract to docs/graph, notch the source change and rebuild assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T09:43:41Z
  TYPE: FACT
  CLAIM: Notched the live source version from 0.2.8206 to 0.2.8207 for this publication-order fix.
    Added release section "Fixed: concurrent first reads of system documents". Promoted readiness-last
    and retry semantics to the source/test maps and corrected the affected component's stale claim that
    package exports were eager StaticSystemDocument objects; the loader exposes lazy query views.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_system_documents/system_documents.py:56-96
  - src/melder/utilities/ai_native_support_tools/system_document_view.py:353-389
  IMPACT: Runtime behavior and maintained documentation agree. No public signature or eager-load change.
  NEXT: Regenerate/accept the affected graph nodes, verify preservation/indexes, then finalize assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T09:47:24Z
  TYPE: FACT
  CLAIM: Documentation and graph promotion verified. Initial extraction and acceptance hit a Windows
    EINVAL opening system_document_view.json; retry completed with zero skipped files, then the module
    and affected class were accepted and the graph assembled. All edited indexes are current.
    Preservation accounts for eight obsolete export/lifecycle lines and three remeasured test-map
    values; every other baseline line is retained. No unrelated source changes were made.
  EVIDENCE:
  - context_compass/artifacts/system_document_publication_race_20260928/graph_extract_retry.log:1-6
  - context_compass/artifacts/system_document_publication_race_20260928/graph_accept.log:1-4
  - context_compass/artifacts/system_document_publication_race_20260928/graph_assemble.log:1-4
  - context_compass/artifacts/system_document_publication_race_20260928/doc_preservation.json:1-28
  IMPACT: The runtime fix is qualified and documented; ready for final generated outputs.
  NEXT: Run the canonical asset/LLM builders and checks; record the actual finalization result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T09:50:15Z
  TYPE: MEASURE
  CLAIM: Finalization complete: the actual _build_asset_runner regenerated agent documentation,
    bind guard and system documents at 0.2.8207, and every --check line is OK. LLM bundles rebuilt
    with --include-untracked and all three output proofs match. The focused runtime suites still
    pass against the regenerated payloads: 128 passed. No outstanding work in this fix.
  EVIDENCE:
  - context_compass/artifacts/system_document_publication_race_20260928/assets_build.log:1-3
  - context_compass/artifacts/system_document_publication_race_20260928/assets_check.log:1-3
  - context_compass/artifacts/system_document_publication_race_20260928/llm_check.log:1-3
  - context_compass/artifacts/system_document_publication_race_20260928/final_packaged_green.log:1-3
  IMPACT: Deliver the verified publication-order correction and its generated assets.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Source fix is complete at 0.2.8207. SystemDocumentView._index publishes its key map before its section
readiness marker. This removes the real free-threaded partial-read window and permits retry after map
construction failure. Eight deterministic regressions failed first; 128 focused tests and 200 original
16-worker contention calls pass with GIL disabled. Docs/graph/release promoted and patch contracts
archived. Actual asset/LLM builders and checks completed successfully, followed by 128 passing tests
against rebuilt payloads. The unrelated coroutine warning was not investigated. No remaining work.
