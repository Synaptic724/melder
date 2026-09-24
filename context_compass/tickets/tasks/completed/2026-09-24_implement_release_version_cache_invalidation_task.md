# Task: Add release-version compatibility to persisted creation caches

## Metadata
- Task ID: TASK-2026-09-24-implement-release-version-cache-invalidation
- Epic: EPIC-2026-09-23-invalidate-creation-cache-on-melder-version-change
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-24T09:20:31Z
- Updated: 2026-09-24T09:52:40Z
- Completed: 2026-09-24T09:52:40Z
- Summary: Exact-release cache admission implemented and qualified; version 0.2.51 and public notes delivered.

## Objective
Implement the approved release stamp, qualify cold/warm behavior, complete the epic, advance
Melder from 0.2.50 to 0.2.51, and update the public next-release draft.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorizes implementation, epic completion, version bump and release notes.
- EXECUTION_BOUNDARY: CachingSystem envelope, cache tests, scoped source documentation, version and
  release notes. Complete all tracking before final package/LLM generation and checks.
- DEPENDENCIES: Parent epic's source-backed concrete plan and linked patch contracts.
- EXIT_GATE: Required compatibility regressions pass; docs/version/epic are delivered; final assets current.
- FAILURE_ESCALATION: Record unexpected runtime failures; do not add per-meld checks or unrelated refactors.

## Scope
- Runtime: src/melder/utilities/caching_system/caching_system.py only, plus canonical version metadata.
- Tests: existing cache utility, schema-history and runtime integration owners; bounded asset checks.
- Documentation: cache ownership/compatibility descriptions, related indexes/descriptors and release draft.
- Keep Crystallizer record schema, live objects, spell identity and runtime execution paths unchanged.
- No wheel, publishing, dependency change or compiler IR/Mojo implementation.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-authorized implementation, qualification, version bump and documentation are complete.

## Work
- [x] Record/consume the cache-policy patch contracts.
- [x] Add meaningful real-bundle regressions and capture the failing baseline.
- [x] Add the envelope stamp and schema generation; qualify affected behavior.
- [x] Complete source docs, epic turn-in, version 0.2.51 and public release notes.
- [x] Qualify generated assets; repeat builders/checks after final turn-in per owner ordering.

## Validation
Real marshal envelopes; same/different/missing/malformed release; legacy schema/interpreter checks;
automatic/dynamic cold rebuild and warm reuse. Fresh-process import and relevant cache suites.
Do not claim repository-wide coverage.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/cache_release_guard_20260924/
  - system_docs/patches/completed/cache_release_guard_2026_09_24/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Applicable Anti-Patterns
- [x] No runtime change before the approved contracts are recorded.
- [x] No guards added to private methods or new work added to meld execution.
- [x] No version override API or mirrored package version constant.
- [x] No separate task or file edits after final asset regeneration.

## Notes
- DATETIME: 2026-09-24T09:52:40Z
  TYPE: DECISION
  CLAIM: The authorized feature and release closeout are complete. Generation 9 stores and enforces
    the canonical Melder release; legacy/malformed/mismatched bundles rebuild through existing paths.
    Final package version is 0.2.51. Three test files, canonical cache documentation/descriptors and
    the focused public next-release draft are updated. The old 0.2.50 release is preserved.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/validation.md:1-51
  - artifacts/cache_release_guard_20260924/final_version.log:1-3
  - artifacts/cache_release_guard_20260924/final_metadata.log:1-2
  - artifacts/cache_release_guard_20260924/documentation_and_scope.json
  IMPACT: 138 unique final-version tests qualify across the 137-case run and deferred asset stamp
    check. All package/LLM checks passed. Source comparison isolates the cache owner and version
    metadata; only the reread cache class was semantically accepted. Turn in the epic/task and
    archive promoted patch contracts. All feature inputs are tracked; the final LLM build uses
    its normal tracked-input mode, leaving the unrelated untracked performance experiment outside it.
  NEXT: Rerun both builders and their checks after this final tracking update, with no subsequent edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:37:05Z
  TYPE: MEASURE
  CLAIM: Fresh-process source import succeeds with the canonical release. A preserved generation-8
    reader rejects a generation-9 bundle. The asset accelerator reuses an unchanged manifest and
    refreshes after its version-bearing content changes. Header-normalization-only medians are
    328.29 ns before and 392.35 ns after (7 x 100000 empty-envelope calls); not a conjure or meld measure.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/compatibility_probe.json
  - artifacts/cache_release_guard_20260924/caching_system_before.py:496-547
  IMPACT: Legacy downgrade fencing and existing asset behavior are qualified. No hot-path changes.
    Initial standalone probe needed src on sys.path, as pytest's conftest normally supplies it.
    The release draft is currently empty and 0.2.50.md exists; create focused 0.2.51 notes without
    restoring the previous release content. uv.lock has no project version field to update.
  NEXT: Promote bounded cache documentation and add the public 0.2.51 release draft.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:31:24Z
  TYPE: MEASURE
  CLAIM: All 138 planned cache utility, schema, runtime, component, executor-rehydration and
    package-metadata tests pass with no skips. Version remains 0.2.50 during this qualification.
    Documentation-only docstring refinements preserve the implementation result.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/qualified.log:1-3
  - artifacts/cache_release_guard_20260924/qualified.xml
  IMPACT: Proceed to bounded legacy-reader/asset probes and source-document promotion. Repeat
    version-sensitive checks after the requested 0.2.51 bump, then generate packaged assets last.
  NEXT: Finish import/compatibility probes and update scoped canonical documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:29:08Z
  TYPE: MEASURE
  CLAIM: The first implemented selection passes all 63 utility/schema/runtime tests. Eight new
    automatic/dynamic cases cover release upgrade, downgrade, prerelease and local-version changes
    with identical spell IDs and schema. They forbid old cached-context publication on mismatch,
    then forbid plan-phase rebuilding on the next compatible run while both spells meld correctly.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/green.log:1-2
  - src/melder/utilities/caching_system/caching_system.py
  - tests/integration/melder/spellbook/test_cache_runtime_integration.py:448-559
  IMPACT: Generation 9 and the exact release stamp are implemented. Private methods gained no
    cleaned checks, and no orchestration/meld code changed. Version remains 0.2.50 until turn-in.
  NEXT: Run the planned compatibility selection and import/asset-accelerator probes before documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:24:51Z
  TYPE: MEASURE
  CLAIM: The real-bundle baseline has 7 intended failures and 19 passes. Emission omits the release
    stamp; different/empty/null/numeric/bytes stamps are ignored; a missing stamp retains old payloads.
    The populated matching control and real existing schema/Python/conduit/payload rejection pass.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/red.log:1-66
  - tests/unit/melder/utilities/test_caching_system.py:79-118
  - tests/unit/melder/utilities/test_caching_system.py:335-446
  IMPACT: Regressions exercise the actual path and encoding, not an absent decoy file. Runtime
    implementation can now be applied against proven failure symptoms.
  NEXT: Add the canonical release stamp and generation 9, then extend runtime integration checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:21:41Z
  TYPE: DECISION
  CLAIM: Consumed architecture, component and code-flow contracts. Map empty/load/write metadata
    to real marshal-envelope unit tests; map generation 9 to schema-history tests; map mismatch
    rejection and next-run reuse to automatic/dynamic runtime tests. Existing invalid JSON-path
    fixtures will be replaced with real .melc inputs and a populated accepted control.
  EVIDENCE:
  - system_docs/patches/completed/cache_release_guard_2026_09_24/architecture_patch.md:1-34
  - system_docs/patches/completed/cache_release_guard_2026_09_24/component_patch_caching_system.md:1-25
  - system_docs/patches/completed/cache_release_guard_2026_09_24/code_description_patch_cache_gate.md:1-31
  IMPACT: Source/test mapping is complete. Production patch remains one file; no per-meld or
    compiler-phase changes. Source hashes captured before edits for final scope verification.
  NEXT: Add and run the real-envelope regressions before changing CachingSystem.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:20:31Z
  TYPE: DECISION
  CLAIM: Owner authorizes implementation, then epic completion, one release increment to 0.2.51
    and public release notes. The parent plan maps this to one runtime envelope owner and three
    existing cache test files. All relevant source and these tests were read in discovery.
  EVIDENCE:
  - Owner's current implementation and release instruction.
  - tickets/epics/completed/2026-09-23_invalidate_creation_cache_on_melder_version_change_epic.md:133-212
  IMPACT: Proceed through red regressions, implementation, qualification and documentation.
    Asset generation is the final operation after all source and tracking edits.
  NEXT: Consume the three patch contracts and add the real-bundle regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed: exact-release creation-cache admission, cache generation 9, meaningful real-file tests,
canonical documentation and public 0.2.51 notes. Runtime version is 0.2.51. Validation receipt links
all red/green/current-version and compatibility evidence. No meld/compiler/record-format changes.
All tracking is closed before the final direct asset-builder repetition. No separate asset task.
