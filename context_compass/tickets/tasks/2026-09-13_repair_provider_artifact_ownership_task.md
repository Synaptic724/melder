# Task: Reproduce and repair provider artifact ownership

## Metadata
- Task ID: TASK-2026-09-13-repair-provider-artifact-ownership
- Story: STORY-2026-09-13-provider-artifact-ownership
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-13T18:52:28Z

## Objective
Keep a provider's canonical executable artifacts alive when a borrower validates its visible graph.

## Ticket Contract
- ENTRY_GATE: linked owner-authorized epic/story, active route and current source trace.
- EXECUTION_BOUNDARY: experiments, regression tests and source reads only until the owner resumes implementation.
- DEPENDENCIES: original CommandOps provider-prefix and linked GraphCache/PolicyEngine acceptance tests.
- EXIT_GATE: native repro turns green; original identity/state/cleanup proofs pass through coordinated verification.
- FAILURE_ESCALATION: do not infer ownership from visibility or repair missing payloads under borrower scope.

## Scope Boundaries
- In scope: native regression, minimal ownership repair, focused documentation and verified package handoff.
- Out of scope: consumer workarounds, Optional/default policy, releases, named conduits and silent environment edits.

## Steps
- [x] Trace current Phase-5 publication and downstream artifact use.
- [x] Reproduce the original validation boundary without extra diagnostic provider melds.
- [x] Compare structural/resolution-only refresh, implicit meld, repeated and two-borrower paths.
- [ ] Write/read the patch contract and implement the minimal owner-scoped correction.
- [ ] Validate repeated/two-borrower behavior and preserve ordinary resolution.
- [ ] Coordinate original GraphCache/PolicyEngine acceptance and refresh generated assets.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: owner-requested experiment tranche and red regressions are complete; production changes paused.

## Validation
Eight characterization cases pass recording provider data/plan/injection outcomes. Thirteen corrected-
contract regressions produce seven expected missing-codegen failures and six passing early-prefix controls.

## Risks / Rollback Notes
Borrower visibility includes the same provider Spell object. Protect canonical ownership rather than
adding borrowed providers to the borrower plan queue. Preserve all unrelated working-tree edits.

## Catch-up Read Map (Required Before Resuming)
Read the latest Notes, then the epic and the original independent-prefix test. Implementation is
paused for owner discussion and experiments. No production source has changed in these repair lanes.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain compact reproduction/validation evidence for owner acceptance.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record ownership questions before patching.

## Notes
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

## Context / Handoff Summary
Production changes paused for discussion. The provider failure is reproduced after validation and
implicit borrower meld. Eight experiment cases show consumer injection identity and retained data
survive while the provider plan is cleared; resolution-only refresh also fails. Thirteen corrected-
contract regressions preserve the original independent-prefix discipline. Full catch-up read map above.
