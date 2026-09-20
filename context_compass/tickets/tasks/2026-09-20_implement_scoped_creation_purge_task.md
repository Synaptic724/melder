# Task: Implement scoped purge through Meld and Creations

## Metadata
- Task ID: TASK-2026-09-20-implement-scoped-creation-purge
- Epic: EPIC-2026-09-19-scope-aware-creation-purge
- Story: none; bounded implementation after completed discovery
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-20T22:06:15Z
- Updated: 2026-09-20T22:06:15Z

## Objective
Implement the approved purge operation with Meld owning selection/scope authority and Creations
owning only removal, locking and disposal. Preserve existing meld execution and scope lifetimes.

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

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner accepted the plan and directed implementation with the original responsibility split.

## Steps / Checklist
- [x] Confirm the writer-lock mapping and record patch contracts.
- [ ] Add meaningful failing regression coverage for stores, locks and public scope authority.
- [ ] Implement native Creations purge, shared Meld routing and both public facades.
- [ ] Run focused feature and existing-scope regressions; repair failures within this boundary.
- [ ] Update documentation/descriptors, regenerate assets and check freshness.
- [ ] Record delivery and leave the ticket ready for owner review.

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
- Not run for implementation at intake. Discovery baseline: 38 passed, two extraction cases deselected.
- No performance claim; existing meld code paths must remain unchanged.

## Risks / Rollback
- Purge cannot revoke external references; pre-existing consumers retain their injected values.
- Supplied objects remain on Spell.user_created_object; store removal is not unbinding.
- Concurrent structural changes/terminal cleanup follow existing lifecycle coordination.
- Rollback removes only this feature and its generated/doc additions; never discards unrelated work.

## Applicable Anti-Patterns
- [ ] No scope checks in Creations.
- [ ] No extraction-based implementation.
- [ ] No new locks/checks on the existing meld hot path.
- [ ] No stale generated asset or unexecuted validation claims.

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

## Context / Handoff Summary
Implementation authorized. Patch id scope_aware_purge_2026_09_20. The crucial boundary is Meld scope
authorization/selection -> Creations.purge(spell) lock/detach/dispose. Unique adds Spell._lock before
the store lock; other modes use only their actual store lock. No runtime changes at intake.
