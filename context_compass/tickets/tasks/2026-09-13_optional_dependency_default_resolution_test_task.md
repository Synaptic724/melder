# Task: Test Optional dependency with a None default

## Metadata
- Task ID: TASK-2026-09-13-optional-dependency-default-resolution-test
- Story: none
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T14:45:34Z
- Updated: 2026-09-13T16:25:07Z

## Objective
Honor ordinary Python defaults by suppressing inferred DI edges while retaining explicit descriptors
and meld overrides. Preserve the executed characterization and red-to-green regression evidence.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests the experiment; existing updater_0 certification remains active.
- EXECUTION_BOUNDARY: Default-precedence integration regressions, the legacy experiment entry point,
  requirements classification, cache compatibility, related docs/generated assets and this task's evidence.
- DEPENDENCIES: Current public Spellbook/Conduit APIs and .venv_new Python 3.14.7 free-threaded.
- EXIT_GATE: Executed registered/missing cases, exact outcomes and source-backed explanation.
- FAILURE_ESCALATION: Preserve and report unexpected runtime behavior without silently fixing the library.

## Scope
- Use a concrete Something class and a consumer with dependency: Optional[Something] = None.
- Compare absent/default/named/different-spellframe provider registration in automatic prebind and
  dynamic pre/post-conjure binding.
- Confirm injected dependency identity through the registered provider's public spell_id lookup.
- Include a plain Optional[object] = None control to isolate DI classification while keeping explicit typing.
- Keep caches and passive recording off and release owned frames/roots deterministically.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Three stale fixtures corrected; 18 reported-file tests pass and thread failure remains unreproduced after ten fresh-process runs.

## Steps
- [x] Inspect component orientation, existing Optional tests and classification/provider selection.
- [x] Write and run the isolated public-API characterization.
- [x] Record exact stage, result/error and identity evidence.
- [x] Convert characterization into CI-discovered default-first regressions and verify the red baseline.
- [x] Implement the default-first runtime correction and existing cache-version invalidation trigger.
- [x] Verify explicit overrides and collection defaults; refresh matching docs and generated assets.

## Validation
- 27 characterization tests passed in 0.49 seconds; scoped Ruff correctness checks pass.
- Desired-contract regressions: 20 expected failures, 20 passes, zero errors/skips in 1.73 seconds.
- Every failure matches default precedence or PLAIN classification; preservation controls pass.
- Final focused suite: 160 passed in 0.90 seconds, including 52 default/override regression cases.
- Scoped Ruff correctness, source asset checks, all three repository corpus proofs and indexes pass.
- Full repository runtime suite and coverage were not run.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/optional_dependency_resolution_20260913/
  - system_docs/patches/active/default_precedence_2026_09_13/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain test evidence at owner-approved closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-13T14:45:34Z
  TYPE: FACT
  CLAIM: The existing integration test proves Optional[IEngine] = None is classified as
    SINGLE_BY_ANNOTATION with is_optional=True, but does not run that consumer through meld.
    The current Phase-3 single-annotation resolver raises when no candidate exists, without
    branching on the optional flag. Registration and missing-provider outcomes need runtime proof.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py:139-144
  - tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py:389-400
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1087-1255
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:434-497
  IMPACT: Do not assume the Python None default wins or that absent optional providers are accepted.
  NEXT: Build real end-to-end cases and capture the actual stage that succeeds or refuses.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T14:45:34Z
  TYPE: FACT
  CLAIM: The phase-3 resolver matches a concrete annotation against the bound class identity,
    even with binding_name/spellframe qualifiers. Single annotation lookup supplies no binding
    filter. A zero-match error is unconditional. Added 15 real-API cases across the three
    lifecycle modes, plus a plain Optional[object] control and provider identity/liveness checks.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-255
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:434-497
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1257-1306
  - tests/experimentation/test_optional_dependency_default_resolution_experiment.py
  IMPACT: Annotation DI may resolve a provider that the earlier unqualified public meld lookup
    cannot address. Test that distinction and characterize missing-provider refusal without a runtime fix.
  NEXT: Execute the experiment and capture results or unexpected failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T14:53:00Z
  TYPE: DECISION
  CLAIM: Owner now asks to understand the Optional/None issue and then patch it. Clarification
    is pending on whether a matching provider should still be injected with None as the absent
    fallback, or whether None should always win without explicit injection. Diagnose independently
    while awaiting that behavior choice. The first test attempt failed on an incorrect liveness
    probe keyword: has_live_creation accepts spell=SHA, whereas meld accepts spell_id=SHA.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/probe_setup_failure.log
  - src/melder/aether/conduit/conduit.py:4187-4250
  - Owner's diagnosis-before-patch instruction and pending semantic clarification in this conversation.
  IMPACT: Corrected only the test probe. Runtime patching is authorized after diagnosis and
    confirmation of intended semantics; required patch artifacts must precede runtime edits.
  NEXT: Run the corrected characterization and trace missing-provider fallback through later compiler phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T14:54:30Z
  TYPE: MEASURE
  CLAIM: Six registered-provider cases pass before and during dynamic prebind. Dynamic postbind
    successfully injects Something into the optional constructor too, but the subsequent direct
    meld of that provider hits a separate missing spell_codegen_creation error. The consumer
    creation itself succeeded; the failing step was the identity assertion's second root meld.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/late_provider_root_failure.log
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:105-126
  IMPACT: Record the late-bound provider-root readiness gap separately. Use the public reuse-only
    query to compare injected identity, avoiding unrelated root compilation in the Optional test.
    The final report must retain this finding; no production fix has been made.
  NEXT: Finish registered/missing/default characterization using meld_existing_spell for identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T14:56:44Z
  TYPE: MEASURE
  CLAIM: Corrected characterization passes all 15 tests in 0.41 seconds. Every registered
    provider variant injects Something despite the None default. Missing provider refuses in
    Phase 3: PhaseExecutionError at conjure for prebind, RuntimeError at consumer bind for
    postbind. Plain Optional[object] remains None and does not construct the registered provider.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/results.log:1-18
  - artifacts/optional_dependency_resolution_20260913/results.xml
  - tests/experimentation/test_optional_dependency_default_resolution_experiment.py:122-179
  IMPACT: Missing-provider fallback is not honored although optional metadata is preserved
    through phases 1-2. The registered-provider precedence decision remains pending with owner.
    The reuse-only API takes spell=SHA; corrected that second probe-call mismatch as well.
  NEXT: Trace empty optional sockets through validation/analyzer/codegen before finalizing the patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:01:31Z
  TYPE: DECISION
  CLAIM: Owner asks to discuss and test a broader default-first rule: honor an ordinary selected
    default even when an injectable provider is registered, unless injection is explicitly requested.
    Extend characterization to numeric/falsy/scalar defaults, a non-None class-instance default,
    and an explicit SpellMap control. Do not assume all defaults are broken: the builtin object
    optional/default control already retained None.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/results.log:13-17
  - Owner's default-precedence preference and request for numeric tests in this conversation.
  IMPACT: Owner resolves the intended precedence toward honoring explicit defaults and requests
    discussion/testing before the patch. Previous inject-if-present behavior is current behavior,
    not the proposed corrected contract. Runtime code remains unchanged during this characterization.
  NEXT: Run the broader default-value matrix and identify the precise patch boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:06:45Z
  TYPE: MEASURE
  CLAIM: Expanded matrix passes 27 characterization cases in 0.49 seconds. Numeric 42/0/1.5,
    False, strings including empty, tuple and builtin Optional defaults are preserved. A user-class
    None default or selected instance default is replaced when a provider exists and causes Phase-3
    refusal when none exists. Explicit SpellMap remains an injection request. All three lifecycle
    modes agree; scoped Ruff passes and no runtime source file changed.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/default_matrix.xml
  - artifacts/optional_dependency_resolution_20260913/default_matrix.log
  - artifacts/optional_dependency_resolution_20260913/default_precedence_findings.md
  IMPACT: The default-first patch belongs in Phase-1 _classify_parameter precedence, using
    has_default rather than default-value truthiness. Merely relaxing Phase 3's missing-provider
    branch would still override selected defaults when a provider exists. Existing explicit DI
    descriptors and required-DI behavior need preserving; older melc plans need invalidation.
    Current tests characterize defects and must become corrected-contract regressions when patched.
  NEXT: Discuss the default-first classification and cache-compatibility change with the owner,
    then stage the runtime patch and required regression/patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:24:05Z
  TYPE: DECISION
  CLAIM: Owner explicitly requests failing regressions first, before the runtime fix. Promote
    the default experiment into tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py,
    replace bug-characterization expectations with default-first expectations, and add guards for
    required DI, nullable annotations without defaults and explicit SpellMap/SpellContract requests.
    Keep the prior experiment path as a thin entry point to the same authoritative tests.
  EVIDENCE:
  - .github/scripts/run_runtime_tests.py:34-41
  - tests/experimentation/test_optional_dependency_default_resolution_experiment.py:1-274
  - Owner's red-regression-first instruction in this conversation.
  IMPACT: Runtime CI includes the integration tier. No expected-failure or skip markers will hide
    the defect. Preserve the pre-regression experiment as historical evidence; production code remains unchanged.
  NEXT: Write the corrected-contract tests, execute them, and verify failures arise from the intended bug.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:25:19Z
  TYPE: FACT
  CLAIM: Canonical integration regressions now require preserving None and selected-instance
    defaults with/without providers. They assert unused providers remain uncreated, require PLAIN
    classification for ordinary defaults, and guard required/nullable-without-default DI, missing
    required providers, explicit SpellMap/SpellContract classification, and scalar defaults.
    The original experiment imports the same tests; historical characterization was archived.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py
  - tests/experimentation/test_optional_dependency_default_resolution_experiment.py
  - artifacts/optional_dependency_resolution_20260913/default_characterization_before_regressions.py
  IMPACT: No contradictory old-behavior tests remain active. Runtime code has not been modified.
  NEXT: Execute the integration file and inspect each failure category; then verify collection and lint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:26:50Z
  TYPE: MEASURE
  CLAIM: Canonical integration run collected 40 cases and produced 20 expected failures plus
    20 passes in 1.73 seconds. Failures cover ignored None/instance defaults, missing-provider
    refusal despite defaults, and SINGLE_BY_ANNOTATION instead of PLAIN. Required DI, scalar
    defaults and explicit descriptor controls pass. No runtime fix or skip/xfail markers were added.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/red_regressions.xml
  - artifacts/optional_dependency_resolution_20260913/red_regressions.log
  IMPACT: The owner-requested red baseline is established in the CI integration tier.
  NEXT: Verify all failure categories, legacy entry-point collection and scoped lint, then document handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:29:05Z
  TYPE: MEASURE
  CLAIM: Final red baseline verified: 40 integration cases, 20 failures, 20 passes, zero errors
    and zero skips. Failure groups are None/provider (9), None/no-provider (3), selected instance/
    provider (3), selected instance/no-provider (3), and PLAIN classification (2). Required DI,
    nullable-without-default DI, missing-required rejection, scalar defaults and explicit descriptor
    controls pass. Both files lint clean; legacy entry point collects all 40 tests.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/red_regression_status.md
  - artifacts/optional_dependency_resolution_20260913/red_regressions.xml
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py:197-349
  IMPACT: The requested tests-first deliverable is complete; the runtime is deliberately unchanged
    and CI will remain red on these cases until the implementation follows. No xfail hides the bug.
  NEXT: Build the scoped default-first classifier/cache-compatibility patch against this red baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T15:45:31Z
  TYPE: DECISION
  CLAIM: Owner resumes the original default-precedence fix. Descriptor optional/default bans
    and the proposed three-fix epic are paused; preserve current SpellMap/SpellContract semantics.
    Full SpellRequirementsFinder source read confirms one early has_default -> PLAIN branch after
    descriptor handling is sufficient to stop inferred edges at their source. Advance the existing
    cache version to reject older plans built with the same bind SHA but different semantics.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1-1306
  - src/melder/utilities/caching_system/caching_system.py:92-126
  - artifacts/optional_dependency_resolution_20260913/red_regression_status.md
  - Owner's instruction to proceed with the original issue in this conversation.
  IMPACT: Scope is classifier, cache compatibility, affected regressions/docs and generated context.
    No new optionality prohibition or unrelated late-provider-root repair is included.
  NEXT: Stage/read patch contracts, then implement and run the red regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:46:37Z
  TYPE: PLAN
  CLAIM: Patch contracts were created, linked and read in architecture -> components -> code
    order. Mapping: requirements precedence -> _classify_parameter early has_default branch ->
    40 integration regressions and requirements suites; cache semantics -> CACHE_VERSION_HISTORY
    entry 8 -> old-version rejection/new-cache replay. Authored context and graph follow validation.
  EVIDENCE:
  - system_docs/patches/active/default_precedence_2026_09_13/architecture_patch.md:8-34
  - system_docs/patches/active/default_precedence_2026_09_13/component_patch_requirements.md:3-25
  - system_docs/patches/active/default_precedence_2026_09_13/component_patch_caching.md:3-20
  - system_docs/patches/active/default_precedence_2026_09_13/code_description_patch_precedence.md:3-20
  IMPACT: Implementation stays within the owner-approved original fix; descriptor strictness proposals remain deferred.
  NEXT: Apply the classifier/cache changes and run the existing red suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T15:47:50Z
  TYPE: MEASURE
  CLAIM: Implemented the early ordinary-default PLAIN branch after existing descriptor handling
    and cache version 8. The established 40-case red regression suite now passes completely in
    0.64 seconds, including all twenty formerly failing cases and all twenty preservation controls.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1088-1220
  - src/melder/utilities/caching_system/caching_system.py:92-130
  - artifacts/optional_dependency_resolution_20260913/green_regressions.xml
  - artifacts/optional_dependency_resolution_20260913/green_regressions.log
  IMPACT: The original default-precedence defect is fixed in the tested modes. Continue with
    compatibility/default-shape tests and documentation before handoff.
  NEXT: Run existing requirements, DI-shape and caching suites to identify affected expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T16:00:00Z
  TYPE: MEASURE
  CLAIM: Related requirements/DI-shape/cache suites return 148 passes and two failures. Both failures
    assert the retired SINGLE classification for Optional[user-class] = None; required nullable
    annotations without defaults remain unchanged. The cache tests also modify four tracked legacy
    JSON fixtures; restore only that generated test churn after validation.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/related_initial.log:1-26
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/test_spell_requirements_finder.py:555-635
  - tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py:389-400
  IMPACT: Update the two expectations and prove real marshal bundle rejection plus new cache replay.
    Existing legacy bundle.json tests alone do not establish the current .melc compatibility contract.
  NEXT: Update the stale expectations and add cache/default-preservation regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

### Prior Handoff Snapshot
Original fix is implemented: ordinary defaults classify PLAIN after descriptor handling; cache version
is 8. All 40 default-precedence regressions pass. Related checks return 148 passes and two stale
Optional/default SINGLE expectations to update. Next: verify real version-7 .melc rejection and cold/
warm default preservation, then refresh authored docs and generated assets. Descriptor restrictions
and the separate late-bound provider-root issue remain outside scope. See linked patch contracts.

- DATETIME: 2026-09-13T16:04:00Z
  TYPE: FACT
  CLAIM: Updated two retired SINGLE expectations and added collection-default identity cases plus
    a cold/warm .melc replay matrix with default liveness and required/SpellMap controls. Found an
    existing real marshal schema-history integration test; extend it to version 8 rather than
    duplicating that test in the unit file. It directly proves version-7 rejection.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:1-75
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py:323-387
  - src/melder/utilities/caching_system/caching_system.py:480-543
  IMPACT: Cache validation targets the production format and verifies actual preload behavior.
  NEXT: Run the combined requirements, DI-shape, defaults and cache suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:07:15Z
  TYPE: DECISION
  CLAIM: Owner stopped the expanded cache work and directed a return to the architecture/components
    contract. Read the binding, spellbook and Meld slices, then verified their fingerprint/cache
    seams: changed constructor signatures miss automatically, but this compiler-only fix leaves
    bind SHA inputs unchanged. Keep the version-8 trigger of existing invalidation; remove the
    new cache replay tests and their harness configuration. No new cache mechanism is introduced.
    The extra combined run hit Windows temp-directory access errors; it is not a passing result.
  EVIDENCE:
  - system_docs/src_components.md:499-615
  - src/melder/aether/spellbook/bind/bind.py:572-670
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-488
  - src/melder/utilities/caching_system/caching_system.py:500-543
  - artifacts/optional_dependency_resolution_20260913/compatibility.log:1-79
  IMPACT: Return to default-precedence regressions and minimal matching documentation.
  NEXT: Run the focused default/requirements/DI-shape checks after removing cache test scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:09:11Z
  TYPE: MEASURE
  CLAIM: Focused default/requirements/DI-shape validation passes all 154 cases in 0.95 seconds.
    The final scope includes 46 default regressions (six collection cases added); no cache replay
    test remains. Existing version-history expected data is advanced with the semantic version.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/focused_final.log:1-4
  - artifacts/optional_dependency_resolution_20260913/focused_final.xml
  IMPACT: Functional fix and preservation controls pass. Keep documentation edits to the selected
    precedence invariant and classifier entry; no architecture/cache redesign or corpus audit.
  NEXT: Add matching default-precedence documentation and refresh affected generated metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:13:02Z
  TYPE: DECISION
  CLAIM: Owner confirmed the PLAIN/explicit-override split and instructed continuation. Added six
    default override cases across automatic prebind, dynamic prebind and dynamic postbind; each
    requires the supplied instance and no unused provider construction. Restored unrelated graph
    regeneration drift and generated fixture churn; only the two affected descriptors are retained.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py
  - Owner's keep-going clarification in this conversation.
  IMPACT: Preserve explicit meld control while correcting inferred DI precedence.
  NEXT: Verify the six override cases with the focused suite and finish generated metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:15:40Z
  TYPE: MEASURE
  CLAIM: Final focused suite passes 160 cases in 0.90 seconds, including all six explicit override
    cases. PLAIN preserves None/instance/collection defaults; explicit overrides replace them without
    constructing the registered provider. Existing descriptor and required-DI controls remain green.
    Source asset checks, all three repository corpus proofs, paired indexes and scoped Ruff pass.
    Documentation preservation comparison reports only the intentional Updated-date replacement.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/default_override_final.log:1-4
  - artifacts/optional_dependency_resolution_20260913/default_override_final.xml
  - artifacts/optional_dependency_resolution_20260913/source_assets.log:1-3
  - artifacts/optional_dependency_resolution_20260913/repo_assets.log:1-4
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py
  - docs/intermediate/registration.md:19-27
  IMPACT: Original fix is ready for review. Cache behavior is unchanged except the version trigger;
    extra cache replay tests were removed. Unrelated generated descriptor and fixture churn was restored.
    The broader suite/coverage and known late-provider-root issue remain outside the completed checks.
  NEXT: Owner reviews the default-precedence change; close the ticket only after acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-13T16:21:09Z
  TYPE: FACT
  CLAIM: Owner reports three component failures consistent with the accepted ordinary-default
    rule: symbolic shape still expects SINGLE, topology expects a provider edge for config=None,
    and a broadcast fixture expects child=None to be injected. The separate cross-thread
    SpellSpace failure only reports aggregated failure booleans; its cause remains UNKNOWN.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:80-180
  - tests/component/melder/spellbook/spell_crafter/topology/test_spellbook_component_spell_local_topology.py:70-151
  - tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py:455-537
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:131-157
  - Owner-provided failure traces in this conversation.
  IMPACT: Reopen the same default-precedence lane. Update expectations/fixtures without reverting
    the default rule; do not assume the fourth failure is related or change concurrency semantics.
  NEXT: Read the four test files, correct default-dependent fixtures, and reproduce the thread outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:22:39Z
  TYPE: MEASURE
  CLAIM: Full reads confirm the first three failures are outdated default assumptions. The
    broadcast test needs a required child dependency to continue testing two real contract sockets.
    The thread probe has a zero-argument constructor and all three tests pass unchanged in isolation
    (0.34 seconds), so its reported failure is not explained by ordinary-default classification.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:80-180
  - tests/component/melder/spellbook/spell_crafter/topology/test_spellbook_component_spell_local_topology.py:70-153
  - tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py:455-537
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:29-40
  - artifacts/optional_dependency_resolution_20260913/thread_followup_initial.log:1-2
  IMPACT: Update only the stale expectations and required-child fixture. Preserve thread assertions;
    improve exception diagnostics and test alongside the reported component files before concluding.
  NEXT: Apply those test corrections and rerun all four reported files together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:23:38Z
  TYPE: MEASURE
  CLAIM: All four reported files pass together: 18 tests in 0.73 seconds. Corrected the symbolic
    PLAIN expectation and empty topology targets; the broadcast fixture now requires its child.
    Thread assertions remain unchanged in meaning, with full worker tracebacks attached on failure.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/reported_files_final.log:1-2
  - artifacts/optional_dependency_resolution_20260913/reported_files_final.xml
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:95-241
  IMPACT: Three stale component fixtures are corrected; the owner's thread failure remains unreproduced.
  NEXT: Run a bounded repeated thread reproduction and refresh generated test bundles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:25:07Z
  TYPE: MEASURE
  CLAIM: Ten additional fresh-process runs of the unchanged thread behavior all pass: 30 tests.
    Combined reported-file validation remains 18 passing cases. The fourth failure's root cause
    remains UNKNOWN; worker tracebacks now survive aggregation if it recurs. No concurrency
    assertion was weakened and no production runtime code changed during this follow-up.
    Both build runners regenerated successfully and both checks pass against current v0.2.40;
    src/tests/other corpus proofs, scoped Ruff correctness and diff whitespace checks pass.
  EVIDENCE:
  - artifacts/optional_dependency_resolution_20260913/thread_followup_repeated.log:1-40
  - artifacts/optional_dependency_resolution_20260913/reported_files_final.log:1-2
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:132-241
  - tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py:479-500
  IMPACT: The first three reported failures are resolved as fixture/expectation drift. The thread
    failure cannot honestly be called fixed; its next occurrence will expose the underlying exception.
  NEXT: Owner reviews/retries the broader suite; investigate the recorded worker traceback if it recurs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Default-first runtime remains verified (160 focused tests in the prior pass). Follow-up corrects
three owner-reported component fixtures: symbolic default shape PLAIN, no default-provider topology
edge, and required nested child for broadcast-contract traversal. All four reported files pass
18 cases together; the thread experiment also passes ten fresh-process runs (30 tests). Its original
failure remains unreproduced, so only traceback diagnostics changed there. Both build runners and
checks are refreshed against current v0.2.40. Review pending; no concurrency repair or source changes
were made during this test-fixture follow-up.