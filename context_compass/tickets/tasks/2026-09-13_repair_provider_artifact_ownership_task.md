# Task: Reproduce and repair provider artifact ownership

CURRENT OWNER DIRECTION (2026-09-19): provider-artifact repair is active under the current model.
The broader redesign is retired. Earlier dependency/parking statements below are superseded history.
Keep tests asserting provider usability; no xfail or expected-error conversion is authorized.


## Metadata
- Task ID: TASK-2026-09-13-repair-provider-artifact-ownership
- Story: STORY-2026-09-13-provider-artifact-ownership
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-19T13:30:00Z

## Objective
Keep a provider's canonical executable artifacts alive when a borrower validates its visible graph.

## Ticket Contract
- ENTRY_GATE: linked owner-authorized epic/story, active route and current source trace.
- EXECUTION_BOUNDARY: current-model artifact ownership repair, native regressions, relevant docs and build checks.
- DEPENDENCIES: original CommandOps provider-prefix and linked GraphCache/PolicyEngine acceptance tests.
  The previous broader-model prerequisite was withdrawn by the owner on 2026-09-19.
- EXIT_GATE: native repro turns green; original identity/state/cleanup proofs pass through coordinated verification.
- FAILURE_ESCALATION: do not infer ownership from visibility or repair missing payloads under borrower scope.

## Scope Boundaries
- In scope: native regressions, repair under the selected ownership model, documentation and verified package handoff.
- Out of scope: consumer workarounds, Optional/default policy, releases, named conduits and silent environment edits.

## Steps
- [x] Trace current Phase-5 publication and downstream artifact use.
- [x] Reproduce the original validation boundary without extra diagnostic provider melds.
- [x] Compare structural/resolution-only refresh, implicit meld, repeated and two-borrower paths.
- [x] Implement the selected current-model publication correction; broader redesign retired.
- [x] Validate repeated/two-borrower and same-book local behavior; preserve ordinary resolution.
- [x] Run all nine unchanged original GraphCache/PolicyEngine checks and refresh generated assets.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: native artifact regressions and nine original CommandOps cases pass; docs and assets verify.

## Validation
Current repair: 29 focused checks pass. Extended selection has 935 ordinary passes plus eight cache
cases passing separately after sandbox ACL setup failures; its 2 skips, 3 xfails and 1 non-strict xpass
come from unchanged tests. All nine original CommandOps provider tests pass. Source/index/graph/build-bundle
checks pass. See repair_result_20260919.md. Full repository suite and coverage: Not run.

## Risks / Rollback Notes
Borrower visibility includes the same provider Spell object. Protect canonical ownership rather than
adding borrowed providers to the borrower plan queue. Preserve all unrelated working-tree edits.

## Catch-up Read Map (Required Before Resuming)
Read the latest Notes and repair_result_20260919.md first. Implementation is delivered for review.
The source map below records the original diagnosis; remeasure ranges against the patched Phase-5 source.

Orientation (verify indexes before slicing):
- system_docs/src_architecture.md: Bind/Conjure/Meld sequences, ownership and cleanup invariants.
- system_docs/src_components_index.md -> SpellCompiler and Validation Pipeline; SpellCompiler Phase
  Artifacts; ConduitWard and Contracts; Meld Resolution Runtime; Change-Control Revalidation.
- system_docs/src_graph_index.md -> the source-file sections below; source stamps are partly stale,
  so read current source before making behavioral claims.

Ownership and invalidation chain:
- src/melder/aether/spellbook/spellbook.py: contracted registration around 1251-1307, scoped resolution
  orchestration around 6594-6766. Read whole methods; these are shared provider Spell references.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py: all 693 lines read;
  _attach_phase5_artifacts_for_snapshot, both setter helpers, run_frame_wide and run_local.
  Visible snapshots include borrowed providers; attachment currently invalidates all visible Spells.
- src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py: all 398 lines read;
  _cleanup_codegen_outputs and structural-versus-planning cleanup boundaries.
- src/melder/aether/spellbook/spellbook_creation_system.py: phase_root_blueprints_factory (2837-2877),
  phase_plan_group_factory (3084-3156), _run_target_foundational_resolution_phases and
  _collect_target_resolution_scope (2134-2230). Frame lead and plan roots are local owned Spells.
- src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:
  run_phase_root_blueprints and run_phase_root_blueprints_local (254-335), plus run_all_phases.
- src/melder/aether/spellbook/spell.py: _cleanup_creation_context and _get_or_build_creation_context;
  context-door epoch reset versus ready flags.
- src/melder/aether/conduit/meld/conduit_meld.py: meld readiness and context acquisition.
- src/melder/aether/conduit/meld/meld.py: _ensure_lineage_resolvable, _gated_validation_required
  and scoped resolution readiness (recheck ranges from the original consultation).
- src/melder/aether/conduit/meld/creation_context/creation_context_factory.py: get_or_build_for_spell.
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py: build requires Phase-11
  output for constructed spells, but existing-object executors return the supplied object directly.

Native tests / fixtures:
- tests/integration/melder/spellbook/test_provider_artifact_ownership.py: new independent-prefix,
  repeated-validation and two-borrower regressions. Each borrower now uses a distinct binding name.
- tests/experimentation/test_borrower_provider_validation_experiment.py: eight characterization cases.
- artifacts/provider_artifact_ownership_20260913/experiment_findings.md: result matrix and proof limits.
- artifacts/provider_artifact_ownership_20260913/experiment_observations.json: passive plan observations
  versus retained data, consumer injection identity and the single final provider lookup.
- tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py: first 500 of 753 lines
  read; finish the remaining lines before editing. Frame-wide builder/publication stubs and expectations.
- tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py: all 437 lines read;
  direct attachment helper call plus scoped-local expectations.
- tests/component/melder/spellbook/spell_crafter/phases/test_spellbook_component_spell_crafter_phase5.py
- tests/component/melder/spellbook/test_spell_compiler_component_system.py
- artifacts/provider_artifact_ownership_20260913/red_native.log: six prefixes pass, then the exact
  missing spell_codegen_creation error; initial two-borrower fixture collision is recorded separately.

Original real-provider acceptance and consultation:
- ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
- ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_provider_invalidation_boundary_task.md
- ../../priv_commandops/tests/component/spectrum/test_linked_commandops_providers.py: all 168 lines read;
  preserve the eight fresh-world prefixes and full GraphCache/PolicyEngine state/cleanup assertions.
- ../../priv_commandops/tests/component/spectrum/conftest.py (fresh world for each test).
- ../../priv_commandops/context_compass/artifacts/2026-09-13_provider_invalidation_boundary/prefix_results_0240.log

Experiment questions before choosing a repair:
- Test refresh_structural=False independently; it has NOT been established as a workaround.
- Compare explicit validation with direct borrower meld, and one/repeated/two-borrower cycles.
- Record retained object data separately from compiled-artifact availability and provider remeld.
- Never insert intermediate provider melds that can change the tested prefix.
- Publication limited to owned Spells is a candidate repair, not an implemented or accepted final design.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/provider_artifact_ownership_20260913/
  - artifacts/provider_artifact_ownership_20260913/repair_result_20260919.md
  - system_docs/patches/active/provider_artifact_ownership_2026_09_19/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain compact reproduction/validation evidence for owner acceptance.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record ownership questions before patching.

## Notes
- DATETIME: 2026-09-19T12:51:19Z
  TYPE: DECISION
  CLAIM: Owner retires the broader redesign and explicitly chooses to fix this artifact bug next.
    This supersedes the September 17 redesign dependency. Retain the current existing-object model
    and all corrected-behavior assertions; do not mark the seven native failures xfail.
  EVIDENCE:
  - Owner reply: Retire the broader redesign; fix the artifact bug next (Recommended).
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:71-216
  IMPACT: Source investigation, bounded compiler repair, tests/docs/build checks are authorized.
    Native scope is provider-owned artifact publication versus borrower visibility, not object redesign.
  NEXT: Re-read the Phase-5 publication/invalidation chain, then stage the bounded patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:14:07Z
  TYPE: FACT
  CLAIM: Current CompilerPhase5 matches the consultation SHA256
    e820efc40b990ae1ca3abb0442949c90034e4fe950628ad5039019de5e53c70d.
    Original provider tests and reset fixture were read completely; preserve their eight independent
    prefixes and full identity/state/cleanup proof. Source version is still 0.2.40.
  EVIDENCE:
  - ../../priv_commandops/tests/component/spectrum/test_linked_commandops_providers.py:1-168
  - ../../priv_commandops/tests/component/spectrum/conftest.py:1-60
  - ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
  IMPACT: Use a native regression alongside unchanged real-provider downstream acceptance.
  NEXT: Read Phase 5 and the artifact publication consumers, then build the native reproduction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-13T18:18:05Z
  TYPE: FACT
  CLAIM: Full Phase-5 and artifact reads confirm that both scoped entry paths attach to every
    visible snapshot Spell, and setters clear codegen/context. The frame-wide lead and plan-group
    queue use local owned Spells. The same shared provider is therefore invalidated outside the
    owner's compile queue. Snapshot visibility must remain broad; publication authority must narrow.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-372
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:501-693
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:365-398
  - src/melder/aether/spellbook/spellbook_creation_system.py:2837-2877
  - src/melder/aether/spellbook/spellbook_creation_system.py:3084-3156
  IMPACT: The graph document's source stamps are partly stale, so current source governs this design.
    Native minimal contract tests will complement, never replace, the original real GraphCache acceptance.
  NEXT: Add native independent-prefix, repeated-validation and two-borrower reproductions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:19:17Z
  TYPE: MEASURE
  CLAIM: Native independent prefixes reproduce the exact boundary: six earlier prefixes pass,
    provider meld fails after validation with missing spell_codegen_creation. Consumer-meld and
    repeated single-borrower cases fail with the same payload error. The two-borrower case initially
    hit a fixture binding-ID collision; give each consumer a distinct binding name in the shared frame.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/red_native.log
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:137-197
  IMPACT: Four native failures corroborate the original mechanism. The fifth is setup drift, not
    evidence for an additional production defect; correct it before evaluating the repair.
  NEXT: Fix the distinct-consumer test identity, then stage the original ownership-preservation patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:37:44Z
  TYPE: MEASURE
  CLAIM: Eight characterization cases pass recording one/two borrowers, repeated validation with
    structural refresh enabled/disabled, and direct consumer meld. Consumer injection retains the
    exact original provider and data survives borrower cleanup. Both validation modes and implicit
    meld clear provider codegen, so the sole final provider lookup fails. Late-bind-only controls pass.
    Corrected-contract regressions: seven expected failures and six early-prefix controls pass.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/experiments_final.log
  - artifacts/provider_artifact_ownership_20260913/experiment_findings.md
  - artifacts/provider_artifact_ownership_20260913/regressions_discussion_final.xml
  IMPACT: refresh_structural=False is not a bypass; implicit local compilation is also affected.
    No production source changes. Existing/provider tasks now carry full catch-up maps and proof limits.
    Both suites together have 23 regression cases: 14 intentional failures, nine passes, zero setup errors.
    Scoped Ruff and generated-test-bundle proof pass; source build assets are current and unchanged.
  NEXT: Discuss the ownership/invalidation results with the owner before selecting the repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T18:50:19Z
  TYPE: FACT
  CLAIM: Reread the relevant component ownership and revalidation sections after compaction.
    They distinguish shared-lifetime creation storage, Spell-owned compiled artifacts and
    conduit-scoped dirty-root tracking. The experiment records surviving object identity/data
    separately from the missing provider codegen payload; no disposal failure was demonstrated.
  EVIDENCE:
  - system_docs/src_components.md:2057-2846
  - system_docs/src_components.md:4127-4189
  - system_docs/src_components.md:4710-4753
  - system_docs/src_components.md:4825-4892
  - artifacts/provider_artifact_ownership_20260913/experiment_findings.md:1-32
  IMPACT: Ownership of a live object and ownership of its compiled plan are separate obligations.
    Do not reinterpret the missing-plan symptom as evidence that borrower cleanup destroyed the object.
  NEXT: Reopen the Phase-5 attachment setters and owner-only planning queue before discussing repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:52:28Z
  TYPE: FACT
  CLAIM: Current source reread confirms that contracted registration retains the same Spell in
    the borrower pool. Both Phase-5 entrypoints publish through the snapshot attachment helper;
    its setters clear codegen and the creation context for every participating Spell. The fused
    planning queue instead draws from the borrower's owned _spells. The publication/rebuild
    scope mismatch remains present. The source working tree has no changes from this discussion.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1251-1307
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-214
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:311-368
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:460-693
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:365-398
  - src/melder/aether/spellbook/spellbook_creation_system.py:3084-3156
  IMPACT: The source agrees with the recorded missing-plan failure; object disposal remains a
    distinct contract. Repair discussion should preserve provider ownership and consumer visibility.
  NEXT: Discuss owner-scoped artifact publication alongside the existing-instance iterator correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:28:39Z
  TYPE: MEASURE
  CLAIM: Annotation-only regressions exposed the missing-codegen symptom after same-book late
    binding too: consumer injection succeeds, then a subsequent root.meld(provider_id) cannot
    build CreationContext. The annotation lane now checks injected identity through the public
    reuse-only door; its original failing log preserves this provider-remeld observation here.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_patch_final.log:4-64
  - tests/integration/melder/spellbook/test_deferred_annotations.py
  IMPACT: Extend future ownership investigation to local target compilation, not only borrowers.
    This lane stays parked under the owner's annotation-only instruction; no ownership fix made.
  NEXT: Reproduce the same-book local publication boundary when the owner resumes this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T01:07:11Z
  TYPE: DECISION
  CLAIM: Owner places this repair under the broader existing-object ownership program and rejects
    its presentation as an independent weekend correctness target. Preserve reproductions and
    qualification criteria, but do not select or implement an isolated ownership patch.
  EVIDENCE:
  - Owner's explicit dependency direction in this conversation.
  - tickets/epics/completed/2026-09-13_existing_object_lifecycle_ownership_epic.md
  IMPACT: Implementation waits for the ownership contracts and required model changes from that epic.
    This records project sequencing, not new source proof that all redesign features are technically necessary.
  NEXT: Resume through the owned-object design program, then revalidate the artifact failure under its model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:02:05Z
  TYPE: FACT
  CLAIM: Owner's pasted suite output contains the same seven missing-codegen failures already
    recorded here on September 13: validation/consumer-meld prefixes, three repeated-borrower cases
    and two explicit/implicit compilation cases. Read the entire supplied output and native test module.
    The fixture binds the RetainedProvider CLASS with unique existence, then obtains its instance by
    meld. These tests do not assume the proposed external-object registration or lifetime redesign.
  EVIDENCE:
  - Owner-supplied Pasted text.txt:1-794 (seven missing spell_codegen_creation failures).
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:68-112
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:134-216
  - artifacts/provider_artifact_ownership_20260913/regressions_discussion_final.xml
  IMPACT: These are retained native corrected-behavior regressions for the deferred artifact ownership
    repair, not stale Protocol expectations or hypothetical future-API tests. The error establishes
    unavailable executable artifacts; it does not by itself establish destruction of the live object.
    This is inspection of owner output and existing evidence, not a fresh test run or runtime repair.
  NEXT: Explain the test contract and preserve the owner's ownership-program sequencing decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:48:07Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner favors retaining the current unique-only supplied-object model and conditionally
    proposes retiring the broader epic and making the ownership tests expected failures. Verified the
    new attachment is byte-identical to the previously read seven-failure report (SHA256
    970b9ccd0094f5e8905446fdd8e3fa4ad36044cb99cb26ab2dbf449c26f66a29).
    Explained that these tests use a class-created unique provider and still expose an independent
    artifact-availability defect. Asked whether to retain the model and fix that defect next, or defer
    the known bug with strict xfails while retiring the expansion proposal.
  EVIDENCE:
  - Owner's current conditional retirement/expected-failure request.
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:71-112
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:134-216
  - The two owner attachments have identical SHA256 and 794 lines.
  IMPACT: No epic deletion/archive or test-expectation change is made from the mistaken inference
    that unique-only semantics make these provider failures correct. Pending clarification concerns
    bug priority and deferral, not permission to retain the already-supported unique-only model.
  NEXT: Apply the owner's selected bug disposition and preserve the completed repair/history links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:54:21Z
  TYPE: FACT
  CLAIM: Current Phase 5 attaches destructive setters to every visible snapshot Spell. Both setters
    clear the Spell's codegen and creation context. Conduit-wide planning rebuilds owned-local Spells;
    target-local planning rebuilds only its target. Therefore filtering only by book ownership would
    still invalidate same-book dependency artifacts during local compilation.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-368
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:460-693
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:365-398
  - src/melder/aether/spellbook/spellbook_creation_system.py:2134-2291
  - src/melder/aether/spellbook/spellbook_creation_system.py:3084-3156
  IMPACT: Preserve full dependency visibility but explicitly limit canonical publication to the pass's
    compilation targets: owned spells for conduit-wide runs, the selected spell for local runs.
    Do not add borrowed providers to the borrower compilation queue or change live-object semantics.
  NEXT: Stage patch contracts, reproduce the retained failures and add a same-book local regression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:56:12Z
  TYPE: MEASURE
  CLAIM: Fresh unchanged native suite reproduces all seven owner-reported missing-codegen failures;
    six early prefixes pass. The broader redesign and three discovery tickets are retired with findings
    retained, not marked implemented. A text-encoding failure during path redirects was recovered by
    byte-preserving replacements; archive destinations and routing were verified.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_red.log
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_red.xml
  - tickets/epics/completed/2026-09-13_existing_object_lifecycle_ownership_epic.md
  IMPACT: Current repair has an exact native baseline and no redesign dependency. The original
    corrected-behavior assertions remain authoritative and will not be converted to xfail.
  NEXT: Consume the new patch contracts and implement explicit Phase-5 publication targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:57:19Z
  TYPE: DECISION
  CLAIM: Required patch contracts are authored, linked and consumed in order. Mapping: architecture
    visibility/publication invariant -> explicit helper publication IDs -> unchanged native borrower
    tests; local rebuild scope -> target-only publication -> same-book late-consumer regression;
    component lifecycle boundary -> preserve excluded artifact references -> frame/local unit controls.
  EVIDENCE:
  - system_docs/patches/active/provider_artifact_ownership_2026_09_19/architecture_patch.md:6-46
  - system_docs/patches/active/provider_artifact_ownership_2026_09_19/component_patch_phase5.md:6-36
  - system_docs/patches/active/provider_artifact_ownership_2026_09_19/code_description_patch_phase5.md:6-31
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:311-368
  - src/melder/aether/spellbook/spellbook_creation_system.py:2229-2291
  IMPACT: Runtime scope is one fully read Phase-5 module; no new public API, owned-object flag or
    provider recompilation fallback. Both Phase-5 unit files and native provider test were read fully.
  NEXT: Add same-book regressions, confirm their baseline, then apply the Phase-5 publication gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T12:58:59Z
  TYPE: FACT
  CLAIM: Added a native same-book late-consumer regression; its corrected single-consumer baseline
    reproduces missing codegen. An initial three-same-class variant hit the existing duplicate-name
    rule and was removed from this focused test. Phase 5 now accepts explicit publication IDs: owned
    book IDs for conduit-wide, selected target only for local. Unit controls preserve excluded artifacts.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/local_single_20260919_red.log
  - artifacts/provider_artifact_ownership_20260913/local_20260919_red.log
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:219-237
  IMPACT: Production correction remains one module and preserves full visible graph construction.
    Existing failure assertions are unchanged. Native acceptance must now verify the repair.
  NEXT: Run the native ownership regressions and Phase-5 unit controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:00:03Z
  TYPE: MEASURE
  CLAIM: Focused production verification passes all 29 cases: fourteen native provider cases including
    all seven previously failing paths plus same-book local compilation, and fifteen Phase-5 unit controls.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_green.log
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_green.xml
  IMPACT: Publication restriction repairs the observed failure without changing existing-object semantics
    or weakening assertions. Broader compiler/contracts and original downstream acceptance remain to check.
  NEXT: Run surrounding native compiler/contract regressions and inspect downstream test availability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:03:05Z
  TYPE: MEASURE
  CLAIM: Surrounding compiler/contract/integration selection reports 935 passed, 2 skipped, 3 existing
    xfails and 1 non-strict xpass; eight cache cases failed sandbox temporary-directory setup. A second
    local temp run also hit Windows directory cleanup permissions. The eight cache tests then pass in
    the approved unsandboxed run. Original unchanged CommandOps provider suite passes all nine cases
    using its .venv314 interpreter and process-local PYTHONPATH to this Melder source; no environment install.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_extended.log
  - artifacts/provider_artifact_ownership_20260913/cache_20260919.log
  - artifacts/provider_artifact_ownership_20260913/commandops_20260919.xml
  - tests/integration/melder/spellbook/test_spellbook_integration_di_validation_faults.py:122-244
  IMPACT: The original GraphCache/PolicyEngine ownership acceptance is now green. This patch added no
    xfail markers. All 943 ordinary native passes are accounted for across the extended/cache runs;
    unrelated pre-existing xfail markers are retained. Docs and generated-asset synchronization remain.
  NEXT: Update compiler publication contracts and graph descriptors, then regenerate/check build assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:08:28Z
  TYPE: MEASURE
  CLAIM: Architecture/components, only the changed Phase-5 descriptor and generated graph/index are
    synchronized. All baseline prose lines survive. All three source asset builders and all repository
    corpus checks pass; a transient index write failure succeeded on retry. Diff/correctness checks pass.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/repair_result_20260919.md
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_assets_check.log
  - artifacts/provider_artifact_ownership_20260913/repair_20260919_bundles_check.log
  - artifacts/provider_artifact_ownership_20260913/commandops_20260919_source.log
  IMPACT: Repair is ready for owner review; the seven original failures and added same-book case pass
    with their intended assertions, not xfails. No release/version/environment change occurred.
  NEXT: Owner reviews and accepts the completed provider-artifact repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:25:41Z
  TYPE: FACT
  CLAIM: Owner's broader component run found a remaining pre-repair assertion in
    test_component_spell_crafter_run_phase_root_blueprints_local_scopes_to_dependency_closure:
    it requires publishing a blueprint onto the dependency. That conflicts with the accepted local
    target-only publication contract. The prior selected run did not include this component file.
  EVIDENCE:
  - Owner's traceback identifies tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1563-1633.
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:612-709
  - system_docs/patches/active/provider_artifact_ownership_2026_09_19/component_patch_phase5.md:10-23
  IMPACT: Reopen the same repair task for a component-test expectation correction, preserving the runtime
    ownership fix. Verify dependency visibility and unchanged pre-existing/absent artifacts explicitly.
  NEXT: Read the component module fully, update this test contract, and run the surrounding component suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:27:24Z
  TYPE: DECISION
  CLAIM: The exact component case reproduces the reported failure. The full 1707-line component module
    was read. Correct its accepted contract by parameterizing absent versus precompiled dependency state:
    keep dependency nodes in the target index, preserve dependency blueprint/index/codegen references,
    and exclude unrelated visible spells. Runtime source and publication behavior stay unchanged.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1563-1637
  - artifacts/provider_artifact_ownership_20260913/component_followup_red.log
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:313-379
  IMPACT: This is an overlooked test expectation, not a reason to restore destructive dependency writes.
  NEXT: Update the component case and run the full Spellbook component selection plus ownership regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:27:50Z
  TYPE: MEASURE
  CLAIM: Corrected component expectations now pass for absent and real compiled provider artifacts.
    The complete reported component module plus native provider-ownership regressions pass 31 cases.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1563-1670
  - artifacts/provider_artifact_ownership_20260913/component_followup_focused.log
  - artifacts/provider_artifact_ownership_20260913/component_followup_focused.xml
  IMPACT: Dependency visibility and preservation are both checked; no runtime change was required.
  NEXT: Run the full Spellbook component tree to catch any other stale expectations from this repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T13:30:00Z
  TYPE: MEASURE
  CLAIM: Full tests/component/melder/spellbook selection passes 491 tests. The reported module and
    native ownership regressions separately pass 31 cases. The revised test verifies both absent and
    real precompiled provider artifacts remain identical while dependency visibility stays intact.
    Test corpus regenerated; all src/tests/other bundle checks and source asset checks pass.
  EVIDENCE:
  - artifacts/provider_artifact_ownership_20260913/component_followup_full.log
  - artifacts/provider_artifact_ownership_20260913/component_followup_full.xml
  - artifacts/provider_artifact_ownership_20260913/component_followup_focused.xml
  - artifacts/provider_artifact_ownership_20260913/component_followup_bundle_check.log
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1563-1664
  IMPACT: The overlooked component expectation is corrected and broader component qualification is green.
    No production changes or xfail markers were needed; full repository-suite coverage is not claimed.
  NEXT: Owner reruns their full suite or accepts this verified component follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
FIXED / REVIEW: stale local Phase-5 component expectation corrected; 491 Spellbook component
tests pass. Test corpus rebuilt and all asset/bundle checks pass. Runtime repair remains implemented: Phase 5 retains full dependency visibility but publishes canonical artifacts only to
owned book targets for conduit-wide passes, or the selected target for local passes. Same-book and
borrowed providers keep their executable state. One production module changed for this bug.
All seven original failures and the added local case pass; 29 focused checks, 943 ordinary native passes
across extended/cache runs, and 9 unchanged CommandOps provider cases. Existing unrelated xfail markers
remain. All relevant docs, graph/indexes, source assets and repository corpora are current.
Broader existing-object redesign and three discovery tickets are retired, with research retained.
The current unique-only supplied-object model and correct-behavior test assertions remain.
Read repair_result_20260919.md for exact evidence and limitations. Acceptance pending; do not restart
redesign discovery or create expected-failure markers for this now-repaired bug.
