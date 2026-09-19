# Task: Trace existing-object references from registration through compiler and lifecycle

- Completed: 2026-09-19T12:51:19Z
- Disposition: retired_by_owner; proposed redesign not pursued.
- Summary: Owner retains the current unique-only supplied-object model and explicitly retires the
  broader redesign. Research and unimplemented proposals below are historical, not pending directives.
  The delivered Protocol repair remains separate. Provider-artifact repair resumes in its original task;
  this retirement does not mark the known artifact bug fixed or make its failing tests expected behavior.


## Metadata
- Task ID: TASK-2026-09-17-trace-existing-object-reference-model
- Story: STORY-2026-09-17-existing-object-reference-blueprint-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-17T21:22:19Z
- Updated: 2026-09-19T12:51:19Z

## Objective
Produce a source-backed current/proposed model for externally supplied references, non-creatable
blueprints, existing scope/lifetime routing and coherent ownership/persistence behavior.

## Ticket Contract
- ENTRY_GATE: linked discovery story, explicit owner request and active board route.
- EXECUTION_BOUNDARY: scoped source reads, isolated diagnostic probes and authored design/evidence only.
- DEPENDENCIES: parent epic and prior existing-instance, Protocol and provider-artifact findings.
- EXIT_GATE: all four trace areas are evidenced; candidate contracts and unresolved decisions are concrete.
- FAILURE_ESCALATION: record unknowns before widening a claim; do not replace unavailable code/state with assumptions.

## Scope Boundaries
- In scope: supplied-reference classification, requirements/plan/executor captures, registry/lookup identity,
  Conduit/SpellSpace stores, transfer/rollback and SpellCrystal/SyntheticModule capture/replay.
- Out of scope: production changes, package/environment installs, independent provider-artifact patches,
  unrelated source cleanup and repeated generic DI research.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: source traces, nine native observations and candidate contract/impact matrix are reviewable.

## Steps
- [x] Trace registration, existing-value classification and representative requirements/compiled execution.
- [x] Trace lifetime stores, external-value admission, staging, transfer and rollback.
- [x] Trace capture/replay with physical source, synthetic source and only a live reference.
- [x] Resolve selected behavior unknowns with bounded native probes; preserve untested hazards explicitly.
- [x] Write the proposed contract/impact matrix, preserve alternatives and identify owner decisions.
- [x] Verify evidence links and synchronize story/epic routing for review.

## Deliverables
- artifacts/existing_object_discovery_20260917/discovery.md.
- Focused probes/logs in the same directory when needed, with source identity and proof limits.
- Current source-to-contract and contract-to-validation maps, with no runtime implementation claim.

## Required Context / Reread Pointers
- Parent epic's Primary Exploration and its verbatim owner proposal.
- Relevant sections of src_components through its verified index: Binding Pipeline; SpellCompiler;
  Meld; Creations/SpellSpace; ConduitWard/Ownership Transfer; Crystallizer/SyntheticModule.
- src_graph slices for the exact classes discovered there; current source is authoritative.
- Earlier task/artifact results establish that supplied A injects into B and that Protocol admission
  and provider artifacts have separate recorded gaps. Do not reinterpret passing observation tests as fixes.

## Initial Source Targets
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/spell.py
- src/melder/aether/spellbook/resolution_style_matrix.py
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py
- src/melder/aether/conduit/meld/conduit_meld.py
- src/melder/aether/conduit/meld/spellspace_meld.py (path verified on 2026-09-17).
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
- src/melder/crystallizer/crystals/spell_crystal.py
- src/melder/crystallizer/synthetic_module.py
- src/melder/crystallizer/crystal_loader_system/restore_engine.py

## Validation
Nine native characterization cases executed on Python 3.14.7: four transition and five crystal/identity
cases. The pre-conjure staged case records a real missing-CreationContextFactory refusal. Passing
characterization is not repair acceptance. Both probe files pass Ruff F. Full suite, performance,
fault injection/concurrency, full checkpoint replay and all codegen variants were not newly tested.

## Risks / Rollback Notes
- A fixed live-reference shortcut can bypass scope-specific storage even after metadata allows a new lifetime.
- Presence flags and source modes may currently be conflated; do not solve this by weakening validation.
- No module file is not proof that code is unavailable, and a live reference is not proof of reconstructible state.
- Provider artifact sharing is a separate trace within the broader ownership program, not a reason to overwrite
  shared state under borrower visibility.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_object_discovery_20260917/discovery.md
  - artifacts/existing_object_discovery_20260917/test_reference_transitions.py
  - artifacts/existing_object_discovery_20260917/reference_transitions.log
  - artifacts/existing_object_discovery_20260917/reference_transitions.xml
  - artifacts/existing_object_discovery_20260917/test_reference_crystals.py
  - artifacts/existing_object_discovery_20260917/reference_crystals.log
  - artifacts/existing_object_discovery_20260917/reference_crystals.xml
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain compact source and experiment evidence for the discovery/implementation sequence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record concrete missing evidence or policy choice before continuation.

## Notes
- DATETIME: 2026-09-19T12:51:19Z
  TYPE: DECISION
  CLAIM: Owner explicitly selected: Retire the broader redesign; fix the artifact bug next.
    Current supplied-object uniqueness remains. Unimplemented model expansion is withdrawn, not delivered.
  EVIDENCE:
  - Owner's explicit choice in the current conversation.
  - tickets/tasks/completed/2026-09-13_repair_provider_artifact_ownership_task.md
  IMPACT: This lane is retired with its findings retained. No production ownership redesign is shipped.
  NEXT: Follow the provider-artifact repair task under the retained current model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:22:19Z
  TYPE: PLAN
  CLAIM: Discovery begins with how a bound target becomes an existing creation and how that choice
    reaches requirements and compiled value retrieval. Then trace stores/transfer and source custody,
    keeping fixed supplied values distinct from definitions awaiting external input.
  EVIDENCE:
  - tickets/stories/completed/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
  IMPACT: This creates durable discovery state before source work. No representation or public API is chosen.
  NEXT: Verify the current indexes and read the registration/compiler branch as one coherent unit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-17T21:36:00Z
  TYPE: FACT
  CLAIM: Existing classification and value presence are already distinct on Spell. Bind still chooses
    the family from the actual supplied target. Direct existing executors bypass scope stores and read
    Spell.user_created_object; consumer runtime-model processing also captures the value reference.
    Relaxing unique-only admission alone cannot establish per-scope external-value resolution.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:323-523
  - src/melder/aether/spellbook/spell.py:955-1066
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:40-101
  IMPACT: Preserve the existing classification/presence distinction. A candidate design needs explicit
    external-only definition admission and a common retrieval authority for direct and nested resolution.
    Constructor discovery remains suppressed; the prior Phase-8/9 repair is not undone.
  NEXT: Trace nested compiled retrieval and current store/transfer ownership before selecting representation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:36:01Z
  TYPE: FACT
  CLAIM: Active existing values enter Creations, but staged admission/reactivation lacks that same
    registration. Transfer moves Spell ownership separately from store payloads. Its no-move helper
    extracts an entry without disposal or clearing the Spell reference. Move rollback is registered
    only after target restore, and per-member failures are swallowed; custody atomicity is unproven.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4752-4951
  - src/melder/aether/spellbook/spellbook.py:1507-1563
  - src/melder/aether/conduit/creations/creations.py:376-514
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1503-1646
  IMPACT: The design must coordinate value retention, active selection, scope admission and cleanup
    responsibility. Existing transaction and store names alone do not prove a coherent transfer contract.
  NEXT: Characterize native transfer/no-move and staged-value store state, then trace crystal replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:39:00Z
  TYPE: MEASURE
  CLAIM: Four isolated native transition observations completed. move_creations=False still returns
    the original reference after both source/target stores lose it; True moves its store entry.
    Post-conjure staging/notch returns the supplied object without store admission. Pre-conjure staging
    followed by notch reaches meld but fails with no configured CreationContextFactory.
  EVIDENCE:
  - artifacts/existing_object_discovery_20260917/test_reference_transitions.py:1-122
  - artifacts/existing_object_discovery_20260917/reference_transitions.log:1-6
  IMPACT: These are real transition gaps the coherent model must cover. The four passing tests record
    current outcomes, including the refusal, and are not assertions of corrected behavior.
  NEXT: Trace crystal/source capture and external replay, then synthesize the candidate contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:41:24Z
  TYPE: FACT
  CLAIM: Instance crystals remain replay_required even when their source is synthetic; target hydration
    refuses before module reconstruction. SyntheticModule requires source text. Phase 4 also requires
    an attached existing value, so definition-first supply needs explicit structural-versus-runtime rules.
    Provider artifact publication still spans visible Spells while the fused rebuild queue is owned-local.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:249-342
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2456-2517
  - src/melder/crystallizer/synthetic_module.py:327-460
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py:79-163
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:311-368
  - src/melder/aether/spellbook/spellbook_creation_system.py:3084-3156
  IMPACT: Persist the external-only policy independently of module replay. Restored definitions need
    explicit unsupplied state; runtime identity/state is not recoverable merely from recorded source.
    Artifact publication authority and live-value cleanup custody both need explicit owners.
  NEXT: Probe synthetic-source versus live-only crystal capture and synthesize the reviewable design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:43:48Z
  TYPE: MEASURE
  CLAIM: Five additional probes passed: synthetic instance source is retained but replay_required;
    the same class definition is hydratable; a live-only named origin produces an unknown-source crystal;
    a nameless origin binds but crystal construction refuses. Equal repr metadata can give different
    instances the same fingerprint; naming can give one instance different fingerprints. Ruff F passed.
  EVIDENCE:
  - artifacts/existing_object_discovery_20260917/test_reference_crystals.py:1-125
  - artifacts/existing_object_discovery_20260917/reference_crystals.log:1-7
  IMPACT: Definition availability, registration fingerprint and live-object identity must remain
    distinct. Synthetic-module support is useful when source exists; it is not automatic state recovery.
  NEXT: Synthesize the candidate external-only contract, impact/qualification map and owner decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:46:58Z
  TYPE: PLAN
  CLAIM: Initial discovery is ready for owner review. Recommend explicit external-only source policy
    plus normal scope value admission, separating definition/registration identity, live values,
    cleanup custody and executable artifact authority. No public representation or runtime patch selected.
  EVIDENCE:
  - artifacts/existing_object_discovery_20260917/discovery.md:187-370
  - artifacts/existing_object_discovery_20260917/reference_transitions.log:1-6
  - artifacts/existing_object_discovery_20260917/reference_crystals.log:1-7
  IMPACT: Review the first direction before implementation. Remaining decisions cover custody start,
    aliases, lifetime meanings, replacement/transfer and opaque-origin recording. Full variant/failure
    qualification remains in the impact map, not implied by the nine passing characterization cases.
  NEXT: Owner reviews the external-only definition plus scoped-admission direction as the first design choice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T22:21:43Z
  TYPE: DECISION
  CLAIM: Initial broad discovery remains a reviewable evidence record. Owner now requests sequential
    design beginning with a user-bound existing instance handled normally with construction disabled.
    The new bind-representation task is the continuation route; do not rerun this entire trace on re-entry.
  EVIDENCE:
  - tickets/stories/completed/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  - tickets/tasks/completed/2026-09-17_existing_object_bind_representation_design_task.md
  IMPACT: Preserve all observations and earlier candidates while giving later agents one concrete stage.
  NEXT: Open the bind-representation design task and compare normal class metadata with supplied-instance metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Noting Behavior
Record each completed source trace or probe result before the next tranche. Preserve exact evidence
ranges, identity/version information and one next step; distinguish proposed changes from current behavior.

## Context / Handoff Summary
Initial discovery ready for review; no production edits. CONTINUE through the story's Current Checkpoint
and tickets/tasks/completed/2026-09-17_existing_object_bind_representation_design_task.md, Stage 1 only.
Reuse this task/artifact's nine observations and source map. The current input is the actual instance
supplied to bind; normal machinery with construction disabled is the target. Transfer/store divergence,
staged factory wiring and synthetic/live-only replay evidence remain available for their later stages.
