# Task: Implement scoped purge through Meld and Creations

## Metadata
- Task ID: TASK-2026-09-20-implement-scoped-creation-purge
- Epic: EPIC-2026-09-19-scope-aware-creation-purge
- Story: none; bounded implementation after completed discovery
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-20T22:06:15Z
- Updated: 2026-09-21T00:13:20Z

## Objective
Implement the approved purge operation with Meld owning selection/scope authority and Creations
owning only removal, locking and disposal. Preserve existing meld execution and scope lifetimes.

Current tranche: implement the accepted instance shortcut and single-instance disposal using the
existing lookup and Creations machinery. Asset, graph and index regeneration remains owner-gated.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorized implementation and reconfirmed the component boundary.
  Discovery plan and the linked scope_aware_purge_2026_09_20 patch contracts are read.
- EXECUTION_BOUNDARY: Creations, Meld, Conduit, SpellSpace; focused tests, related documentation,
  descriptors/indexes and generated assets. No new scope system or unrelated runtime repairs.
- DEPENDENCIES: Discovery task and its plan; established creation writer locks and scope stores.
- EXIT_GATE: Positive/refusal scope matrix and deterministic lock/disposal regressions pass;
  existing scoped behavior remains green; docs/assets describe and expose the API.
- FAILURE_ESCALATION: Record a demonstrated incompatibility before extending scope. Preserve user
  work; do not bypass locks or weaken assertions to complete this feature.

## Owner Decisions
- Meld resolves the actual Spell, determines authority and discovers the target Creations.
- Creations does not discover scope, authorize callers, or accept a new scope-policy payload.
- Use a native Creations.purge(spell); never use extraction/transfer helpers.
- SpellSpace may purge only its own many or unique_per_spell_space entries.
- Conduit-local many and unique_per_conduit remain local; unique requires the Spell owner.
- Lineage requires the lineage root; cluster requires the elected store's leader.
- Mirror creation locks: unique uses Spell._lock then store lock; other modes use store lock.
- Remove live/disposal entries together; dispose after releasing locks; retain definitions/contexts.
- Return removed count, zero when empty; disposal errors aggregate after removal, without rollback.
- ConduitMeld owns conduit policy; SpellSpaceMeld owns space policy; base Meld shares discovery only.
- Both input paths are intentional: instance -> inspected class -> existing lookup, or explicit
  Meld-style selectors. Do not add reverse indexes, metadata recovery or registry scans for discovery.
- purge_all=True retires the selected binding's retained entries. False retires the supplied
  instance in the authorized store; it requires an instance rather than guessing a many entry.
- No public internal-Spell targeting or runtime Spell import is supported.
- Do not regenerate assets, graph or indexes until the owner explicitly approves the source code.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Both input paths and single/all retirement are implemented. All 270 focused
  checks and scoped lint pass; generated products remain held for explicit owner code approval.

## Steps / Checklist
- [x] Confirm the writer-lock mapping and record patch contracts.
- [x] Add meaningful failing regression coverage for stores, locks and public scope authority.
- [x] Implement native Creations purge, concrete Meld doors and both public facades.
- [x] Share existing many disposal mechanics and cover multiple failures across both facades.
- [x] Run focused feature and existing-scope regressions; repair failures within this boundary.
- [ ] Finish documentation/descriptors and regenerate assets only after explicit code approval.
- [x] Record this bounded source delivery and leave the ticket ready for owner review.
- [x] Experiment with instance selectors, named/frame bindings and object identity across scopes.
- [x] Implement inspected-class discovery and single-instance retirement; validate both facades.

## Deliverables
- Public Conduit.purge and SpellSpace.purge using Meld selectors and returning removal counts.
- Native store retirement with correct synchronization/disposal and explicit lifecycle limits.
- Tests and source-backed documentation/build evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/scope_aware_purge_2026_09_20/architecture_patch.md
  - system_docs/patches/active/scope_aware_purge_2026_09_20/component_patch_creations.md
  - system_docs/patches/active/scope_aware_purge_2026_09_20/component_patch_meld.md
  - system_docs/patches/active/scope_aware_purge_2026_09_20/component_patch_conduit.md
  - system_docs/patches/active/scope_aware_purge_2026_09_20/code_description_patch_creations.md
  - artifacts/purge_implementation_20260920/
- DISPOSITION: promote_to_documentation for patch contracts; retain_as_reference for validation.
- CLEANUP_TRIGGER: accepted feature closure after canonical promotion.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: refer to discovery plan and current source before changing the contract.

## Validation
- Final implementation selection: 270 passed in 1.62 seconds, including 77 purge cases, 22
  reference-discovery cases and the existing Creations/Meld/lineage/cluster regressions.
  Evidence: artifacts/purge_implementation_20260920/instance_purge_final.log and instance_purge_final.xml.
- Test Ruff passes with UP007/UP045 excluded for required Union/Optional syntax. Runtime critical
  rules E9,F63,F7,F82 pass. Logs: instance_purge_test_lint.log and instance_purge_source_lint.log
  under the same artifact directory. No generation was performed.
- Reference-discovery experiment: 22 passed in 0.52 seconds; scoped Ruff passed with UP007/UP045
  excluded to preserve the role's required Union/Optional syntax. No production code changes.
  Evidence: artifacts/purge_implementation_20260920/instance_reference_discovery_final.log,
  instance_reference_discovery_final.xml and instance_reference_discovery_lint_final.log.
- Initial experiment output is retained separately: two invalid duplicate-name fixture failures
  were corrected without changing the validator or bypassing it; twenty other cases already passed.
- Source-only validation after the multiple-disposal change: 226 passed in 1.29 seconds.
  Logs: artifacts/purge_implementation_20260920/multiple_disposal.log and multiple_disposal.xml.
- Test-module Ruff check passed with UP045 excluded to retain the required Optional/Union style.
  Critical runtime Ruff rules E9,F63,F7,F82 passed for the six runtime files.
- No asset, graph or index regeneration after the owner's code-approval gate. Earlier generated
  outputs are stale relative to the concrete-door refactor and shared disposal helper.
- Full suite and coverage: Not run. Discovery baseline: 38 passed, two extraction cases deselected.
- No performance claim; existing meld code paths must remain unchanged.

## Risks / Rollback
- Purge cannot revoke external references; pre-existing consumers retain their injected values.
- Supplied objects remain on Spell.user_created_object; store removal is not unbinding.
- Concurrent structural changes/terminal cleanup follow existing lifecycle coordination.
- Rollback removes only this feature and its generated/doc additions; never discards unrelated work.

## Applicable Anti-Patterns
- [x] No scope checks in Creations.
- [x] No extraction-based implementation.
- [x] No new locks/checks on the existing meld hot path.
- [x] Generated staleness is explicit; validation claims identify the executed selection.

## Notes
- DATETIME: 2026-09-20T22:06:15Z
  TYPE: DECISION
  CLAIM: Owner corrected the proposed scope-check placement: keep it in Meld; Creations owns
    creations only. Source confirms the generalized planner also chooses Spell._lock only for unique,
    and store locks for every other Existence. This agrees with direct-root executors.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2666-2676
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-870
  - artifacts/purge_scope_discovery_20260920/plan.md
  IMPACT: The original four-file plan is authorized with no caller-policy fields added to Creations.
  NEXT: Write the regression tests, then implement the approved boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:06:15Z
  TYPE: PLAN
  CLAIM: Patch contracts read in architecture, component, then code-description order. Mapping:
    Creations contract -> native purge/detach helpers -> value/disposal/lock tests; Meld contract ->
    existing lookup and lifetime/store authority helper -> root/lesser/space/cluster refusals; facade
    contracts -> thin public normalization -> selector and scope-lifecycle tests. Keep meld unchanged.
  EVIDENCE:
  - system_docs/patches/active/scope_aware_purge_2026_09_20/architecture_patch.md
  - system_docs/patches/active/scope_aware_purge_2026_09_20/code_description_patch_creations.md
  IMPACT: Patch entry/consumption gates are satisfied under the existing owner authorization.
  NEXT: Execute feature regressions red, then implement the native operation and forwarding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-20T22:13:01Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner requires reuse of established disposal mechanics and clarified two targeting forms.
    Asked whether a created many-instance reference purges exactly that instance while Spell/selectors
    purge the bucket, or whether the two forms are direct Spell and normal selectors, both bucket-wide.
    No runtime implementation exists yet. Scope-authority and disposal regressions are independent.
  EVIDENCE:
  - Owner correction on 2026-09-20 about object/Spell references and normal meld targeting.
  IMPACT: Do not finalize instance-versus-binding dispatch until the reply arrives. The existing
    no-extraction, Meld-scope and Creations-lock/disposal boundaries remain unchanged.
  NEXT: Write binding-selector scope regressions while awaiting the targeting clarification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:17:11Z
  TYPE: DECISION
  CLAIM: Owner selected purge_all: bool = True. Default targeting removes the resolved Spell's
    retained entries; purge_all=False uses the supplied created-instance reference for identity-only
    removal. Direct Spell metadata and normal meld selectors are supported for whole-binding removal.
    Type/instance discovery already exists in SpellInputUtils and must be reused.
  EVIDENCE:
  - Owner reply on 2026-09-20: add purge_all, default enabled.
  - src/melder/utilities/helpers/general_helpers.py:274-294
  - src/melder/utilities/helpers/general_helpers.py:372-430
  IMPACT: Add only the bool and optional internal creation reference to the native purge contract.
    Single-instance mode refuses a class/name/id-only target rather than guessing a many entry.
  NEXT: Add exact-reference tests and implement both removal forms using existing disposal helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:23:05Z
  TYPE: FACT
  CLAIM: Initial regressions failed at the missing Conduit.purge API. Four production files now
    implement the approved split: Meld resolves direct Spell or normal selectors, checks scope and
    selects a store; Creations takes the existing writer locks, detaches all or one identity and
    reuses _dispose_disposable_registry/_attempt_cleanup. Public facades carry purge_all=True.
    Added scope, exact-reference, ordered disposal, real constructor-race and callback-lock tests.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/red.log
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py
  - src/melder/aether/conduit/creations/creations.py
  - src/melder/aether/conduit/meld/meld.py
  IMPACT: Native retirement has no scope-policy inputs and no extraction/transfer calls. Existing
    meld bodies remain unchanged. Validation is next; no pass claim yet.
  NEXT: Run the focused feature module and address concrete failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:23:53Z
  TYPE: MEASURE
  CLAIM: First feature run reached 43 passes and three failures. Scope selection, whole-bucket
    retirement, selectors and lock-order tests passed. Failures involve inherited cleanup methods on
    test subclasses: many instances are untracked and singleton retirement returns one without disposal.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/feature_first.log
  IMPACT: Verify bind-time disposal admission before changing runtime behavior; tests must declare
    the actual configured disposal contract.
  NEXT: Read the disposal matching seam, fix any fixture mismatch, and extend cluster/edge coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-20T22:26:15Z
  TYPE: FACT
  CLAIM: Bind matches disposal candidates against ClassBindingProfile.method_names, and that
    profile enumerates cls.__dict__ only. The failed test subclasses inherited cleanup but did not
    declare it, so their Spells had no recorded disposal. Fixtures now declare cleanup explicitly;
    production disposal matching is untouched. Added distinct-owner cluster, borrower and input checks.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:441-465
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:65-138
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py
  IMPACT: The tests now exercise real retained/disposable creations under the existing bind contract.
  NEXT: Run the full feature selection and existing creation/scope regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:33:13Z
  TYPE: DECISION
  CLAIM: Owner corrected the interpretation: "spell" meant the actual created instance, never the
    internal Spell metadata object. Removed the runtime Spell import and special public dispatch;
    restored its existing TYPE_CHECKING-only import. Owner explicitly deferred the instance-target
    part. This tranche implements normal name/type/frame/id discovery and whole-target purge only;
    instance references and purge_all=False explicitly raise NotImplementedError.
  EVIDENCE:
  - Owner correction on 2026-09-20: implement the other features and flag instance targeting unimplemented.
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/creations/creations.py
  IMPACT: The initial 139-pass result predates this scope correction. Exact-instance removal code
    and its public internal-Spell test were removed; final validation must cover explicit deferral.
  NEXT: Finish documentation/assets for the normal-selector tranche and rerun its final regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:39:24Z
  TYPE: FACT
  CLAIM: The normal-selector implementation and explicit instance deferral are documented in the
    public scope guide and canonical architecture/component maps. Native Creations has no scope
    authorization or caller-policy payload. Source descriptors record only the new responsibilities;
    measured C1 ranges were refreshed and a pre-edit multiset proves no prose was lost.
  EVIDENCE:
  - docs/intermediate/scopes.md
  - artifacts/purge_implementation_20260920/document_validation.json
  - context_compass/system_docs/src_components.md
  IMPACT: Documentation and epic now distinguish delivered selector-based purge from deferred
    instance targeting. No runtime Spell import or metadata-object dispatch remains.
  NEXT: Regenerate indexes/graph and packaged assets; execute final corrected scope tests/checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:47:21Z
  TYPE: DECISION
  CLAIM: Owner requires a code-review boundary before any further asset regeneration. Move conduit
    purge orchestration/store policy into ConduitMeld and SpellSpace policy into SpellSpaceMeld;
    shared Meld retains only the abstract contract and shared selector discovery. Expand the new
    production/test docstrings to the role's Purpose/Contract/Args/Returns/Raises/lifecycle style.
  EVIDENCE:
  - Owner instruction on 2026-09-20: improve code, use concrete Meld doors, do not regenerate until approval.
  IMPACT: Scope now includes the two concrete doors. Previously generated assets remain on disk but
    will be stale after this refactor; do not rebuild them or their graph/index derivatives until approval.
    Final review must explicitly state that deferred work. Source tests remain authorized.
  NEXT: Refactor the concrete doors and improve docstrings, then run source-only validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T22:57:31Z
  TYPE: FACT
  CLAIM: ConduitMeld now owns purge orchestration and _get_purge_creations authority/routing;
    SpellSpaceMeld owns its local-only purge orchestration. Base Meld declares an abstract purge
    contract and _resolve_purge_spell discovery helper with no store selection. New production and
    test docstrings state purpose, contracts, arguments/results and lifecycle/locking behavior.
    Optional/Union and TYPE_CHECKING-only Spell imports are retained per the selected role.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:Meld.purge
  - src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld.purge
  - src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.purge
  - src/melder/aether/conduit/creations/creations.py:Creations.purge
  IMPACT: No asset builder, graph generator or index generator has run since the owner imposed
    the code-approval gate. The corrected source still needs its final source-only checks.
  NEXT: Run source regression/lint checks, then present the code for review with assets held.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:14:32Z
  TYPE: PLAN
  CLAIM: Owner selected the multiple-disposal work while leaving object discovery for later.
    Current whole-registry cleanup already loops over many metadata and calls _attempt_cleanup;
    targeted purge reaches that loop by building a temporary one-key registry. Factor the many
    loop into a native shared helper, call singular disposal directly, and reuse both from purge
    and whole-registry cleanup. Preserve ordering and per-object failure semantics.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:205-269
  - src/melder/aether/conduit/creations/creations.py:381-449
  IMPACT: Only Creations disposal mechanics and focused behavior tests change. Scope routing,
    instance discovery and the owner-gated generated assets remain untouched.
  NEXT: Extend the many test to multiple captured failures across both facades, then share the
    existing disposal loop and run source-only validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:17:54Z
  TYPE: FACT
  CLAIM: Creations now shares _dispose_many_creations between purge and whole-store disposal.
    The helper visits detached many entries newest-first, reuses _attempt_cleanup per object and
    collects failures without stopping other objects. Singular purge calls _attempt_cleanup directly;
    the temporary single-key registry is gone. The targeted test now captures two failures at
    different method positions across both Conduit and SpellSpace while preserving another target.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:Creations._dispose_many_creations
  - src/melder/aether/conduit/creations/creations.py:Creations.purge
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py:test_purge_many_preserves_disposal_order_and_aggregates_failures
  IMPACT: Single and batch retirement reuse the existing disposal practice. Scope routing,
    creation locks, instance-discovery deferral and the no-regeneration gate are unchanged.
  NEXT: Run the existing cleanup/purge/Meld regressions and source lint checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:24:12Z
  TYPE: MEASURE
  CLAIM: Source-only purge, Creations, Meld and existing scoped regressions passed: 226 tests in
    1.29 seconds. The feature-module Ruff check and critical runtime lint rules also passed.
    Re-entry confirmed the saved logs; no additional test run or generation was needed.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/multiple_disposal.log:1-5
  - artifacts/purge_implementation_20260920/multiple_disposal_test_lint.log:1-1
  - artifacts/purge_implementation_20260920/multiple_disposal_source_lint.log:1-1
  IMPACT: The shared multiple-disposal implementation has passing source regression evidence.
    Generated artifacts remain deliberately stale pending the owner's explicit code approval.
  NEXT: Read the final disposal helper and its regression, then hand back the bounded delivery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:26:00Z
  TYPE: FACT
  CLAIM: Final source reread confirms targeted many purge and whole-store teardown share
    _dispose_many_creations, which calls _attempt_cleanup for every detached entry newest-first.
    Per-object method ordering and first-failure behavior remain unchanged. The two-failure
    regression covers both public facades, unrelated bindings and no repeat disposal at shutdown.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:205-320
  - src/melder/aether/conduit/creations/creations.py:429-548
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py:413-501
  - artifacts/purge_implementation_20260920/multiple_disposal.xml:1-1
  IMPACT: Multiple disposal is ready for owner review. Component flow prose still names the
    pre-refactor base-Meld orchestration and registry-wrapper disposal path. Update that prose,
    descriptors and generated products together only after the owner's code approval.
  NEXT: Present the completed multiple-disposal tranche; await direction on deferred discovery
    and explicit approval before any generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:29:00Z
  TYPE: PLAN
  CLAIM: Owner requests an experiment establishing whether normal meld accepts an application
    instance reference and whether the existing lookup identifies its binding or the exact creation.
    Trace SpellInputUtils and the concrete Meld doors, then exercise default, named, framed and
    scoped bindings with real instances. Keep purge implementation and generated outputs unchanged.
  EVIDENCE:
  - Owner request on 2026-09-20: run an experiment with meld(reference) before instance discovery.
  - src/melder/utilities/helpers/general_helpers.py
  - src/melder/aether/conduit/meld/meld.py
  IMPACT: The next approved step is source-backed characterization, not the deferred implementation.
  NEXT: Read the selector call path and relevant test setup; add and execute a focused experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:34:00Z
  TYPE: FACT
  CLAIM: Normal Meld accepts a non-string instance in its selector path. SpellInputUtils derives
    __name__ or type(instance).__name__, then combines it with the explicit frame and binding name.
    _resolve_spell looks up that key; it never checks creation identity. Concrete doors use the
    selected Spell for ordinary execution/reuse. Purge can reuse this discovery without calling meld.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:273-423
  - src/melder/aether/conduit/meld/meld.py:1403-1641
  - src/melder/aether/conduit/meld/conduit_meld.py:424-553
  - src/melder/aether/conduit/meld/spellspace_meld.py:397-519
  IMPACT: A reference appears sufficient for ordinary class-name/default bindings, but inferred
    names cannot prove the originating binding or exact scope membership. Executable cases must
    distinguish those concerns before any instance-purge implementation.
  NEXT: Add the focused real-runtime experiment covering ordinary, named, framed, factory and scoped inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:36:52Z
  TYPE: FACT
  CLAIM: Added a 22-case experiment covering reference lookup versus returned object identity,
    both public facades, named/default bindings, explicit frames, scope changes, supplied instances,
    factory products and unhashable instances. Tests assert the characterized source contracts;
    runtime purge and all generated files are unchanged.
  EVIDENCE:
  - tests/experimentation/test_meld_instance_reference_discovery_experiment.py
  IMPACT: The executable selection can confirm which discovery semantics purge may reuse.
  NEXT: Run this experiment through the existing uv environment and retain output/XML.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-20T23:36:52Z
  TYPE: MEASURE
  CLAIM: First reference-discovery experiment: 20 passed and two setup failures. Ordinary,
    named/frame-qualified, many, cross-scope, supplied-object, factory-product and unhashable cases
    matched source. The two failures occurred at conjure: the duplicate-name validator rejects
    default plus blue bindings of the same unframed class before the intended lookup runs.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/instance_reference_discovery.log
  - tests/experimentation/test_meld_instance_reference_discovery_experiment.py:214-242
  IMPACT: Do not claim that dual-binding fixture is a supported world or bypass its validator.
    Replace it with the narrower valid experiment: a never-registered same-type reference can
    select a default binding without becoming the returned managed instance.
  NEXT: Verify the validator contract, correct that fixture, and rerun the experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:38:00Z
  TYPE: FACT
  CLAIM: DuplicateSpellNameStrategy groups visible definitions by spell_name alone, explaining
    the two pre-runtime failures. The experiment now uses one valid default binding and a fresh
    unregistered reference to prove membership is not checked and the input is not adopted.
    No validator or runtime behavior was changed; the initial failed fixture output is retained.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:72-154
  - tests/experimentation/test_meld_instance_reference_discovery_experiment.py:217-241
  IMPACT: The corrected experiment isolates reference discovery without relying on an invalid world.
  NEXT: Execute the corrected 22-case experiment and scoped lint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T23:39:00Z
  TYPE: MEASURE
  CLAIM: Reference-discovery experiment passes all 22 cases in 0.52 seconds. Both public facades
    accept instance references. The lookup-only helper returns the registered Spell without
    construction, while meld(instance) follows normal Existence: singleton reuse or fresh many.
    Named bindings and distinct frames require explicit qualifiers. An unregistered same-type
    object can select a binding; cross-scope references resolve in the caller's scope. A factory
    product's class name does not recover the factory binding. Unhashable instances also resolve.
  EVIDENCE:
  - tests/experimentation/test_meld_instance_reference_discovery_experiment.py:129-325
  - artifacts/purge_implementation_20260920/instance_reference_discovery_final.log:1-26
  - artifacts/purge_implementation_20260920/instance_reference_discovery_lint_final.log:1-1
  IMPACT: Recommended future reuse: the existing lookup selects the binding; retain the original
    application reference separately and use identity within the authorized Creations store for
    exact-instance removal. Lookup does not certify membership or recover missing qualifiers.
    This is a proposal only; production code and generated products remain unchanged this tranche.
  NEXT: Explain the results and discuss the bounded instance-purge behavior with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:03:38Z
  TYPE: DECISION
  CLAIM: Owner accepted two input paths and directed implementation. An instance is another
    selector: inspect its class, then use the existing Spell lookup. Discovery does not search
    stored objects or recover binding metadata. Keep scope policy in the concrete doors and pass
    purge_all plus the original reference to Creations for whole-target or single-object retirement.
  EVIDENCE:
  - Owner's clarification and explicit implementation direction after the 22-case experiment.
  - src/melder/aether/conduit/meld/meld.py:533-601
  - src/melder/aether/conduit/creations/creations.py:429-548
  IMPACT: Changes are bounded to the six purge runtime surfaces, their tests and manual public
    documentation. Single removal searches only the already-selected many bucket and preserves
    paired disposal records. False without an instance raises ValueError instead of choosing one.
    No regular meld changes or generated artifacts are authorized by this tranche.
  NEXT: Update the patch contracts and regressions, then implement discovery/retirement and validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:07:00Z
  TYPE: MEASURE
  CLAIM: Thirteen focused instance/single-removal cases fail against the prior implementation,
    at its explicit NotImplementedError guards or missing Creations keyword arguments. The new
    tests also cover class inspection despite an instance __name__, scope isolation, sparse
    disposal metadata, failed disposal and competing single purges. Lock-family tests cover both modes.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/instance_purge_red.log
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py
  IMPACT: The regressions exercise the missing feature. Updated patch contracts preserve existing
    scope, locking and disposal behavior; only discovery and per-target multiplicity are extended.
  NEXT: Implement inspected-class lookup, concrete-door forwarding and native single detachment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:10:00Z
  TYPE: FACT
  CLAIM: Implemented the accepted shortcut: shared purge discovery inspects an instance's class
    and calls existing _resolve_spell. Concrete doors retain scope checks and forward the original
    instance only for single removal. Creations detaches that singleton or one selected many entry
    with matching disposal metadata under existing writer locks, then reuses established disposal.
    Full purge keeps the existing bucket path. Public docstrings/guide explain both input paths.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:Meld._resolve_purge_spell
  - src/melder/aether/conduit/creations/creations.py:Creations._detach_single_many_creation
  - docs/intermediate/scopes.md
  IMPACT: No reverse discovery index, metadata recovery, scope policy in Creations, ordinary meld
    changes or asset generation. Single removal returns zero for an unretained reference.
  NEXT: Run the purge suite and retained discovery experiment; inspect any concrete failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:12:00Z
  TYPE: MEASURE
  CLAIM: First implemented run passes all 92 cases: 70 purge checks plus the 22 reference-lookup
    experiments. Both facades, single/all modes, lock families, competing removal, sparse metadata
    and disposal failure behave as intended.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/instance_purge_first.log:1-3
  IMPACT: The core implementation is green. Final review will include explicit qualified-instance
    selectors, last-entry retirement and application equality that must not run during disposal.
  NEXT: Complete those bounded regression checks and run the existing creation/Meld/scope selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:13:20Z
  TYPE: MEASURE
  CLAIM: Final source selection passes 270 checks in 1.62 seconds: 77 purge cases, the 22
    reference experiments and existing Creations, Meld, lineage and cluster regressions. Scoped
    test lint and critical runtime lint pass. Final reread confirms class-based discovery and
    paired single/all retirement through the existing scope owners and disposal methods.
  EVIDENCE:
  - artifacts/purge_implementation_20260920/instance_purge_final.log:1-5
  - artifacts/purge_implementation_20260920/instance_purge_test_lint.log:1-1
  - artifacts/purge_implementation_20260920/instance_purge_source_lint.log:1-1
  - src/melder/aether/conduit/meld/meld.py:533-602
  - src/melder/aether/conduit/creations/creations.py:429-635
  IMPACT: The requested source implementation is ready for review. No further tests are needed
    without a new change or failure; full-suite/coverage and generated freshness are not claimed.
  NEXT: Present the implemented API; await explicit code approval before any generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T00:22:00Z
  TYPE: DECISION
  CLAIM: Owner accepted the feature and explicitly requested epic turn-in. This satisfies the
    code-review gate for the previously held canonical documentation and generated assets. Complete
    that final work, then close this task, the purge discovery/planning tasks and their parent epic.
  EVIDENCE:
  - Owner instruction: "go ahead and turn in your epic since your finished".
  - artifacts/purge_implementation_20260920/instance_purge_final.log:1-5
  IMPACT: No new runtime changes, release, commit or push. Preserve other agents' concurrent board
    and documentation work. Retain validation evidence and archive promoted patch contracts.
  NEXT: Update canonical purge descriptions/descriptors, regenerate their indexes/assets and verify.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Both input paths and single/all retirement are implemented. purge(instance) inspects the class and
uses existing _resolve_spell; explicit name/class/function/frame/id selectors remain available.
The shortcut is a choice, not a promise of automatic binding metadata recovery. No reverse index,
registry search during discovery, runtime Spell import or ordinary meld changes were added.

ConduitMeld and SpellSpaceMeld retain scope authority. Creations receives the selected definition,
purge_all and the original creation for False. True retires the target bucket/singleton; False
requires an instance and retires its one stored entry, or returns zero if absent. Only the selected
many bucket is searched during single removal, with paired sparse disposal metadata and empty-key
cleanup under existing locks. Disposal runs after lock release through the existing helpers.

All 270 focused tests and scoped lint pass. The public guide and touched docstrings describe the
current API. NEXT: owner reviews the code. Do not run asset, graph or index generators until the
owner explicitly approves. Earlier generated outputs and canonical component flow prose predate
these refactors; finish those together after approval. The ticket remains open for that final step.
