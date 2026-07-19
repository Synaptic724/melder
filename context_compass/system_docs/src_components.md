

# Src Components (C3/C2/C1)

## Metadata
- Doc ID: COMP-SRC-2026-01-17
- Status: in_progress
- Owner:
- Created: 2026-01-17
- Updated: 2026-06-13

## Scope
This document defines C3 components, C2 subcomponents, and C1 code references
for the Melder core platform (`src/melder`). It complements
`context_compass/system_docs/src_architecture.md` by providing component-level
responsibilities, contracts, and relationships.
Melder is framed here as a Dependency Graph Runtime (DGR) with DI-style
binding and resolution as a subset capability.

Out of scope:
- Tests and example docs.
- JSON sidecar metadata files (`__*.json`).

## Documentation Quality Standard
This document is treated as durable context. It must be deep enough to recover
system understanding from a blank slate without handwaving.

Required rules:
- No handwaving. Every claim must be grounded in source evidence or marked as UNKNOWN.
- Explicit entrypoints and method-level call flows for core behavior.
- Explicit ownership, lifecycle, and cleanup order for components.
- Explicit invariants, failure modes, and concurrency constraints.
- ASCII and Mermaid diagrams for core flows.
- Update the information sources list when new files are used.

## DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference (preferred: file + symbol/method/class name).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to the Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).

## Unknowns
This section is a living list of claims currently not backed by evidence.
Each item must include:
- What is unknown.
- Why it matters (impact).
- Where to investigate (file(s) + symbol(s)).
- Current status (uninvestigated / investigating / blocked).

- SYNC NOTE (2026-06-12 path/rename sweep, filesystem-verified):
  - C1 path normalization applied in this doc:
    the Nexus subtree now resolves under `src/melder/nexus/`;
    the dev-ops subtree remains under
    `src/melder/aether/aetheric_frame/dev_ops/`;
    `aetheric_frame.py` and `conduit_cloud.py` now resolve under
    `src/melder/aether/aetheric_frame/`;
    mutation-research paths now resolve under
    `src/melder/mutation_research/`;
    `spell_crafter/` -> `spell_compiler/` (class `SpellCrafter` is now
    `SpellCompiler`; `spell_requirements_finder/` moved up to
    `spell_compiler/spell_requirements_finder/`).
  - Verified renames: `Configuration` -> `SpellbookConfiguration`;
    `conjure(...)` takes `dynamic: bool` (no `automatic` parameter);
    `MeldGate`/`MeldGateController` files replaced by
    `utilities/synchronization/creation_gate.py` /
    `creation_gate_controller.py`; `meld_context/` replaced by
    `creation_context/` (`creation_context.py`,
    `creation_context_builder.py`, `creation_context_factory.py`).
  - Verified removals (paths annotated REMOVED below): runtime
    `MutationContract` descriptor and `MUTATION_CONTRACT_DISABLED` are gone
    from `src/melder`; the `structure_profiles` subsystem is gone; the
    `spell_examiner` AI-profile files are gone (current profiles:
    `binding_profile.py`, `general_profile.py`, `detailed_profile.py`,
    `spell_compiler/profiles/resolution_profile.py`);
    `rift_event_configuration.py` is gone; `phase12_*_executor.py` are gone;
    `creations/creation.py` (the `Creation` wrapper) is gone and
    `conduit_creations.py` is the conduit/root specialization seam;
    `SpellCrafter._phase8_11_codegen_ir_dirty` no longer exists as the owning
    surface; the live field is
    `SpellCompilerArtifact._phase8_11_codegen_ir_dirty`.
  - Verified compiler phase-artifact ownership:
    `SpellCompilerArtifact` is the spell-scoped owner of the phase-8-to-11
    analysis/planning/runtime outputs
    (`_occurrence_graph_analysis`, `_occurrence_order_analysis`,
    `_occurrence_instance_analysis`, `_occurrence_contract_analysis`,
    `_spell_codegen_model`, `_spell_codegen_plan`,
    `_spell_codegen_creation`, `_codegen_ir`,
    `_phase8_11_codegen_ir_dirty`), while the later facade layers publish into
    those slots rather than owning them:
    `SpellAnalyzer` -> occurrence analyses,
    `SpellArtifactProcessor` -> `SpellCodegenModel`,
    `SpellCodegenPlanner` -> `SpellCodegenPlan`,
    `CodegenCreationSystem` -> `SpellCodegenCreation`.

- UNKNOWN: Producer call sites for advanced mutation/contract state flags
  (`SpellState.contract_violation`, `SpellState.mutation_candidate`,
  `SpellState.mutation_quarantined`, `SpellState.mutation_failed`) remain
  unresolved in runtime code.
  Why it matters: Without explicit producers, mutation/contract diagnostics and
  policy gating can drift from actual runtime behavior.
  Clarification: SpellContract/MutationContract descriptor behavior is already
  evidenced and no longer unknown. SpellContract contract-unvalidated wiring is
  present via Phase 4 + `mark_contract_dependents_dirty` call paths; and
  MutationContract sockets are explicitly blocked in Phase 4 with
  `MUTATION_CONTRACT_DISABLED`, while mutation overlays still emit
  `mutation_contract_set` / `mutation_contract_cleared` through
  `Spell.apply_mutation_override` and `Spell.clear_mutation_override`.
  Evidence from current sweep (SYNC NOTE 2026-07-11): the May MR skeleton that
  carried the placeholder hooks (`research/**` with `SpellMutationNode`,
  `CreationMutationNode`, `Research.promote_spell_version`) was DELETED in the
  ResearchSet rebuild; no code path produces these flags today, by design.
  Producers belong to the future MR runtime-seam slice (select/staged/promoted
  acts over the notch/bind_inactive seams).
  Where to investigate:
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`,
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state.py`,
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state_change_reason.py`.
  Follow-up stories:
  `STORY-2026-02-13-spellstate-advanced-flag-producers`,
  `STORY-2026-02-13-mutation-research-runtime-wiring`.
  Current status: blocked (producers await the MR runtime-seam slice).

## Table of Contents
- Metadata
- Scope
- Documentation Quality Standard
- DO NOT ASSUME / Unknowns Gate
- Unknowns
- Table of Contents
- Component Template
- C3 Components Catalog
- C2 Subcomponents Catalog
- Method-Level Call Flows (C1)
- C1 Code Map (Core)
- Diagrams
- Information Sources
- DI Resolution Contract Notes (Spec vs Implementation)
- Open Questions
- Context / Handoff Summary

## Component Template
Each component entry includes:
- Purpose
- Responsibilities
- Inputs
- Outputs
- Owned State
- Lifecycle/Cleanup
- Concurrency/Threading
- Invariants/Guarantees
- Failure Modes
- Observability
- Extension Points
- Key Files (C1)

## C3 Components Catalog

### Component: Public API and Runtime Guardrails
Purpose:
- Provide the package entrypoint and import-time guardrails.

Responsibilities:
- Warn on Python < 3.13 and on GIL-enabled builds.
- Instantiate the registration guard singleton.
- Expose package metadata and version string.

Inputs:
- Python runtime version and `sys._is_gil_enabled()`.

Outputs:
- UserWarning messages.
- Module-level `__melder_registration_guard__` instance.

Owned State:
- Package metadata (`__version__`, `__author__`, `__license__`, `__description__`).
- `__melder_registration_guard__` singleton instance.

Lifecycle/Cleanup:
- Executes at import time; no explicit cleanup.

Concurrency/Threading:
- No explicit locks; import-time only.

Invariants/Guarantees:
- Guard singleton exists after package import.
- Runtime warnings are emitted but do not block execution.

Failure Modes:
- `InternalRegistrationError` when a candidate tagged with the guard sentinel is
  submitted through guarded registration paths.
- Runtime guardrails are warning-only for Python version / GIL mode checks.

Observability:
- Warnings via `warnings.warn`.
- Guard-block failures are surfaced as `InternalRegistrationError` exceptions in
  guarded bind paths.

Extension Points:
- None.

Key Files (C1):
- `src/melder/__init__.py`
- `src/melder/__melder_registration_guard__.py`

### Component: Packaged Hardcopy Documents And Public Helper Exports
Purpose:
- Expose the package-root agent/document surfaces and opt-in helper/config
  utilities that ship alongside the runtime.

Responsibilities:
- Instantiate the package-root hardcopy document objects:
  `__architecture__`, `__components__`, `__graph_network__`, and
  `__graph_details__`.
- Provide the immutable `StaticSystemDocument` carrier used by those exports.
- Export root configuration helpers:
  `AetherConfiguration` and `AetherConfigurationBuilder`.
- Export the public `ProtocolCrafter` helper for protocol generation and
  bounded interface-file maintenance.

Inputs:
- Minified JSON hardcopy payload strings for packaged document modules.
- Public helper/config class implementations wired into `melder.__all__`.

Outputs:
- Package-root `StaticSystemDocument` objects for agent-facing hardcopy access.
- Public helper/config class exports available from the top-level package.

Owned State:
- Module-level `StaticSystemDocument` singletons in the packaged doc modules.

Lifecycle/Cleanup:
- Hardcopy document exports are immutable after import and define no cleanup
  contract.
- Helper/config objects own their own cleanup only when callers instantiate
  them.

Concurrency/Threading:
- Hardcopy exports are import-time objects only.
- Exported helpers use their own instance locks when instantiated.

Invariants/Guarantees:
- Package-root hardcopy docs remain queryable without conjuring a conduit.
- The current packaged hardcopy payloads are placeholder markdown/json
  carriers, not live regenerated architecture snapshots.
- Public helper/config exports do not mutate runtime state merely by being
  imported from `melder`.

Failure Modes:
- Invalid hardcopy JSON would fail import of the packaged doc module.
- Helper/config misuse fails when the helper/config instance is used, not at
  package export time.

Observability:
- `render_json()` / `render_markdown()` on the hardcopy document objects.
- Class-level agent-purpose strings on the packaged document modules.

Extension Points:
- Replacing placeholder hardcopy payloads with real packaged system docs.
- Expanding root configuration policy beyond logger activation.
- Extending protocol generation/file-maintenance helpers.

Key Files (C1):
- `src/melder/system_document.py`
- `src/melder/__architecture__.py`
- `src/melder/__components__.py`
- `src/melder/__graph_network__.py`
- `src/melder/__graph_details__.py`
- `src/melder/aether/aether_configuration.py`
- `src/melder/aether/aether_configuration_builder.py`
- `src/melder/utilities/ai_native_support_tools/protocol_crafter.py`

### Component: Spellbook Core (Binding and Conjure)
Purpose:
- Provide the primary binding and conjure surface for the DGR.

Responsibilities:
- Manage configuration lifecycle and logger initialization.
- Register spells into local maps and spell-id caches.
- Maintain spell_id maps for O(1) spell_id resolution.
- Start transaction-backed SpellIndex mutation flows:
  `notch_spell(...)`, `add_spell_into_spellindex(...)`, and
  `remove_spell_from_spellindex(...)`.
- Run phase pipelines before conjure.
- Conjure exactly one Conduit per Spellbook instance.
- Provide SpellBinder fluent adapter.
- Scan user-supplied modules for `scan_bind` metadata and bind spells.

Inputs:
- User spell objects, configuration inputs, policy/automatic flags.
- Module objects passed to `scan(...)`.

Outputs:
- Spell IDs from `bind()`.
- Spell ID lists from `scan(...)`.
- SpellIndex mutation transaction results from `notch_spell(...)`,
  `add_spell_into_spellindex(...)`, and `remove_spell_from_spellindex(...)`.
- Conduit instances from `conjure()`.

Owned State:
- Spell registries (`_spells`, `_lookup_spells`, `_contracted_spells`).
- Spell_id maps (`_spells_by_id`, `_contracted_spells_by_id`).
- Spell-id caches (`_spell_ids`, `_contracted_spell_ids`).
- `_spell_validator`, `_spell_system_states`.
- `_configuration`, `_configuration_locked`.
- `_conduit`, `_conjured`, `_bind`.

Lifecycle/Cleanup:
- `SpellbookConfiguration` is validated/frozen before conjure.
- Cleanup is idempotent, unregisters local lineages from SpellSystemStates, and clears spells, configuration, validators, and logger. EVIDENCE: src/melder/aether/spellbook/spellbook.py:_cleanup_spells

Concurrency/Threading:
- Internal RLock guards most mutable operations.

Invariants/Guarantees:
- Conjure allowed once per Spellbook instance.
- `SpellbookConfiguration` must be frozen before Conduit creation.
- Existing-object spells are registered into Creations on conjure/bind.

Failure Modes:
- `SpellbookValidationError` when Phase 1-4 produces broken spells.
- RuntimeError for duplicate spell ids or lookup key collisions.
- `NotImplementedError` from the current SpellIndex multi-member seam methods
  (`_apply_notch`, `_apply_add_to_index`, `_apply_remove_from_index`) until
  that model lands.

Observability:
- Logs via SafeLogger in Spellbook and related components.

Extension Points:
- Conduit lifecycle hooks pulled from `SpellbookConfiguration`.
- Spell-level hooks (pre, activation, post).
- SpellBinder fluent binding surface.

Key Files (C1):
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/spellbinder.py`
- `src/melder/aether/spellbook/bind/scan.py`

### Component: Binding Pipeline (Bind, Spell, SpellIndex)
Purpose:
- Convert user objects into registered spell metadata with stable index identities.

Responsibilities:
- Build binding profiles via SpellExaminer.
- Compute fingerprints and create SpellIndex entries (the stable index that categorizes and targets spells).
- Determine canonical SpellType from binding profile + name/spellframe.
- Enforce Protocol and module binding constraints.
- Reject module and Protocol concrete binding targets while allowing class,
  callable, and existing-object bindings under profile/existence rules.
- Enforce existence constraints for method/lambda spells.
- Construct Spell objects with metadata and hooks.

Inputs:
- Spell object, spellframe, binding name, existence, permissions.

Outputs:
- Spell and SpellIndex instances.

Owned State:
- SpellIndex: immutable ULID index that holds the active selected spell; versions owned by MutationResearch.
- Spell: metadata, hooks, dependency placeholders, ownership fields.

Lifecycle/Cleanup:
- SpellIndex and Spell are Cleanable and null references on cleanup.

Concurrency/Threading:
- SpellIndex and Spell use RLock to protect mutation and cleanup.

Invariants/Guarantees:
- SpellIndex hash identity is stable and never changes.
- Protocols cannot be bound as concrete spells.
- Method/lambda spells must use `Existence.unique`.
- SpellType classification is stable for a given binding profile + metadata.
- Resolution style policy is maintained in
  `src/melder/aether/spellbook/resolution_style_matrix.py`, where
  `BINDING_FAMILY_POLICY` is canonical and SpellType rows are derived.

Failure Modes:
- TypeError for invalid binding targets or protocol misuse.
- ValueError for invalid bindings (existence rules, binding name conflicts).
- ValueError if method/lambda spells are bound with non-unique existence.

Observability:
- Errors surfaced via exceptions and Spellbook logger.

Extension Points:
- Binding profile strategies in SpellExaminer.

Key Files (C1):
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/bind/spell_index.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/aether/spellbook/spell_types/spell_types.py`
- `src/melder/aether/spellbook/resolution_style_matrix.py`

### Component: DI Descriptors and Contract Sockets
Purpose:
- Provide declarative DI placeholders and contract sockets for spell parameters.

Responsibilities:
- SpellMap encodes explicit DI intent and optional override payloads (dict/list/tuple).
- SpellMap supports concrete spell, spellframe, and frame-only forms and supplies canonical keys via SpellInputUtils.
- SpellContract declares late-bound sockets to be satisfied via conduit links.
- Legacy mutation-socket classifications are still recognized by validation,
  but no live `MutationContract` descriptor class remains in `src/melder`.
- ParameterDIShape classification drives Phase 1 socket interpretation.

Inputs:
- Spell/frame/binding identifiers and optional override payloads (dict/list/tuple).
- Legacy mutation-socket classification metadata interpreted through
  `ParameterDIShape.MUTATION_CONTRACT`.

Outputs:
- Canonical keys (frame_key, binding_key) and lookup triplets consumed by SpellCompiler and validators.

Owned State:
- SpellMap/SpellContract fields (spell, spellframe, binding_name, override).

Lifecycle/Cleanup:
- Cleanable descriptors; cleanup clears overrides and references.

Concurrency/Threading:
- No internal locks; immutable intent objects after construction.

Invariants/Guarantees:
- At least one of `spell` or `spellframe` must be provided.
- Binding names are normalized for case-insensitive matching and default to `__default__` when omitted.
- SpellMap preserves override payloads as provided; when `None`, no override is attached.
- SpellContract is intended for dynamic mode usage; legacy mutation-socket
  classifications are only preserved so validation can block them explicitly.

Failure Modes:
- ValueError when both `spell` and `spellframe` are None.
- `ContractProviderPresenceStrategy.validate` emits errors for SpellContract
  sockets in automatic mode; emits warnings for missing SpellContract providers;
  emits errors for invalid or ambiguous SpellContract defaults.
- `ContractProviderPresenceStrategy.validate` emits
  `MUTATION_CONTRACT_DISABLED` errors for legacy mutation-socket paths while
  mutation systems are on hold.

Observability:
- Exceptions on invalid construction; validation issues reported in Phase 4.

Extension Points:
- None (descriptor types are not intended for subclassing).

Key Files (C1):
- `src/melder/aether/conduit/meld/contracts/spell_map.py`
- `src/melder/aether/conduit/meld/contracts/spell_contract.py`
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`

### Component: Spellbook Configuration and System State
Purpose:
- Provide the validated, freezable `SpellbookConfiguration` surface for one
  spellbook/runtime context.

Responsibilities:
- Maintain configuration properties and hook registry.
- Validate required properties and freeze mutation.
- Provide configuration flags consumed by the logger provider path and AR
  eligibility rules (`system_state`, `ai_native_enabled`,
  `rift_enabled`).
- Control system_state (automatic vs dynamic).

Inputs:
- Property values and hook registrations.

Outputs:
- Frozen configuration and hook maps.

Owned State:
- `_properties`, `available_properties`, `_idempotent_keys`.
- `_hooks`.

Lifecycle/Cleanup:
- `freeze()` locks property mutations.
- Cleanup clears properties and hooks.

Concurrency/Threading:
- RLock guards property and hook mutations.

Invariants/Guarantees:
- Idempotent properties can be set once only.
- Frozen configuration cannot be modified.

Failure Modes:
- RuntimeError when cleaned/frozen configuration is mutated.
- ValueError when required properties are missing or semantically invalid.
- TypeError for invalid key/factory/hook input types.
- KeyError for unknown property lookup requests.

Observability:
- Exception-based reporting; no internal logging.

Extension Points:
- Additional properties and hook names.

Key Files (C1):
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `src/melder/aether/spellbook/configuration/system_state.py`

### Component: Aether Singleton (Global Runtime)
Purpose:
- Global singleton for all frames and shared registries.

Responsibilities:
- Create and manage AethericFrames.
- Bind configuration to frames.
- Own one optional Aether root configuration and expose
  create/builder/install/activate helpers that apply root logger policy into
  `AetherUtilitySystem`.
- Expose explicit post-boot logger control through `attach_logger(...)` and
  `enable_logging(...)`.
- Lazily host the process-wide `MutationResearch` singleton root above
  frame-local runtime state.
- Register conduits and spell lineages.
- Provide selected-spell registry for spell ids.
- Privately host singleton support roots for utility logging, crystallizer
  policy/activation, and Nexus AR behavior.

Inputs:
- Conduit objects, SpellIndex sets, `SpellbookConfiguration`, and optional
  `AetherConfiguration`.

Outputs:
- Frame-level registries and lookups plus applied root logger-provider policy
  in `AetherUtilitySystem`.

Owned State:
- `_aetheric_frames`, `_default_frame`, `_logger`, `_aether_utility_system`,
  `_crystallizer`, `_mutation_research`, `_nexus`.
- Singleton state (`_instance`, `_initialized`, `_lock`).

Lifecycle/Cleanup:
- `cleanup()` tears down frames and resets singleton state.

Concurrency/Threading:
- Class-level RLock guards singleton initialization and updates.

Invariants/Guarantees:
- One Aether instance per interpreter.
- Default frame exists when needed.

Failure Modes:
- ValueError for missing frames, duplicate registry entries, or not-found lookups.
- TypeError for invalid input types (e.g., non-string frame names).
- RuntimeError when singleton/frame registries are cleaned or unavailable.

Observability:
- Logs via SafeLogger.

Extension Points:
- Additional frame behaviors or registries.

Key Files (C1):
- `src/melder/aether/aether.py`
- `src/melder/aether/aether_configuration.py`
- `src/melder/aether/aether_configuration_builder.py`
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/mutation_research/mutation_research.py`

### Component: AethericFrame Services
Purpose:
- Per-frame container for conduits, registries, and control-plane services.

Responsibilities:
- Track conduits and spell registries.
- Maintain selected-spell registry.
- Own the frame-local DevopsInformationRegistry that mirrors topology and
  transaction state for reporting and strategy resolution.
- Provide ConduitCloud for named conduit lookup (dynamic mode).
- Provide ConduitCluster for auto-sharing roots.
- Own SpellSystemStates and DevOpsManager.
- Frames carry NO mutation-research dimension (owner ruling 2026-07-06, frame
  half unchanged). REVERSED for conduits/spellbooks 2026-07-12 (patch
  mutation_research_accessor_doors_2026_07_12): Spellbook and Conduit bind the
  Aether-hosted world root at init (crystallizer pattern) and expose it through
  one borrowed read-only `mutation_research` property each; research is still
  declared through that one world root and its `ResearchSet` surface only.

Inputs:
- Conduit objects and SpellIndex sets.

Outputs:
- Registry state and DevOps services.

Owned State:
- `_conduits`, `_spell_registry`, `_selected_spell_registry`.
- `_devops_information_registry`, `_conduit_cloud`, `_conduit_clusters`.
- `_spell_system_states`, `_dev_ops_manager`.
- `_configuration` (bound by Spellbook), `_frame_configuration`.

Lifecycle/Cleanup:
- Cleanup cascades to conduits, clusters, cloud, and control plane.

Concurrency/Threading:
- Frame-level RLock.

Invariants/Guarantees:
- One DevopsInformationRegistry, SpellSystemStates, and DevOpsManager per
  frame.

Failure Modes:
- Cleanup is best-effort; errors are suppressed to complete teardown.

Observability:
- Minimal internal logging; relies on caller logs.

Extension Points:
- Additional per-frame services.

Key Files (C1):
- `src/melder/aether/aetheric_frame/aetheric_frame.py`
- `src/melder/aether/aetheric_frame/conduit_cloud.py`
- `src/melder/aether/conduit/conduit_cluster.py`

### Component: Crystallizer Root, Persistence Record, And Module-World Surfaces
Purpose:
- Provide the hosted crystallizer policy root, the passive persistence RECORD
  (digital-twin custody of the configured world), and the retained/live module
  world surfaces used for crystallized spell loading and activation.

Responsibilities:
- Own configured/activated crystallizer policy at the hosted root.
- Act as the passive emission sink: structural units PUSH twins/custody at
  their own confirmation points; every sink verb is a NO-OP while inactive.
- Own the persistence RECORD (`PersistenceSystem`): named profiles with one
  ACTIVE emission target ("default" guaranteed) and a shared checkpoint
  ledger of `PersistenceCrystal` snapshot artifacts. Since the 2026-07-10
  decomposition the `CrystallizerCache` is owned by `AssetManagementSystem`,
  not the record (see the dated Subsystem Decomposition section below).
- Mirror spell lifecycle into the record: custody births at bind
  (active/staged locations), moves at park/promote, LEAVES at true removal;
  book/frame death evicts whole subtrees; Nexus/MR flip a
  `RecordedUnitState` switch (enabled/disabled/cleaned) with twins retained.
- Record index MEMBERSHIP as a first-class twin (`SpellIndexCrystal`:
  owner edge, selection, member SHAs) - re-snapshotted at bind/staging,
  notch (post-repoint), disposal, index moves, and transfer; evicted at
  index destruction.
- Record inter-conduit RELATIONSHIPS (`ContractCrystal`: both endpoints +
  per-side Detail/IndexDetail projections incl. permissions, direction,
  and live subscription heads) - emitted at link, re-snapshotted through
  the eight public contract verbs and the notch/destroy fan-outs, evicted
  at sever (`_remove_contract` choke point); `ConduitCrystal.link_targets`
  carries each conduit's OUTBOUND (initiated) link edges.
- Record CLUSTER topology (`ClusterCrystal`: cluster/frame identities,
  member conduit ids, elected leader, shared lineage entries) - emitted
  from the cluster's own state mutators via the configuration-precedent
  singleton pull (clusters have no crystallizer-bearing parent); evicted
  at live cluster deletion and swept by frame death.
- Seal incremental checkpoints: manual (`create_checkpoint`) and automatic
  (emit-driven cadence, `checkpoint_interval_minutes`), with FIFO ledger
  dropout at `max_persistence_crystals`.
- Sweep a mid-flight-activated live world into the record
  (`_catch_up_live_world`, shared-spellbook deduped).
- Build `SpellCrystal` manifests from live spells; the L3 crystal ALSO
  absorbs the bind signature (spell/binding/spellframe/existence/permissions
  names, spellbook parent edge, derived `rebindability`).
- Hold source-classification + checkpoint policy in
  `CrystallizerConfiguration` (`with_defaults()` = complete easy mode; only
  `user_source_root_paths` is hard-required).
- Use `SyntheticModule` as the live in-memory module embodiment; on park,
  optionally unpublish a spell's synthetic root module
  (`remove_inactive_synthmodules`, default False).

Inputs:
- Optional `CrystallizerConfiguration`.
- Twin emissions from configurations at their true-activation points
  (Spellbook/Frame/Aether/MR/Nexus configs) and from config-less objects
  (root Conduit at init; Spell custody at bind).
- Removal/lifecycle events from the owning teardown seams (spellbook
  `cleanup_and_remove_spell`/`cleanup_spell`/`_cleanup_components`, frame
  `cleanup`, Nexus `enable/disable/cleanup`, MR
  `activate/deactivate/cleanup`).
- Live `Spell` objects passed to `create_spell_crystal(...)`.

Outputs:
- Hosted crystallizer configured/activated state.
- The recorded world: profile describe dicts, custody lookups
  (`get_spell_crystal`), checkpoint ids/metadata (facades return names and
  dicts ONLY - the persistence model never escapes the root).
- `PersistenceCrystal.to_cached_item()`/`from_cached_item()` detached cache
  payloads (real round trip; storage itself is the persistence epic).
- `SpellCrystal` loader-facing manifests; `SyntheticModule` runtime modules.

Owned State:
- `Crystallizer`: `_configuration`, `_configured`, `_activated`, `_aether`,
  `_persistence_system`, `_asset_management_system`,
  `_crystal_loader_system` (the three post-decomposition children),
  `_checkpoint_interval_seconds`, `_last_automatic_checkpoint_monotonic`.
- `PersistenceSystem`: `_profiles_by_name`, `_active_profile_name`,
  `_checkpoint_crystals_by_id` (ULID-keyed; lexicographic = chronological),
  `_max_persistence_crystals`. No cache slot since the S3 decomposition:
  disk custody lives on `AssetManagementSystem`.
- `PersistenceProfile`: flat level maps (frames by name, books/conduits by
  id, spell custody split active/inactive by spell SHA), three singleton
  twins, `_nexus_state`/`_mutation_research_state` switches, the emission
  journal + checkpoint mark.
- Twin family (pure-data, `describe()`-detached): `AetherCrystal`,
  `AethericFrameCrystal`, `SpellbookCrystal`, `ConduitCrystal`,
  `NexusCrystal`, `MutationResearchCrystal`, `SpellCrystal` (L3; the whole
  family lives at package level in `crystallizer/crystals/` since the S2
  move).

Lifecycle/Cleanup:
- `Crystallizer` is a hosted singleton root owned by `Aether`; frames are
  cleaned BEFORE it in full teardown, so eviction seams always fire against
  a live record (or skip via the lifecycle-evidenced gates).
- Replace-on-emit: a displaced twin/custody crystal is CLEANED; runtime
  holders must fetch fresh per use (never retain long-lived references).
- `clear_profile` resets one profile's content, journal, mark, and state
  switches in place; `delete_profile` guards "default", falls selection
  back, and its sealed ledger crystals SURVIVE deletion.
- `PersistenceCrystal` wipe = cleanup (reload from cache is the recovery).

Concurrency/Threading:
- Instance `RLock` discipline at every level; one-way lock order
  (spellbook/frame/nexus/MR -> crystallizer -> persistence system ->
  profile); the cadence ticker stamps under the crystallizer lock and seals
  outside it (stamp advances BEFORE sealing - no hot-loop on failure).
- `SyntheticModule` uses registry locking for importlib-facing paths.

Invariants/Guarantees:
- The crystallizer root starts unconfigured and inactive; every sink verb
  and profile/checkpoint facade requires activation.
- The record is DYNAMIC-LANE positioned: bind custody is gated
  `activated AND _is_dynamic_posture()`; automatic frames emit nothing;
  crystallizer-off worlds are byte-identical (R-A covenant).
- The conjure configuration-discipline guard refuses a dynamic conjure over
  binds that ran while the spellbook configuration was mutable (recorded
  worlds are never born config-incoherent).
- Runtime ULIDs are emitted, never rehydrated, and normalized out of seal
  fingerprints (restore mints fresh identities via translation map).
- Aether/Crystallizer have NO state switch by design: the record dies with
  them and could never report their teardown.

Failure Modes:
- `Crystallizer.configure(...)` rejects reconfiguration while active.
- `create_spell_crystal(...)`/`get_spell_crystal(...)`/facades raise when
  not activated; unknown profile/checkpoint names raise `KeyError`;
  `emit(...)` of an unsupported twin type raises `TypeError`.
- `load_checkpoint` is LIVE (RestoreEngine, 2026-07-07) and MEDIATED since
  the 2026-07-10 decomposition: it routes through
  `CrystalLoaderSystem`/`LoadAdmission` with blocker-refusing admission
  (see the dated sections below). `CrystallizerCache` is REAL and
  asset-owned: atomic JSON per checkpoint ULID under
  `__crystallizer_cache__` ({profile}/ scoped); misses raise a teach-grade
  `KeyError`; `flush_checkpoint(id|None=all)` / `reload_cached_checkpoint`
  (insert-if-absent, no retention on reload) /
  `list_cached_checkpoint_ids` remain the byte-compatible facade lane; the
  user-DB seam is the asset-owned `ExternalPersistenceManager`.

Observability:
- `describe_profile`/`describe_checkpoint`/`list_*` facades expose the whole
  record as detached dicts, ids, and counts.
- Checkpoint payload special-cases keep replay truthful: removal tombstones
  (`spell_removed`/`spellbook_removed`/`frame_removed`), activity
  current-truth, and state-switch values.

Extension Points:
- Storage adapter behind `CrystallizerCache` (persistence epic P1-P6).
- Restore engine consuming checkpoint replay (bootstrap epic).
- Loader chain / dependency-ordered unfold (parent epic M3).

Key Files (C1):
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration_builder.py`
- `src/melder/crystallizer/persistence/persistence_system.py`
- `src/melder/crystallizer/persistence/persistence_profile.py`
- `src/melder/crystallizer/persistence/persistence_crystal.py`
- `src/melder/crystallizer/asset_management/asset_management_system.py`
- `src/melder/crystallizer/asset_management/crystallizer_cache.py`
- `src/melder/crystallizer/crystal_loader_system/` (crystal_loader_system.py,
  load_admission.py, load_plan.py, restore_engine.py, bootstrap_loader.py)
- `src/melder/crystallizer/crystal_analysis/` (crystal_analyzer.py,
  crystal_analysis_result.py, custody/, strategies/, preflight/)
- `src/melder/crystallizer/crystals/recorded_unit_state.py`
- `src/melder/crystallizer/crystals/spell_crystal.py` (package-level since
  the S2 move; carrier-slimmed in S1)
- `src/melder/crystallizer/crystals/` (aether / aetheric_frame /
  spellbook / conduit / nexus / mutation_research twins, plus
  `spell_index_crystal.py` membership map, `contract_crystal.py`
  relationship map, and `cluster_crystal.py` cluster map)
- `src/melder/crystallizer/synthetic_module.py`

### Component: AR Runtime Surface (Nexus, Rift, RiftSpace)
Purpose:
- Provide the live AR-facing access layer into the Melder-owned object world.

Responsibilities:
- Expose `Nexus` as the public singleton root for Rift-domain behavior.
- Own process-wide AR configuration, Rift registry state, and Nexus-managed
  frame policy.
- Own `FrameDescriptorManager` for frame-scoped descriptors, passive
  frame/conduit/spell publication, and Nexus-managed frame-record state.
- Own `FrameACLManager` for frame-local ACL container creation, profile
  registries, chain access, and frame-level ACL change fan-out.
- Surface `NexusFrameBuilder` from `NexusFrameManager.begin(...)` so Nexus
  frame authoring is an explicit builder-owned flow instead of manager-only
  prose.
- Enforce process-wide Rift creation/direct-access policy plus target-frame,
  Nexus-frame, and active-Rift budget checks.
- Compile frame-scoped projection sets from descriptor truth plus selected ACL
  family names.
- Fan out ACL-driven projection refresh to the impacted live Rifts for one
  changed-frame batch, with the single-frame ACL callback delegating to the
  same batch path.
- Create and register bare `Rift` objects with finalized per-Rift config snapshots.
- Program one primary room from `RiftConfiguration.space_type`.
- Enforce Nexus frame topology rules (`single`, `indexed`,
  `one_per_workspace`) and target-frame eligibility for static vs codegen AR.
- Keep Nexus-frame creation explicit rather than auto-provisioned.
- Route Nexus-facing managed creation through the normal public Spellbook API
  instead of direct frame-first config injection.
- Return rooted conduits from Nexus/Rift-facing managed creation and recovery,
  not frame objects.
- Keep `create_*` strict:
  - creation raises when the target managed frame already exists
  - recovery stays on `get_*`
- Constrain raw `NexusFrameManager` creation by mode:
  - `single`
    - only the canonical shared frame name may be created directly
  - `indexed`
    - explicit named direct creation remains allowed
  - `one_per_workspace`
    - raw direct manager creation is rejected because the path carries no Rift
      owner identity
- Make rooted Nexus creation defaulted and caller-nameable:
  - root conduit is created by default
  - caller may override the root conduit name
  - current default root conduit name is `"root"`
- Let `Rift` own exactly one primary room, explicit frame targeting,
  Nexus-frame access, current projection registry state, and projection-driven
  asset application.
- Let `Rift` own per-frame `FrameLinkContract` state plus per-Rift refresh
  orchestration over that contract set and current projection-driven asset
  refresh.
- Let `RiftSpace` own room-local metadata, attached durable asset state
  (Rift-backed `FrameViewer`, workstation, command system), one room-local
  event system, and one room-local memory system.
- Let `CodegenRiftSpace` own one internal `CodegenSystem` and attach it to the
  room-owned `CodegenCommandSystem` during room initialization.
- Let `RiftSpace` compose one room-local `Workstation`, one room-local
  `CommandSystem`, one room-local event system, and one room-local memory
  system above the descriptor/viewer path.
- Let `RiftSpace` build the durable Rift-backed viewer asset during room init.
- Let static rooms host `StaticFrameViewer` directly so the spell-facing viewer
  surface stays live-only while still reading current Rift projection truth.

Inputs:
- Nexus configuration and Rift configuration/profile templates.
- Rift creation requests and later explicit frame-target requests.
- per-frame ACL family changes from frame-local ACL containers.
- Static, capability, or codegen room posture.

Outputs:
- Live `Rift` objects.
- Programmed primary room instances.
- frame-scoped `FrameProjectionSet` objects for targeted frames.
- Nexus-managed frame references and frame-name listings.
- Registered room/workspace objects.

Owned State:
- `Nexus`: `_configuration`, `_configured`, `_enabled`, `_rifts_by_id`,
  `_rift_ids_by_name`, `_rift_profiles_by_name`,
  `_next_default_rift_number`, `_frame_manager`,
  `_rift_gate_controller`, `_target_frame_ref_counts`,
  `_frame_descriptor_manager`, and `_frame_acl_manager`.
- `Rift`: config snapshot, one owned `_space`, `_is_registered`,
  `_is_active`, local metadata, one `FrameLinkContract` per engaged target
  frame carrying per-frame ACL family selection, one `RiftGate`, and the
  current `FrameProjectionSet` registry.
- `RiftSpace`: room id/name/kind, room metadata, attached `FrameViewer`, one
  room-local event system, one room-local memory system, workstation, and
  command system.
- `CodegenRiftSpace`: the base room-owned state above, plus one owned
  `_codegen_system`.

Lifecycle/Cleanup:
- `Nexus` is singleton, boot-hosted by `Aether`, and may remain inert until
  configured/enabled.
- `Rift` cleanup clears the owned space, config snapshot, `RiftGate`,
  frame-link contracts, projection registry, metadata, and then logger state.
- `RiftSpace` cleanup clears room-local state and its event system.

Concurrency/Threading:
- `Nexus` and `Rift` use per-instance `RLock` for cleanup and multi-step
  state mutation.
- `RiftSpace` now owns an `RLock` and uses it for grouped room mutation and
  cleanup.

Invariants/Guarantees:
- `Nexus` is the only intended public root for Rift-domain work.
- `Aether` still owns actual `AethericFrame` objects; `Nexus` owns policy and
  frame records only.
- One frame-local ACL container exists per frame when the ACL subsystem is
  provisioned.
- Each frame-local ACL container now owns separate named version chains for:
  - view
  - command
  - codegen
- `Rift` frame-link ACL selection is same-name and fixed per frame link:
  `view`, `command`, and `codegen` all resolve to the attached `frame_name`.
- When the frame-name contract does not yet exist, `Rift.create_frame_link(...)`
  materializes that same-name contract from the current default ACL snapshot
  before refreshing projections.
- `single` mode is behaviorally shared across Rifts even though the enum name
  still uses the older `single` label.
- Bare Rift creation does not require an initial target frame.
- `Rift.create_frame_link(...)` requires descriptor truth before the target frame is
  accepted into the frame contract or the viewer path.
- `Nexus` does not build live viewers anymore.
- `RiftSpace` no longer manages projection state directly.
- `Rift` applies projection state to the hosted viewer and command assets.
- `FrameViewer` no longer stores a local projection registry or default-frame
  state; it reads current view projections from `Rift` on demand.
- `ViewMultiFrame`, `ViewFrame`, `ViewConduit`, and `ViewSpell` are helper
  surfaces built on demand over the current viewer/Rift contract instead of a
  profile-owned or cached-bound helper system.
- Codegen AR requires `rift_enabled=True`,
  `ai_native_enabled=True`, and `system_state=dynamic`.
- Current room-mode matrix:
  - `static`
    - static viewer overlay
    - weak-by-default workstation
    - no topology mutation
    - no direct create-path spell activation
    - live-only spell-facing retrieval and status helpers
  - `capability`
    - broad manual runtime/object access
    - strong-by-default workstation
    - no codegen
    - lower Melder frame truth still wins
  - `codegen`
    - keeps a selected runtime-helper subset rather than capability parity
    - owns one internal `CodegenSystem` under `CodegenRiftSpace`
    - routes public validate/execute requests through `CodegenCommandSystem`
      into that engine
    - emits full-source codegen room-memory records for top-level validation
      and execution actions
- `Workstation` owns separate strong/weak object, attribute, and method stores
  plus one active target binding.
- `CommandSystem` is the shared room-local command base for infrastructure,
  shared runtime/query helpers, and workstation-target execution.
- `CapabilityCommandSystem` owns conduit discovery, the link/contract-topology
  helper surface, the broad manual-runtime topology surface, and direct spell-
  activation/reuse helpers.
- `StaticCommandSystem` owns live-only spell retrieval, reuse-only spell
  activation, and static spell-status helpers.
- `CodegenCommandSystem` keeps the selected slim runtime-helper surface,
  attaches one room-owned `CodegenSystem`, delegates
  `validate_codegen(...)` / `execute_codegen(...)` into that engine, and emits
  full-source codegen memory records.
- `CodegenSystem` owns the internal transaction, validation, namespace,
  compile/exec, and monitor collaborators beneath the room command facade.
- When the room-local memory system has registered callbacks, one top-level
  successful public command call emits one `IRiftMemory` record through that
  system.
- ACL-driven projection refresh is config-backed:
  - `projection_refresh_gate_enabled`
  - `projection_refresh_gate_timeout_seconds`
  - `projection_refresh_gate_poll_interval_seconds`
  with default-on RiftGate drain behavior around the refresh.

Failure Modes:
- Unconfigured or disabled `Nexus` operations fail fast.
- Rift creation or direct-access requests fail when Nexus policy gates,
  required tokens, or configured budgets reject them.
- `Rift` creation fails when configuration is invalid.
- `Rift.create_frame_link(...)` fails when target-frame eligibility rules are not met.
- `Rift.create_frame_link(...)` fails when descriptor truth is missing for the
  requested frame.
- Requested Nexus frame access fails when the request violates the current
  frame-mode policy.
- `Rift.on_nexus_frame_disposed(...)` is still a placeholder seam and does not
  yet push a real Rift-level event orchestration layer.

Observability:
- `Nexus` and `Rift` log lifecycle events through the provider-based
  `SafeLogger` path.

Extension Points:
- Rift profile templates on `Nexus`.
- Future Rift-level event orchestration layer.
- Future richer workspace/context contract above `RiftSpace`.

Key Files (C1):
- `src/melder/nexus/nexus.py`
- `src/melder/nexus/frame_descriptor_manager.py`
- `src/melder/nexus/frame_acl_manager.py`
- `src/melder/nexus/nexus_frame_manager.py`
- `src/melder/nexus/nexus_frame_builder.py`
- `src/melder/nexus/rift/frame_link/frame_link_contract.py`
- `src/melder/nexus/rift/frame_link/frame_link.py`
- `src/melder/nexus/rift/rift_gate/rift_gate.py`
- `src/melder/nexus/rift/rift_gate_controller/rift_gate_controller.py`
- `src/melder/nexus/rift/frame_viewer/frame_viewer.py`
- `src/melder/nexus/rift/frame_viewer/view_multiframe.py`
- `src/melder/nexus/rift/frame_viewer/view_frame.py`
- `src/melder/nexus/rift/frame_viewer/view_conduit.py`
- `src/melder/nexus/rift/frame_viewer/view_spell.py`
- `src/melder/nexus/rift/rift.py`
- `src/melder/nexus/rift/frame_viewer/static_frame_viewer.py`
- `src/melder/nexus/rift/rift_space/rift_space.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event_system.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event.py`
- `src/melder/nexus/rift/rift_space/static_rift_space.py`
- `src/melder/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/nexus/rift/rift_space/capability_rift_space.py`
- `src/melder/nexus/rift/rift_space/workstation.py`
- `src/melder/nexus/rift/rift_space/memory_system/rift_memory_system.py`
- `src/melder/nexus/rift/rift_space/memory_system/rift_memory.py`
- `src/melder/nexus/rift/command_system/command_system.py`
- `src/melder/nexus/rift/command_system/static_command_system.py`
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `src/melder/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/nexus/acl/builder/frame_acl_builder.py`
- `src/melder/nexus/rift/codegen_system/codegen_transaction_context.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validator.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validation_result.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validation_reporter.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_compiler.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_executor.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_execution_result.py`
- `src/melder/nexus/rift/codegen_system/observability/codegen_monitor.py`
- `src/melder/nexus/rift/codegen_system/observability/codegen_event_publisher.py`
- `src/melder/nexus/configuration/nexus_frame_mode.py`
- `src/melder/nexus/configuration/rift_space_type.py`

### Component: Codegen Internal Engine
Purpose:
- Provide the room-owned internal codegen runtime beneath the public command
  facade.

Responsibilities:
- Build per-call `CodegenTransactionContext` objects.
- Resolve optional `CodegenProjection` state from the owning `Rift`.
- Build default namespace configuration and live codegen namespaces.
- Validate generated Python before execution.
- Compile accepted code and execute it against the built namespace.
- Publish validation/execution lifecycle events through the room event system.

Inputs:
- generated Python `code`
- target `frame_name`
- room-owned `Rift` and `CodegenRiftSpace`

Outputs:
- `ICodegenValidationResult`
- `ICodegenExecutionResult`
- shared `ICodegenTransactionContext`
- public validation payloads through the reporter

Owned State:
- `CodegenSystem`: `_validator`, `_validation_reporter`,
  `_namespace_builder`, `_compiler`, `_executor`, `_monitor`
- `CodegenTransactionContext`: frame name, code, code hash, optional
  projection, namespace configuration, optional namespace, and metadata

Lifecycle/Cleanup:
- `CodegenSystem` is owned by `CodegenRiftSpace`.
- cleanup is idempotent, lock-disciplined, and cascades into the owned
  monitor before references are nulled.

Concurrency/Threading:
- `CodegenSystem` uses an instance `RLock` around validate/execute flows.

Invariants/Guarantees:
- validation runs before execution on the execute path
- namespace building happens only after accepted validation
- room-memory emission stays on `CodegenCommandSystem`, not the engine root

Failure Modes:
- empty code or frame names raise `ValueError`
- rejected validation returns a validation-failed execution result without
  compile/exec
- missing projection support degrades to `None` projection instead of failing
  transaction construction

Observability:
- `CodegenMonitor` publishes validation/execution lifecycle events through the
  room event system

Extension Points:
- richer namespace strategies
- additional validation strategies
- expanded monitor/reporter policy

Key Files (C1):
- `src/melder/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/nexus/rift/codegen_system/codegen_transaction_context.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validator.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validation_result.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validation_reporter.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_compiler.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_executor.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_execution_result.py`
- `src/melder/nexus/rift/codegen_system/observability/codegen_monitor.py`
- `src/melder/nexus/rift/codegen_system/observability/codegen_event_publisher.py`

### Component: Nexus Descriptor And ACL Managers
Purpose:
- Own the frame-scoped descriptor publication and ACL registry layers beneath
  the public `Nexus` facade.

Responsibilities:
- `FrameDescriptorManager` owns `frame_name -> FrameDescriptor`.
- Refresh frame posture and frame-handle cache before passive publication.
- Publish and remove frame, conduit, and spell records.
- Own Nexus-managed frame-record lookup, creation, enumeration, and counts.
- `FrameACLManager` owns `frame_name -> FrameACLContainer`.
- Create frame-local ACL containers on demand, expose profile registries, and
  propagate frame-level ACL change callbacks back through `Nexus`.
- `FrameACLContainer` owns one `FrameACLBuilder`, and that builder owns the
  active family draft workflow for view/command/codegen revisions.

Inputs:
- Frame names, Aether frame handles, Spellbook/Conduit/Spell publication
  requests, and frame-scoped ACL selection/change requests.

Outputs:
- Updated `FrameDescriptor` aggregates, published canonical records, and
  frame-local ACL containers.

Owned State:
- `FrameDescriptorManager`: `_frame_descriptors_by_name`, hidden Aether
  reference, posture cache, and publication helpers.
- `FrameACLManager`: `_frame_acl_containers_by_name`,
  `_frame_acl_profiles_by_name`, and one manager-owned
  `FrameACLProfileBuilder`.

Lifecycle/Cleanup:
- Both managers are owned by `Nexus`.
- Cleanup is idempotent and cascades into owned descriptors, containers, and
  profile registries before dropping manager-owned mappings.

Concurrency/Threading:
- Both managers serialize multi-step mutation through one instance `RLock`.

Invariants/Guarantees:
- `FrameDescriptorManager` is the sole owner of the descriptor registry.
- `FrameACLManager` is the sole owner of the frame ACL container registry.
- `Nexus` remains the public facade; frame-scoped mutation lives behind the
  managers.

Failure Modes:
- Publication short-circuits when a frame is not Rift-enabled/publishable.
- Required frame/container lookups raise when callers target missing state.

Observability:
- Runtime effects are visible through the descriptor and ACL surfaces consumed
  by `Rift` and the viewer path.

Extension Points:
- Wider descriptor payload families.
- Additional frame-local ACL profile families and compiled access projections.

Key Files (C1):
- `src/melder/nexus/frame_descriptor_manager.py`
- `src/melder/nexus/frame_acl_manager.py`
- `src/melder/nexus/frame_descriptor/`
- `src/melder/nexus/acl/`

### Component: RiftSpace Workstation And Command Surface
Purpose:
- Provide the room-local binding canvas and mediated command surface above the
  descriptor/viewer path.

Responsibilities:
- `Workstation` stores strong/weak object, attribute, and method bindings by
  name.
- Track one active target binding and support target cleanup/call behavior.
- Emit weak-binding collection events back into the owning room event system.
- `CommandSystem` resolves selected viewer targets into records or runtime
  objects subject to room-mode and compiled ACL rules.
- Expose shared spell lookup, shared runtime/query helpers, and
  workstation-target execution helpers.
- Leave room-only topology mutation, room-only link/contract-topology
  traversal, room-only spell activation/reuse commands, and room-only conduit
  discovery to room-specific command subclasses.
- `CodegenCommandSystem` owns the room-facing codegen validate/execute seams
  and delegates real validation/execution work into the attached
  `CodegenSystem`.
- Bind command results back into the workstation when requested.
- Emit one `IRiftMemory` record for one successful top-level public command
  call when the room-local memory system has registered callbacks.
- Emit full-source codegen memory metadata for top-level codegen validation and
  execution actions.
- Let static/capability/codegen subclasses narrow or widen the shared command
  posture without forking the whole API surface.

Inputs:
- Viewer-projected records and frame names.
- Room-local workstation bindings and optional result-binding requests.

Outputs:
- Retrieved records/runtime objects, runtime mutations, status/query payloads,
  and optional workstation-bound command results.

Owned State:
- `Workstation`: strong/weak binding stores, active target name/store,
  default weak-ref posture, and optional event publisher.
- `CommandSystem`: owning room reference, workstation reference, one stable
  command-system id, and one nested public-command call-depth counter used to
  suppress duplicate memory emission from internal command-to-command calls.
- `CodegenCommandSystem`: the base command-system state above plus one
  attached `_codegen_system` reference.

Lifecycle/Cleanup:
- Both objects are owned by `RiftSpace`.
- `Workstation.cleanup()` clears binding stores but does not cleanup stored
  objects automatically.
- `CommandSystem.cleanup()` drops only command-system-owned references.

Concurrency/Threading:
- `Workstation` and `CommandSystem` each use an instance `RLock`.

Invariants/Guarantees:
- `Workstation` never fabricates new runtime objects; it stores room-local
  bindings only.
- `CommandSystem` gates runtime access before bind and leaves already-bound
  workstation objects outside post-bind ACL policing.
- `StaticCommandSystem` denies topology mutation and direct `meld(...)`.
- `CapabilityCommandSystem` now owns the broad manual-runtime posture, while
  `CodegenCommandSystem` owns a selected slim runtime-helper posture plus the
  room-facing delegation boundary into `CodegenSystem` instead of inheriting
  the full capability surface.
- Research surface (2026-07-11): `CodegenCommandSystem` owns the FULL
  `research_*` command family (seven record reads: walk/history/heads/
  residency/diff [structural default]/campaign_view/recent [the
  cold-landing newest-window read; group_history additionally takes a
  campaign= narrow - the WHERE x WHEN join]; five organization
  verbs: create_lane [now typed]/attach/detach/join/archive; two campaign
  verbs: set/clear; nine foresight commands - see next bullet; three
  synthesis verbs: research_synthesize/research_stage_ancestry/
  research_clear_staged_ancestry; eight composition commands
  (GroupedResearchNode ruling 2026-07-11): research_group_register/
  research_group_recompose organization + research_group_view/
  research_group_diff/research_group_impact/research_group_footprint/
  research_group_drift/research_group_history reads - 34 commands
  total); `CapabilityCommandSystem` owns the twenty-one reads ONLY
  (seven record reads + eight foresight reads + six composition reads);
  static rooms own none. All ride
  `_entered_command_action` + the room lock, and reach the Aether-hosted
  MutationResearch root through `_require_live_mutation_research()` - a
  non-constructing peek that refuses teach-grade while research is absent
  or inactive. DISCOVERABILITY LAW (2026-07-11): the full research family
  is ADVERTISED in both rooms' `list_supported_command_methods`
  presentation tuples (an agent asking a room "what can you do" learns
  the research surface exists; the earlier invisible-precedent was a
  mistake and is corrected).
- Foresight surface (2026-07-11, agent QoL kit): `research_source`
  (recorded module text first, live-disk fallback with drift marker,
  honest text_unavailable), `research_impact` (blast radius joined with
  research residency AND lifted to composition grain - every radius names
  the current GroupedResearchNode subsystems it touches under
  `affected_compositions`; exactly one center per call), `research_module_graph`
  (walkable module world: deps, local reverse edges, exports, load order),
  `research_source_drift` (full recorded-vs-disk report), the crystal-well
  reads (owner ruling 2026-07-11, units-and-scales 4.1): `research_module`
  (the module DOSSIER - text labeled synthetic/user/live_disk,
  fingerprint, path, deps both ways, export surface, drift in ONE call),
  `research_part` (one named top-level function/class's text + span +
  carrying module; present-tense resolution), `research_parts` (the
  class-code INVENTORY: every top-level part per module with full text -
  no names needed up front), `research_part_diff`
  (unified text diff of one named part between two versions - RECORDED
  material only per the comparison law - carrying its module-grain blast
  radius automatically), and - CODEGEN ROOMS ONLY, it takes code -
  `research_preview` (the read-only candidate mock: AST defines/import
  roots, would-be source + structural diff via
  `DiffEngine.diff_materials`, would-be radius, plus an optional
  frame-scoped `validate_codegen` verdict when `frame_name` is given;
  nothing executes, binds, or records). Custody-unavailable refuses LOUD
  (RuntimeError) on the reads; preview parse errors answer honestly.
  COMPARISON LAWS (2026-07-11): diff material drinks BOTH recorded
  carriers (synthetic first, user-retained fills gaps - string AND
  structural diffs speak the FULL module, physical or synthetic) and
  NEVER the live disk (both sides would read the same present-day file
  and lie about both versions); impact stays module-grain (a part's
  honest radius IS its module's radius). GRAIN CHOICE (owner ruling
  2026-07-11): the whole-version diff offers THREE registered strategies
  and the agent picks - "source" (whole-module text), "structural" (AST
  shape reports), "parts" (PartDiffStrategy: per-class/function code -
  added/removed parts WITH full text, changed parts as unified diffs,
  module-body residue compared as its own region); preview_candidate
  composes all three.

Failure Modes:
- Strong/weak binding misuse raises instead of silently degrading storage mode.
- Denied runtime actions fail fast.

Observability:
- Weak-binding collection can publish room-local events.
- Command methods surface explicit errors for denied or ambiguous access.

Extension Points:
- Additional room-local command helpers.
- Richer event-queue consumers and room-local automation policies.

Key Files (C1):
- `src/melder/nexus/rift/rift_space/rift_space.py`
- `src/melder/nexus/rift/rift_space/workstation.py`
- `src/melder/nexus/rift/command_system/command_system.py`
- `src/melder/nexus/rift/command_system/static_command_system.py`
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `src/melder/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event_system.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event.py`

### Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Execution scope for resolving spells and managing object lifecycles.

Responsibilities:
- Register normal conduits into Aether and ConduitCloud.
- Own one `ConduitCreations` registry for conduit/root-scoped live objects.
- Own one `ConduitMeld` front door for conduit-scoped runtime resolution.
- Own one `CreationGate` registered through the frame-owned
  `CreationGateController`.
- Own one `SpellSpacePool` for request-local spellspace surfaces and one
  `ConduitPool` for lesser-conduit reuse.
- Manage ConduitWard and hook wiring.
- Create lesser conduits and manage lineage trees.
- Upgrade lesser conduits to normal in dynamic mode by preserving/rebinding the
  current Creations manager and rewiring Meld/ConduitWard state.
- Manage peer link/sever flows and fire conduit hooks on success.
- Transfer spell ownership between conduits in dynamic mode.
- Gate meld execution per conduit via `CreationGate` and register gates in the
  lineage `CreationGateController` for bulk enable/disable and close-and-drain.

Inputs:
- Spellbook, `SpellbookConfiguration`, policy and dynamic flags, optional logger.
- Optional name/hooks for `upgrade_to_normal`.
- Target conduit for `link(...)` / `sever_link(...)`.
- Target conduit and transfer options for `transfer_spell_ownership(...)`.

Outputs:
- Resolved instances via `meld()`.
- Boolean link/sever results.
- Ownership transfer preflight summary (dict).

Owned State:
- `_creations` (`ConduitCreations`), `_meld` (`ConduitMeld`),
  `_conduit_ward`, `_conduit_hooks`.
- `_meld_gate` (per-conduit gate) and `_meld_gate_controller` registry.
- `_spellspace_stack`, `_spellspace_registry`, `_spellspace_pool`,
  `_conduit_pool`.
- Conduit metadata (`_id`, `_name`, `_automatic`, `_aetheric_frame`).

Lifecycle/Cleanup:
- Cleanup fires hooks, tears down Meld, ConduitWard, Creations, then logger.
- Upgrade rewires Creations/Meld and converts ConduitWard lineage state.

Concurrency/Threading:
- Internal RLock guards conduit operations.
- `CreationGate` uses an internal RLock and Event to block/unblock meld calls
  and a per-gate ticket deque for active meld tracking and close-and-drain.

Invariants/Guarantees:
- Normal conduits register with Aether; lesser conduits do not.
- Lesser conduits cannot have names.
- Existing-object spells must be Existence.unique when registered into Creations.
- `upgrade_to_normal` requires dynamic mode and a lesser conduit state.
- `link` and `sever_link` are only allowed in dynamic mode.
- `upgrade_to_normal` rewires Meld to the currently owned Creations manager.
- Ownership transfer is only allowed in dynamic mode.
- The caller-facing meld door for a conduit is always `ConduitMeld`.
- Spellspace-local request work is routed through `SpellSpaceMeld`, not
  through the conduit front door.

Failure Modes:
- RuntimeError for invalid policies, missing root conduits, or illegal operations.
- RuntimeError if `upgrade_to_normal` is called in non-dynamic mode or on a non-lesser conduit.
- RuntimeError if `link`/`sever_link` is called in non-dynamic mode.
- TypeError if `link` target is not an `IConduit`.
- RuntimeError if `link` target lacks a valid creation context.
- RuntimeError if `transfer_spell_ownership` is called in non-dynamic mode.
- Meld calls block while the local `CreationGate` is disabled.

Observability:
- Logs via SafeLogger.

Extension Points:
- Per-conduit hooks via `SpellbookConfiguration`.
- Dynamic policies and ConduitCloud registration.

Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/synchronization/creation_gate.py`
- `src/melder/utilities/synchronization/creation_gate_controller.py`

### Component: ConduitWard and Contracts
Purpose:
- Control-plane manager for conduit contracts and lineage links.

Responsibilities:
- Maintain contract graph and linking indices.
- Manage parent/child (lesser) lineage tree.
- Apply policy rules for contract creation.
- Update Spellbook contracted maps when links change.
- Convert lesser lineage state to normal during conduit upgrade.

Inputs:
- Conduit objects, policies, and SpellIndex sets.

Outputs:
- Contract state and contracted spell visibility.

Owned State:
- `_contracts`, `_initiated_index`, `_received_index`.
- `_lesser_conduits`, `_parent_conduit`, `_root_conduit`.
- `_policy` and `_dynamic` flags.

Lifecycle/Cleanup:
- Cleanup severs contracts and cleans lesser conduits.

Concurrency/Threading:
- Internal RLock; contract creation uses ordered locking (per docstring).

Invariants/Guarantees:
- Ward owns and cleans all lesser conduits it links.
- Peer links require dynamic mode and normal conduits.
- `_convert_to_normal_conduit` requires a parent link and no children.

Failure Modes:
- RuntimeError for invalid policy or state transitions.
- RuntimeError for self-linking, linking lesser conduits, or policy-gated links.
- RuntimeError if `_sever_link` finds no contract to remove.

Observability:
- Logs via SafeLogger.

Extension Points:
- Policies and contract detail types.

Key Files (C1):
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/conduit_ward/policies/policies.py`
- `src/melder/aether/conduit/conduit_ward/permissions/permissions.py`

### Component: Creations and SpellSpace
Purpose:
- Instance lifecycle registry for Conduits and scoped spellspaces.

Responsibilities:
- Track live objects in `_creations`.
- Track cleanup-only disposal metadata in `_disposable_creations`.
- Store unique entries as `spell_id -> object`.
- Store many entries as `spell_id -> list[object]`.
- Dispose tracked entries during cleanup using only the detached disposable
  metadata registry.
- Provide SpellSpace scoping for unique_per_spell_space.
- `ConduitCreations` acts as the conduit/root specialization seam over the
  generic scoped `Creations` store.
- Preserve/rebind the active creations manager during lesser-to-normal upgrade.

Inputs:
- Instances created by Meld.

Outputs:
- Stored instances and cleanup errors (ExceptionGroup).

Owned State:
- `_creations`
- `_disposable_creations`
- owner/scope ids

Lifecycle/Cleanup:
- Cleanup detaches both registries first, disposes through
  `_disposable_creations`, then drops the live field surface.
- SpellSpace cleanup resets scope and unregisters from owner.

Concurrency/Threading:
- RLock guarding instance maps.

Invariants/Guarantees:
- Creations is used by both normal and lesser conduits; behavior is driven by
  conduit state and root-lineage wiring.
- `ConduitCreations` uses the conduit id as both owner id and scope id.
- Disposal uses declared per-object method-name lists and does not wrap the
  live runtime store in a second `Creation.value` carrier.

Failure Modes:
- ExceptionGroup raised if any disposal errors occur.
- SpellSpaceScopeError if scope is misused.
- RuntimeError if conduit state is missing during Creations initialization.

Observability:
- Logs errors during cleanup and disposal attempts.

Extension Points:
- Disposal method names in `SpellbookConfiguration`.

Key Files (C1):
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`

### Component: Meld Resolution Runtime
Purpose:
- Resolve and instantiate spells within a Conduit.

Responsibilities:
- Provide a shared abstract `Meld` core for lookup, validation, lazy
  recompilation, and creation-context dispatch.
- `ConduitMeld` owns conduit-front-door runtime routing.
- `SpellSpaceMeld` owns spellspace-front-door runtime routing.
- Resolve spells by spell_id or by normalized (spell/spellframe/binding_name) keys.
- Support root entry modes: spell_name (logical name), spell object, spellframe, or spell_id string.
- Normalize per-call `spell_override` payloads (dict/list/tuple) into runtime-friendly maps.
- Expose no-create live-creation probes that reuse meld lookup semantics:
  `has_live_creation(...)` and `describe_live_creation_status(...)`.
- Enforce reuse vs instantiate based on Existence, including EXISTING_CREATION spells returning stored objects.
- Select creations container by Existence: shared lifetimes (unique, unique_per_conduit_cluster,
  unique_per_conduit_lineage) use `spell._owner_creations`; per-conduit lifetimes
  (unique_per_conduit, many, unique_per_spell_space) use caller creations.
- Apply hooks and register instances into Creations.
- Enforce spell validity and change-control gates.
- Gate execution when ChangeControlManager marks a root dirty (if available).
- Perform lazy structural/resolution validation when validity is UNKNOWN or GATED.
- Build spell-bound `CreationContext` instances through
  `CreationContextBuilder`, which now consumes the compiler-owned
  `_spell_codegen_creation` handoff for constructed spells.

Inputs:
- Spellbook maps and spell identifiers (`spell_name`, `spell`, `spellframe`, `binding_name`).
- Optional `spell_override` payloads (dict/list/tuple).

Outputs:
- Constructed instances.
- Live-creation presence/status results without construction.

Owned State:
- Shared `Meld` core owns:
  - spellbook lookup references
  - input-resolution cache
  - change-control-manager cache
  - optional compiler-system helper
- `ConduitMeld` adds the conduit-owned creations registry reference.
- `SpellSpaceMeld` adds:
  - spellspace object
  - spellspace-local creations
  - owner-conduit creations
  - spellspace and owner-conduit ids

Lifecycle/Cleanup:
- Cleanup clears spellbook references and CreationContext caches.

Concurrency/Threading:
- Internal RLock guards Meld operations.

Invariants/Guarantees:
- At least one of `spell_name`, `spell`, or `spellframe` is required to resolve a target.
- `spell` as a string is treated as a spell_id; `spell_name` is treated as a logical name key.
- `spell_name` without an explicit spell/spellframe resolves via SpellInputUtils name normalization.
- The live-creation probe mirrors the same spell-resolution path as `meld(...)`
  but stops before construction.
- EXISTING_CREATION spells bypass the runtime and return the stored object.
- Constructed spells expect `_spell_codegen_creation` to exist before
  `CreationContextBuilder` builds their runtime context.
- `ConduitMeld` rejects `requires_spellspace_request` lineages because the
  conduit door cannot fabricate a request-local spellspace scope.
- `SpellSpaceMeld` is the only runtime door that may satisfy
  `unique_per_spell_space` request-local storage directly.
- Spells must be validated and not broken before execution.
- Change control may block dirty roots.
- Change-control checks are best-effort; failures to access change control do not block.
- Gated validity triggers Phase 1-4 and Phase 5-11 reruns under spell lock.

Failure Modes:
- ValueError when no identity inputs are provided.
- KeyError when a spell_id or lookup key cannot be resolved.
- TypeError when `spell_override` has an unsupported shape.
- RuntimeError for missing runtime state or EXISTING_CREATION spells without a backing instance.
- SpellSpaceScopeError for unique_per_spell_space without an active spellspace.
- MeldExecutionError for invalid spell state or dirty root gating.
- HookExecutionError for hook failures.

Observability:
- Exceptions and SafeLogger errors.

Extension Points:
- Hook maps from `SpellbookConfiguration`.

Key Files (C1):
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/conduit_meld.py`
- `src/melder/aether/conduit/meld/spellspace_meld.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`

### Component: SpellCompiler and Validation Pipeline
Purpose:
- Compile per-spell artifacts and validate correctness before resolution.

Responsibilities:
- Build requirements, symbolic graph, and local frames.
- Classify ParameterDIShape for constructor sockets (single, collection, SpellMap, contracts).
- Resolve SpellMap defaults and single/collection DI targets during Phase 3 graph construction.
- Produce foundational phase-1-to-phase-7 truth that the substituted live
  phase-8-to-phase-11 systems consume.
- The live post-phase-7 mapping is now:
  - phase 8 `SpellAnalyzer`
  - phase 9 `SpellArtifactProcessor`
  - phase 10 `SpellCodegenPlanner`
  - phase 11 `CodegenCreationSystem`
- Existing-creation spells bypass the live phase-8-to-phase-11 group.
- Track `SpellCompilerArtifact._phase8_11_codegen_ir_dirty` as a spell-local export
  freshness bit for phase8_11 IR snapshot updates.
- Run validation strategies and record results.
- Clean per-phase artifacts after resolution phases.
- Register ChangeControlManager revalidator and rebuild component-of index.
- Execute Phase 4 structural strategies (circular/self-dependency, SpellMap shape,
  contract provider presence, binding resolution cycles, parameter policy).
- Execute Phase 6 system strategies (cycle detection, graph consistency,
  root reachability/coverage, contract graph cycles, root viability/scale).

Inputs:
- Spell objects and spellbook registries.

Outputs:
- Validation results and foundational rooted artifacts on Spell.
- Analyzer/model/plan/creation artifacts are later published onto
  `SpellCompilerArtifact` by the substituted live phases 8-11.

Owned State:
- Per-spell artifacts (requirements, symbolic graph, resolution frame).
- Validation results, root blueprints, and occurrence plans.

Lifecycle/Cleanup:
- Cleanup clears phase artifacts and detaches from Spell.

Concurrency/Threading:
- Internal RLock; PhaseScheduler coordinates parallel work items.

Invariants/Guarantees:
- Phase artifacts are keyed by `spell_index.selected_spell_id`.
- Broken spells halt conjure via SpellbookValidationError.
- Single-annotation DI resolves to exactly one class/creation spell (methods/lambdas excluded).
- Collection DI (list[FrameType]) can resolve zero or more spells, including methods/lambdas.
- SpellMap defaults must resolve to exactly one candidate.
- `phase8_11` IR dirty state means "refresh export payload before read/compile",
  not "runtime root requires revalidation."

Failure Modes:
- Validation errors captured in SpellValidationResult and SpellbookValidationError.
- RuntimeError when single-annotation DI resolves to zero or multiple candidates.
- RuntimeError when SpellMap defaults resolve to zero or multiple candidates.

Observability:
- Errors surfaced via exceptions and logger in Spellbook.

Extension Points:
- Custom validation strategies registered in SpellValidationSystem.

Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`

### Component: DevOps Control Plane
Purpose:
- Track lineage validity, per-conduit resolution validity, dirty roots, and pending changes.

Responsibilities:
- Maintain SpellSystemStates registry, SpellSystemState entries, and per-conduit ConduitResolutionState.
- Track dirty roots and pending changes in ChangeControlManager.
- Aggregate incident/change control in DevOpsManager.
- Revalidate dirty roots via registered callback outside the lock.
- DevOpsManager and ChangeControlManager are per-frame; per-conduit resolution validity lives in SpellSystemStates._resolution_by_conduit_id. EVIDENCE: src/melder/aether/aetheric_frame/aetheric_frame.py:__init__ + src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:get_or_create_conduit_resolution_state.
- RiskManager tracks per-conduit risk and toggles Spellbook validation gating. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:register_conduit + on_resolution_validity_change.

Inputs:
- SpellIndex/Spell registrations and dependency updates.
- Conduit ids, per-conduit validity updates, and system diagnostics (Phases 5-11).

Outputs:
- Lineage validity and dirty-root state used by Meld gates.
- Per-conduit resolution validity and diagnostics surfaced by SpellSystemStates.

Owned State:
- `SpellSystemStates` indexes, dirty sets, and `_resolution_by_conduit_id`.
- `ConduitResolutionState` validity maps, diagnostics, and dirty flags.
- `ChangeControlManager` pending changes and dirty roots.
- `DevOpsManager` incident and change control managers.
- `RiskManager` per-conduit risk sets and spellbook gating state. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:__init__ + _conduit_states.

Lifecycle/Cleanup:
- Cleanup is idempotent and releases references.

Concurrency/Threading:
- RLocks guard state mutations.

Invariants/Guarantees:
- Registering a lineage marks it dirty.
- Dirty roots for a conduit can block Meld execution.
- `revalidate_dirty_roots(conduit_id, ...)` returns early without dirty roots or a revalidator for that conduit.
- Successful revalidation clears dirty roots and disables monitoring for that conduit.
- DevOps dirty roots are conduit-scoped revalidation state and are separate from
  SpellCompilerArtifact `phase8_11` IR freshness dirty tracking.

Failure Modes:
- ValueError for invalid or missing ids.
- RuntimeError when SpellSystemStates is cleaned/unavailable for state access.

Observability:
- Exceptions; minimal internal logging.

Extension Points:
- Revalidation hooks in ChangeControlManager.

Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`

### Component: Transaction Admission Plane (Scope Acquisition)
Purpose:
- Serialize structural mutations (bind, link, cluster_link,
  transfer_ownership, unlink) through one cheap scope-acquisition gate so
  non-overlapping work proceeds in parallel and only true overlap waits.

Responsibilities:
- `TransactionMediator` is the front door: identity-validated transaction
  ingress, same-thread nested joins, root-session ownership, scope-local
  pending (wait-and-retry admission bounded by
  `max_transaction_wait_time_in_seconds`), and commit/abort finalization.
- `ChangeControlEmbargoManager` is the moded lock table: claim records carry
  `ClaimMode` (`x` exclusive / `s` shared / `ix` intent), acquisition is
  atomic all-or-nothing with `(scope_key, holder, mode)` blocking evidence,
  release wakes waiters, cleanup notifies waiters so nothing hangs.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:ClaimMode + try_acquire + release_owner.
- `ChangeControlOrchestrator.admit_request` is one acquisition under the
  admission lock; the legacy in-flight conflict scan is retired and
  `ChangeControlConflictManager` is no longer consulted at admission.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:admit_request.
- Requests may carry per-scope claim modes
  (`ChangeControlTransactionRequest.scope_claims`); unspecified keys default
  to exclusive, preserving pre-mode semantics.
- `TransactionStrategy.apply_commit_delta(...)` runs between the session
  commit pipeline and orchestrator commit, while scopes are still held; the
  base default stamps `DevopsFactRecord` baselines (family, region,
  reporter, generation) into `DevopsInformationRegistry` so information
  strategies can skip re-derivation when all changes since the baseline
  flowed through the plane.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:_apply_strategy_commit_delta + src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:report_fact.
- `TransactionStrategyBuilder` is the registry-backed dispatch seam for the
  built-in transaction families. The current builder registers:
  `bind`, `link`, `unlink`, `cluster_link`, `transfer_ownership`,
  `add_to_index`, `remove_from_index`, and `notch`, then resolves the
  strategy class for `build_start_plan(...)`, `on_start(...)`, `on_end(...)`,
  and `apply_commit_delta(...)`.
- `unlink` is a full mediated transaction (`UnlinkTransactionStrategy`):
  `Conduit.sever_link` self-admits it (admit -> ward sever -> commit), and
  `ConduitWard._remove_contract` re-resolves the borrowing side's SpellContract
  consumers on a whole-link sever so the next meld revalidates (existing
  creations rebuild lazily; nothing is torn down eagerly).
  EVIDENCE: src/melder/aether/conduit/conduit.py:sever_link + begin_transaction(unlink branch); src/melder/aether/conduit/conduit_ward/conduit_ward.py:_remove_contract.

Invariants/Guarantees:
- Admission cost is O(requested scopes) dict operations under one lock.
- Disjoint claim sets admit in parallel; `s`/`s` and `ix`/`ix` coexist on
  one scope; `x` excludes everything (static matrix).
- One admitted request owns exactly one root session; cross-thread re-begin
  of a hosted request fails fast naming the owning thread.
- Scope-wait timeout raises with blocking scope keys and holder request ids.
- Readers (meld paths) never enter this plane; they remain protected by
  validity gating that commits trigger.

Failure Modes:
- RuntimeError on scope-wait timeout (with holder evidence) and on
  non-waitable admission denial.
- Commit-delta failures poison the session abort path like commit-hook
  failures.

Admission Vocabulary:
- Scope KEYS are the admission vocabulary; scope HASHES are advisory
  identity evidence and carry no claims. Hash-only roots admit
  independently even when their hashes overlap.
- Same-thread session reuse is per-identity: the same identity re-begins
  into its session, while a different identity on the same thread opens its
  own root session.
  EVIDENCE: tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:test_change_control_scope_hash_only_roots_admit_independently.
- `queue_competing_root_transactions` is fully removed (config ctor/slot/
  property/fluent setter, frame merge, CCM wiring, mediator ctor/configure/
  describe). Root admission policy has exactly one knob:
  `max_transaction_wait_time_in_seconds`. SYNC NOTE 2026-06-12 (patch lane
  `devops_info_catalog_and_queue_removal_2026_06_12`).

Family Claim Modes (landed 2026-06-14):
- Strategies emit per-family `scope_claims`. Owning spellbooks are claimed `ix`
  (intent), not `x`, so additive piece-work (link/bind/cluster) coexists on a
  spellbook while a whole-spellbook `x` claim (transfer) is still excluded:
  - link: `ix` each owning spellbook; participant conduits/wards `x`.
  - bind: `ix` owning spellbook (+ `ix` each affected cluster post-conjure);
    conduit/ward `x` (the conjure owns them).
  - cluster_link: `ix` each member spellbook; cluster + conduits + wards `x`.
  - transfer_ownership: already `x` on every scope (no override needed).
  - unlink (sever): mirrors link -- `ix` spellbooks, `x` conduits/wards.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/{link,bind,cluster_link,unlink}_transaction_strategy.py.
- Relational commit deltas: NOT NEEDED (chosen final design: eager, not lazy).
  The provider->borrower link mirror (`ConduitWard._add_spell_to_contract` ->
  `register_provider_conduit` -> `register_conduit_link`; sever via
  `_remove_contract` -> `unregister_provider_conduit`) and the cluster-membership
  mirror (`ConduitCluster.add/remove_member` ->
  `register/unregister_cluster_membership`) are maintained EAGERLY at the
  mutation site, now race-safe under the transaction's held claims. Base
  `apply_commit_delta` still stamps fact baselines, so freshness truth is
  written without per-family delta overrides.

Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unlink_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/cluster_link_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/add_to_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/remove_from_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_scope_acquisition.py`

### Component: DevOps Information Strategies
Purpose:
- Caller-paid, registry-only information checks: live activity views, change
  impact sets, frame rollups, and the registry's own consistency audit, each
  with a uniform freshness verdict built from fact-record baselines.

Responsibilities:
- `DevopsInformationStrategyBuilder` registers the default catalog at
  construction and counts successful executions per normalized name
  (`get_execution_count` / `list_execution_counts`); later registrations
  under the same name override defaults.
- Catalog (`src/melder/aether/aetheric_frame/dev_ops/information_strategies/`):
  - `transaction_activity_view`: live transaction ids along one axis
    (identity_kind+identity_id | scope_key | transaction_type).
  - `cluster_fanout`: membership fan-out for one conduit (siblings unioned
    across its clusters) or one cluster (member roster).
  - `transfer_blast_radius`: full relational impact set for transferring one
    conduit (owning spellbook, siblings, borrowers, providers, clusters).
  - `frame_operational_view`: one-shot frame rollup (population by kind,
    ownership/link/cluster shape, transaction pressure by type, fact
    coverage by family).
  - `registry_consistency_audit`: symmetry audit over every bidirectional
    map and transaction reverse index; any asymmetry is evidence a write
    bypassed the transaction plane.
- `InformationFreshnessInspector` centralizes the staleness vocabulary:
  `normalize_region` folds "scope:" keys onto fact-record region form;
  `build_freshness_view` returns per-region baselines/ages and, when the
  caller passes `max_age_in_seconds`, `stale_regions` plus a `fresh`
  verdict. This implements the control-plane economy: check the baseline
  first, re-derive only when cold or stale.
- `DevopsInformationRegistry.snapshot_relationship_maps()` (additive)
  returns all forward/reverse maps copied under one lock acquisition with
  identity tuple keys rendered "kind:id"; strategies stay on public API.

Invariants/Guarantees:
- Strategies are static-execute classes resolved by normalized name; results
  are detached ids-only payloads (no live object references).
- Nothing in the runtime invokes the catalog automatically; execution is
  caller-paid by design.
- Failed executions do not increment builder counters.

Known Deferred Work (patch lane `devops_info_catalog_and_queue_removal_2026_06_12`):
- Live-runtime-truth reconciliation probes (verifying mirrored maps against
  real runtime objects) await probe contracts on runtime classes.
- Audit sampling cadence (who schedules audits, how often) is policy left to
  callers.

Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_strategy_builder.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/information_strategy_support.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/transaction_activity_view_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/cluster_fanout_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/transfer_blast_radius_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/frame_operational_view_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/information_strategies/registry_consistency_audit_strategy.py`
- `tests/unit/melder/aether/dev_ops/test_devops_information_strategies.py`

### Component: Logging and Initialization Helpers
Purpose:
- Provide the process-wide logging provider host plus the adapter and helper
  functions that route runtime logging through it.

Responsibilities:
- Host one process-wide channel-logger resolver and one default stdlib logger
  fallback in `AetherUtilitySystem`.
- Wrap stdlib or channel loggers in `SafeLogger`.
- Route explicit post-boot logger attachment through
  `InitHelpers.resolve_safe_logger(...)`.
- Route provider-backed channel logger acquisition through
  `InitHelpers.resolve_channel_logger(...)`.
- Gate automatic channel logger activation behind Aether-owned configuration so
  the provider path can no-op by default.

Inputs:
- Logger instances, logger-like channel objects, registrant metadata, and
  provider registration callables.

Outputs:
- SafeLogger instances.

Owned State:
- `AetherUtilitySystem` owns the registered resolver and default fallback
  logger.
- `SafeLogger` holds the wrapped logger reference and level data.

Lifecycle/Cleanup:
- `AetherUtilitySystem` cleanup clears provider registrations and resets
  singleton state for tests.
- `SafeLogger` cleanup releases the wrapped logger reference.

Concurrency/Threading:
- SafeLogger uses no explicit locking; underlying logger handles threading.

Invariants/Guarantees:
- SafeLogger never raises during init for None logger.
- Provider-backed logger lookup falls back to the registered stdlib logger
  before finally falling back to a silent SafeLogger.

Failure Modes:
- TypeError if logger/provider types are unsupported.

Observability:
- SafeLogger routes messages with or without masking.

Extension Points:
- Channel logger resolver registration.
- Default stdlib logger fallback registration.

Key Files (C1):
- `src/melder/aether/aether_utility_system.py`
- `src/melder/utilities/logger/safe_logger.py`
- `src/melder/utilities/helpers/init_helpers.py`

### Component: Spell Examination Profiles
Purpose:
- Provide reflective examination profiles for raw candidates and bound spell
  runtime surfaces.

Responsibilities:
- Build `general` and `detailed` examination profiles through
  `SpellExaminer`.
- Build binding and resolution profiles through the registered strategy layer.
- Add class and callable inspection payloads on the detailed path.
- Expose registry-driven profile creation by stable profile name.

Inputs:
- Raw candidate objects for binding inspection.
- Registered `Spell` objects for resolution-backed profile generation.

Outputs:
- `SpellBindingProfile`
- `SpellResolutionProfile`
- `SpellGeneralProfile`
- `SpellDetailedProfile`
- `ClassProfile`
- `MethodProfile`

Owned State:
- `SpellExaminer` owns the builder registry for named profile creation.
- Emitted profile objects own their nested binding, resolution, and inspector
  payloads.

Lifecycle/Cleanup:
- `SpellExaminer` is lightweight and registry-backed rather than long-lived
  frame state.
- The profile objects are cleanable and release nested profile payloads on
  cleanup.

Concurrency/Threading:
- `SpellExaminer` resolves a named builder and delegates synchronously.
- Profile building reads live spell state when a bound `Spell` is supplied but
  does not mutate runtime ownership.

Invariants/Guarantees:
- The built-in default profile names are `general` and `detailed`.
- `create_profile(...)` does not reinterpret the target or enforce a concrete
  return type beyond whatever the resolved builder emits.
- Binding and resolution remain distinct nested layers inside the emitted
  profile objects.

Failure Modes:
- `SpellExaminer.create_profile(...)` raises `ValueError` when the requested
  profile name is not registered.
- Builder or inspector failures bubble from the resolved builder path.

Observability:
- These layers are primarily introspection/tooling surfaces and do not define
  a separate logging stack.

Extension Points:
- `register_profile_builder(...)` for new named examination views.
- Future richer inspection payloads on top of the existing general/detailed
  contract.

Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/spell_examiner.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/general_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/detailed_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py`
- `src/melder/aether/spellbook/spell_compiler/profiles/resolution_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/profiles/class_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/profiles/method_profile.py`

### Component: PhaseScheduler and UnitOfWork Orchestration
Purpose:
- Coordinate multi-phase execution across spells.

Responsibilities:
- Register phases with factories producing UnitOfWork.
- Manage worker threads and a shared cancellation signal.
- Enforce phase barriers and timeouts.

Inputs:
- Spellbook and `SpellbookConfiguration`.

Outputs:
- Phase results (UnitOfWork sequences).

Owned State:
- Worker threads, queue, cancellation signal.
- Phase registry and order.

Lifecycle/Cleanup:
- Cleanup cancels workers, joins threads, and clears registries.

Concurrency/Threading:
- Dedicated worker threads and shared queue.

Invariants/Guarantees:
- One-shot usage; cleaned scheduler is unusable.

Failure Modes:
- PhaseTimeoutError or PhaseExecutionError on failures.

Observability:
- Exceptions raised to caller.

Extension Points:
- Additional phases or alternative UnitOfWork factories.

Key Files (C1):
- `src/melder/utilities/synchronization/phase_scheduler.py`

## C2 Subcomponents Catalog

### Subcomponent: Runtime Warning Guardrails
Parent Component: Public API and Runtime Guardrails
Purpose:
- Warn on unsupported Python versions and GIL mode.
Contract/Interface:
- `warnings.warn` used for soft warnings.
Data Structures:
- None.
Concurrency/Threading:
- Import-time only.
Key Files (C1):
- `src/melder/__init__.py`

### Subcomponent: Registration Guard Sentinel
Parent Component: Public API and Runtime Guardrails
Purpose:
- Block internal objects from being bound as spells.
Contract/Interface:
- `assert_allowed(candidate, context)` raises on internal sentinel.
Data Structures:
- `_SENTINEL` identity object.
Concurrency/Threading:
- Singleton, no explicit lock.
Key Files (C1):
- `src/melder/__melder_registration_guard__.py`

### Subcomponent: Packaged Hardcopy Document Modules
Parent Component: Packaged Hardcopy Documents And Public Helper Exports
Purpose:
- Publish immutable package-root hardcopy system-document objects for
  agent-facing architecture/component/graph queries.
Contract/Interface:
- `StaticSystemDocument.render_json()`
- `StaticSystemDocument.render_markdown()`
Data Structures:
- Module-level `StaticSystemDocument` singletons.
Concurrency/Threading:
- Import-time only; no mutable shared runtime state.
Key Files (C1):
- `src/melder/system_document.py`
- `src/melder/__architecture__.py`
- `src/melder/__components__.py`
- `src/melder/__graph_network__.py`
- `src/melder/__graph_details__.py`

### Subcomponent: ProtocolCrafter Utility
Parent Component: Packaged Hardcopy Documents And Public Helper Exports
Purpose:
- Generate protocol code and maintain bounded protocol blocks in interface
  files.
Contract/Interface:
- `craft_protocol_code(...)`
- `craft_protocol_module_code_from_source_file(...)`
- `write_protocol_module_from_source_file(...)`
Data Structures:
- Instance-local protocol-crafter id and lock.
Concurrency/Threading:
- Instance `RLock` groups generation and file-update operations.
Key Files (C1):
- `src/melder/utilities/ai_native_support_tools/protocol_crafter.py`

### Subcomponent: Aether Root Configuration Assembly
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Build, install, and activate the root logger-policy configuration that
  Aether applies into `AetherUtilitySystem`.
Contract/Interface:
- `create_configuration()`
- `create_configuration_builder()`
- `configure(...)`
- `activate(...)`
Data Structures:
- Installed `AetherConfiguration` plus the one-shot
  `AetherConfigurationBuilder`.
Concurrency/Threading:
- Aether instance lock around configuration install/activation paths.
Key Files (C1):
- `src/melder/aether/aether.py`
- `src/melder/aether/aether_configuration.py`
- `src/melder/aether/aether_configuration_builder.py`

### Subcomponent: Scan-Bind Module Scanner
Parent Component: Spellbook Core (Binding and Conjure)
Purpose:
- Replay `scan_bind` metadata from one module into `Spellbook.bind(...)`.
Contract/Interface:
- `Spellbook.scan(...)`
- `Scan.scan_module(...)`
Data Structures:
- Frozen `ScanBindMetadata` payloads attached under `__melder_scan_bind__`.
Concurrency/Threading:
- Delegates actual binding synchronization to the owning Spellbook.
Key Files (C1):
- `src/melder/aether/spellbook/bind/scan.py`
- `src/melder/aether/spellbook/spellbook.py`

### Subcomponent: Spellbook Configuration Initialization
Parent Component: Spellbook Core (Binding and Conjure)
Purpose:
- Initialize `SpellbookConfiguration` by adopting a frame-owned shared config
  or creating a new one.
Contract/Interface:
- `_initialize_configuration()` sets `_configuration` and `_configuration_locked`.
Data Structures:
- `SpellbookConfiguration` properties and hook maps.
Concurrency/Threading:
- RLock in Spellbook and `SpellbookConfiguration`.
Key Files (C1):
- `src/melder/aether/spellbook/spellbook.py`

### Subcomponent: Spellbook Conjure Pipeline
Parent Component: Spellbook Core (Binding and Conjure)
Purpose:
- Run phases 1-4 plus conduit resolution phases 5-11 (with 8-11 gated on
  foundational success), then build a Conduit and wire ownership into spells.
Contract/Interface:
- `conjure(policy, dynamic, name, conduit_logger)`.
Data Structures:
- PhaseScheduler units and spell registries.
Concurrency/Threading:
- Spellbook lock + PhaseScheduler workers.
Key Files (C1):
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`

### Subcomponent: Spellbook Binding Pipeline
Parent Component: Binding Pipeline (Bind, Spell, SpellIndex)
Purpose:
- Register a spell and update local maps and SpellSystemStates.
Contract/Interface:
- `Spellbook.bind(...)` and `Bind._bind_logic(...)`.
Data Structures:
- SpellIndex, Spell, lookup maps.
Concurrency/Threading:
- RLocks in Spellbook, Bind, and SpellIndex.
Key Files (C1):
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/bind/bind.py`

### Subcomponent: SpellIndex (Spell Index / Categorization)
Parent Component: Binding Pipeline (Bind, Spell, SpellIndex)
Purpose:
- Provide a stable index that categorizes and targets spells and holds the
  active selected spell. Version history is owned by MutationResearch.
Contract/Interface:
- `SpellIndex.selected_spell_id` and `SpellIndex.update(...)`.
Data Structures:
- ULID index id and the active selected spell id.
Concurrency/Threading:
- RLock protecting selected-spell updates.
Key Files (C1):
- `src/melder/aether/spellbook/bind/spell_index.py`

### Subcomponent: SpellIndex Mutation Surface
Parent Component: Binding Pipeline (Bind, Spell, SpellIndex)
Purpose:
- Expose the current public Spellbook seams for SpellIndex active-member
  switching and member movement between indices.
Contract/Interface:
- `notch_spell(...)` starts the `notch` transaction and delegates the current
  member-store switch to `_apply_notch(...)`.
- `add_spell_into_spellindex(...)` starts the `add_to_index` transaction and
  delegates the move-in to `_apply_add_to_index(...)`.
- `remove_spell_from_spellindex(...)` starts the `remove_from_index`
  transaction and delegates the split to `_apply_remove_from_index(...)`.
Data Structures:
- Transaction metadata carrying spellbook/conduit ids, binding key, member id,
  and source/target SpellIndex ids.
Concurrency/Threading:
- Public entrypoints use the Spellbook lock and the transaction mediator;
  the actual member-store seam is still unimplemented.
Key Files (C1):
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/add_to_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/remove_from_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py`

### Subcomponent: Parameter DI Shape Classification
Parent Component: DI Descriptors and Contract Sockets
Purpose:
- Classify constructor parameters into DI shapes (single, collection, SpellMap, contracts).
Contract/Interface:
- `ParameterDIShape` enumeration and Phase 1 requirements capture.
Data Structures:
- `ParameterDIShape` values attached to SpellRequirements.
Concurrency/Threading:
- No internal locks; classification occurs under SpellCompiler orchestration.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`

### Subcomponent: SpellMap Descriptor
Parent Component: DI Descriptors and Contract Sockets
Purpose:
- Declare explicit DI targets with optional override payloads.
Contract/Interface:
- `SpellMap.lookup_triplet` and `SpellMap.canonical_key`.
Data Structures:
- `(spell, spellframe, binding_name)` tuple and override payload.
Concurrency/Threading:
- No internal lock.
Key Files (C1):
- `src/melder/aether/conduit/meld/contracts/spell_map.py`

### Subcomponent: SpellContract and Legacy Mutation-Socket Semantics
Parent Component: DI Descriptors and Contract Sockets
Purpose:
- Describe the live SpellContract descriptor plus the retained validation-only
  semantics for the removed mutation-socket family.
Contract/Interface:
- `SpellContract.lookup_triplet` and `canonical_key`.
- Legacy mutation-socket classifications are currently blocked by Phase 4
  validation (`MUTATION_CONTRACT_DISABLED`) while mutation systems are on
  hold.
Data Structures:
- SpellContract keys and optional override payloads, plus validation-side
  mutation-socket classification handling.
Concurrency/Threading:
- No internal lock.
Key Files (C1):
- `src/melder/aether/conduit/meld/contracts/spell_contract.py`
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`
- `src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`

### Subcomponent: SpellbookConfiguration Freeze and Validation
Parent Component: Spellbook Configuration and System State
Purpose:
- Validate required properties and freeze `SpellbookConfiguration`.
Contract/Interface:
- `freeze()` (which internally calls `validate()` before locking).
Data Structures:
- Property map and idempotent keys.
Concurrency/Threading:
- RLock guards property mutation and freeze.
Key Files (C1):
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`

### Subcomponent: PhaseScheduler Pipeline
Parent Component: PhaseScheduler and UnitOfWork Orchestration
Purpose:
- Run phases with worker pool, barrier timeout, and cancellation.
Contract/Interface:
- `register_phase` and `run_all_phases`.
Data Structures:
- Worker threads and shared queue.
Concurrency/Threading:
- Dedicated worker threads, cancellation signal.
Key Files (C1):
- `src/melder/utilities/synchronization/phase_scheduler.py`

### Subcomponent: SpellCompiler Phase Artifacts
Parent Component: SpellCompiler and Validation Pipeline
Purpose:
- Build per-spell requirements, symbolic graphs, and resolution frames.
Contract/Interface:
- `SpellCompilerArtifact.cleanup_phase_artifacts()` and phase methods.
Data Structures:
- Requirements, symbolic graph, resolution frame, validation results.
- RootResolutionBlueprint uses a PathRegistry (PathId interning) and DagIndex
  (SocketRef stores param_path_id) for Phase 5/8 path handling.
- `_phase8_11_codegen_ir_dirty` tracks whether exported phase8_11 IR must be
  recaptured before `codegen_ir` reads or codegen-creation compile work.
Concurrency/Threading:
- SpellCompilerArtifact RLock; PhaseScheduler creates UnitOfWork.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py`
- `src/melder/aether/spellbook/spell_compiler/dag/dag_index.py`

### Subcomponent: Spell Validation Strategies
Parent Component: SpellCompiler and Validation Pipeline
Purpose:
- Run structural validation strategies (Phase 4).
Contract/Interface:
- `SpellValidationSystem.validate_spell(...)`.
Data Structures:
- Strategy registry and validation results.
Concurrency/Threading:
- RLock on strategy registry.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`

### Subcomponent: System Validation (Phase 6)
Parent Component: SpellCompiler and Validation Pipeline
Purpose:
- Validate Phase 5 artifacts at system level and update resolution validity.
Contract/Interface:
- `SpellSystemValidationSystem.validate(...)`.
Data Structures:
- Root blueprints and diagnostics.
Concurrency/Threading:
- No internal locking; caller-managed.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`

### Subcomponent: Change-Control Revalidation Wiring
Parent Component: SpellCompiler and Validation Pipeline
Purpose:
- Rebuild component-of index and register revalidation callback for dirty roots.
Contract/Interface:
- `ChangeControlManager.rebuild_component_of(conduit_id, ...)` and `set_revalidator(conduit_id, ...)`.
- Component-of rebuild uses **owned roots only** (filtered from Phase 5 root blueprints). EVIDENCE: src/melder/aether/spellbook/spell_compiler/spell_compiler.py:run_phase_root_blueprints + _filter_root_blueprints_to_owned.
- Revalidation wiring consumes ChangeControlManager dirty roots and is not
  driven by `SpellCompilerArtifact._phase8_11_codegen_ir_dirty`.
Data Structures:
- Root blueprint DAGs from Phase 5.
Concurrency/Threading:
- Compiler-phase orchestration plus ChangeControlManager lock in
  `rebuild_component_of`.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`

### Subcomponent: Aether Frame Registry
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Ensure and retrieve AethericFrames and bind configuration.
Contract/Interface:
- `_ensure_frame`, `_bind_configuration`, `_get_configuration`.
Data Structures:
- `_aetheric_frames` map and `_default_frame`.
Concurrency/Threading:
- Aether singleton class lock for instance creation and Aether instance lock for
  frame registry operations.
Key Files (C1):
- `src/melder/aether/aether.py`

### Subcomponent: Conduit Normal Initialization
Parent Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Register a normal conduit in Aether and register spell indices.
Contract/Interface:
- `_configure_conduit_state()` and `_add_spells_to_aether()`.
Data Structures:
- Aether frame registry and spell registry.
Concurrency/Threading:
- Conduit lock and Aether lock.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`

### Subcomponent: Lesser Conduit Creation
Parent Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Spawn a lesser conduit and link it into the lineage tree.
Contract/Interface:
- `create_lesser_conduit(...)`.
Data Structures:
- ConduitWard lineage maps and Creations delegation.
Concurrency/Threading:
- Parent conduit lock.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`

### Subcomponent: Conduit Upgrade to Normal
Parent Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Convert a lesser conduit into a normal conduit in dynamic mode.
Contract/Interface:
- `upgrade_to_normal(name, hooks)`; preserves/rebinds the current `Creations`
  manager, rewires Meld, calls `ConduitWard._convert_to_normal_conduit`, and
  calls `Spellbook.create_new_preset_spellbook`.
Data Structures:
- Current `Creations` manager rebound to upgraded conduit state.
- Snapshot of root conduit resolution state (if available).
Concurrency/Threading:
- Conduit lock with ConduitWard lock during conversion.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/spellbook/spellbook.py`

### Subcomponent: Conduit Link and Sever
Parent Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Establish or sever peer link contracts between normal conduits.
Contract/Interface:
- `link(...)` and `sever_link(...)` delegate to ConduitWard `_link`/`_sever_link`,
  which create or remove Spellbook link contracts.
Data Structures:
- Contract maps and inbound/outbound indices.
Concurrency/Threading:
- Conduit lock and SafeGuard ordering in ConduitWard.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/spellbook/spellbook.py`

### Subcomponent: Conduit Hook Wiring
Parent Component: Conduit Runtime (Normal and Lesser)
Purpose:
- Pull hook map from `SpellbookConfiguration` and attach to Conduit and Meld.
Contract/Interface:
- `_initialize_conduit_hooks()` and `_get_conjure_hook_map()`.
Data Structures:
- Hook map keyed by spellbook id.
Concurrency/Threading:
- Conduit lock.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/spellbook/spellbook.py`

### Subcomponent: ConduitWard Contract Graph
Parent Component: ConduitWard and Contracts
Purpose:
- Create and manage contracts and link indices.
Contract/Interface:
- `_link`, `_sever_link`, `_remove_contract`.
Data Structures:
- Contract map and inbound/outbound indexes.
Concurrency/Threading:
- Ward lock and ordered locking during contract creation.
Key Files (C1):
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`

### Subcomponent: ConduitWard Conversion
Parent Component: ConduitWard and Contracts
Purpose:
- Convert a lesser conduit's lineage state to normal during upgrade.
Contract/Interface:
- `_convert_to_normal_conduit()`.
Data Structures:
- Parent/root conduit references and policy state.
Concurrency/Threading:
- ConduitWard lock.
Key Files (C1):
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`

### Subcomponent: Ownership Transfer
Parent Component: ConduitWard and Contracts
Purpose:
- Transfer spell stewardship between conduits in dynamic mode.
Contract/Interface:
- `Conduit.transfer_spell_ownership(...)` and `_transfer_spell_ownership(...)`.
Data Structures:
- Preflight summaries (borrowers, dependencies, creations) and rollback snapshots.
Concurrency/Threading:
- SafeGuard around source/target conduit locks during registry flips.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`

### Subcomponent: ConduitCluster Auto-Sharing
Parent Component: AethericFrame Services
Purpose:
- Auto-share spell roots among cluster members.
- Shareable roots are filtered to `Existence.unique_per_conduit_cluster` via
  `ConduitCluster._get_shareable_spells`.
Contract/Interface:
- `handle_join`, `handle_leave`, `share_to_borrower`.
- `share_to_borrower` calls `Conduit.add_spell_to_contract` with permissions from
  `spell.permissions` (defaults to "create" if missing) and dependency linking
  controlled by `auto_link_dependencies`.
- `share_to_borrower` uses a cluster-scoped `root_spell_id`
  (`cluster:{name}:{owner_id}:{spell_id}`) so cluster teardown removes only
  cluster-created contracts.
Data Structures:
- `members` set and `shared_spells` map.
Concurrency/Threading:
- Cluster lock.
Key Files (C1):
- `src/melder/aether/conduit/conduit_cluster.py`

### Subcomponent: ConduitCloud Registry
Parent Component: AethericFrame Services
Purpose:
- Registry for named conduits in dynamic mode.
Contract/Interface:
- `get_conduit`, `_register_conduit`, `_unregister_conduit`.
Data Structures:
- `_registry` map.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/aetheric_frame/conduit_cloud.py`

### Subcomponent: Crystallizer Root
Parent Component: Crystallizer Root And Module-World Surfaces
Purpose:
- Hold crystallizer policy and build retained module-world manifests from live
  spells.
Contract/Interface:
- `create_configuration()`, `configure(...)`, `activate(...)`, `deactivate()`
- `create_spell_crystal(...)`
Data Structures:
- Installed `CrystallizerConfiguration` plus configured/activated state.
Concurrency/Threading:
- Singleton lock for construction and instance `RLock` for lifecycle changes.
Key Files (C1):
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration_builder.py`

### Subcomponent: SpellCrystal Manifest
Parent Component: Crystallizer Root And Module-World Surfaces
Purpose:
- Carry the retained module/classification/dependency manifest for one
  concrete spell (custody-twin CARRIER since the 2026-07-10 S1 slimming).
Contract/Interface:
- Constructed from one live `Spell` plus crystallizer source-root policy.
- Delegates the module-world walk to a single-use `CrystalAnalyzer` and
  carries the returned `CrystalAnalysisResult` (V3 carrier law).
- Exposes root module identity, module/path inventories, classification
  buckets, direct-dependency maps, physical SHA256 fingerprints, export
  surfaces, and topological module load order via delegating properties.
Data Structures:
- `_analysis` (one carried `CrystalAnalysisResult`; the pre-decomposition
  per-map slots were absorbed into it).
Concurrency/Threading:
- Instance `RLock`.
Key Files (C1):
- `src/melder/crystallizer/crystals/spell_crystal.py`
- `src/melder/crystallizer/crystal_analysis/crystal_analyzer.py`

### Subcomponent: SyntheticModule Runtime
Parent Component: Crystallizer Root And Module-World Surfaces
Purpose:
- Provide the live in-memory module embodiment and importlib publication path
  for crystallized source.
Contract/Interface:
- `create_module_for_spec(...)`, `build_registered_spec(...)`,
- `exec_registered_module(...)`, and explicit registration/publication helpers.
Data Structures:
- Class-level synthetic import registry plus per-module source/dependency
  metadata.
Concurrency/Threading:
- Class-level registry lock plus instance `RLock`.
Key Files (C1):
- `src/melder/crystallizer/synthetic_module.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py` (the M3
  synthetic-module rebuild consumer; `crystal_loader/bootstrap_manifest.py`
  is gone since the 2026-07-10 decomposition)

### Subcomponent: MutationResearch Root (ResearchSet Registry)
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Own the formal research declaration record over the live spell world from
  the Aether-hosted singleton root (2026-07-11 rebuild; the May session model
  and its conduit/frame facades are GONE).
Contract/Interface:
- `Aether.mutation_research`
- `create_configuration()`, `create_configuration_builder()`,
  `configure(...)`, `activate(...)`, `deactivate()`
- `research_set(name="default")`, `create_research_set(name)`,
  `list_research_set_names()`
- `describe_research_composition()` (the MutationResearchCrystal twin feed)
- `load_recorded_composition(...)` (hydration seam; registry replaced
  wholesale, guaranteed `default` set recreated when absent)
- Foresight reads (2026-07-11): `source_view(spell_id, module_name=None)`
  (recorded-first module text - synthetic always, user when retained;
  live-disk fallback through the recorded path with a drift marker vs the
  sealed fingerprint; honest `text_unavailable`/`unknown_module`),
  `impact_view(spell_id=|module_name=, set_name)` (crystallizer
  `analyze_impact` radius JOINED with research residency per affected
  spell: declared/lane/state/campaign), `module_graph_view(spell_id)`
  (single-crystal walkable world incl. LOCAL reverse import edges),
  `source_drift_view()` (no-args full drift passthrough), and
  `preview_candidate(code, against_spell_id=None, module_name=None)`
  (read-only candidate mock: sha + AST defines/import roots, would-be
  source + structural diffs via `DiffEngine.diff_materials` with the
  candidate keyed to the against-spell's root module, would-be radius).
  Custody-unavailable = LOUD RuntimeError (the caller asked for recorded
  truth); candidate parse errors answer honestly, never raise.
- Surgical synthesis + ancestry mint (2026-07-11, salvaged May lane):
  `synthesize_candidate(base_spell_id, donor_spell_id, take_functions=,
  take_classes=, stage_ancestry=, set_name=)` composes one candidate from
  two recorded root-module texts through the owned `StructuralSynthesizer`
  (AST line-splice: same-named parts replace, new parts append, decorators
  travel; unknown selections refuse loudly; parse errors honest) and runs
  the composed text through the full `preview_candidate` against the base.
  The MINT half is the ambient staged-ancestry seam (campaign-pattern):
  `stage_ancestry(parents)` / `clear_staged_ancestry()` / `staged_ancestry`
  - the next FRESH world entry consumes the stamp ONE-SHOT and mints the
  multi-parent node (`record_world_entry` carries parent_spell_ids end to
  end with register_spell's residence validation; rediscoveries re-stage
  the stamp untouched, because identical content re-entering is not the
  synthesized candidate arriving).
- Lane-type policy (2026-07-11, salvaged May lane): configuration key
  `lane_type_enforcement` (bool, default False; reload-lane backfill-safe)
  propagates to every set at activation, hydration, and set creation
  (`set_lane_type_enforcement`); when armed, a type-mixing join requires
  force=True. The vocabulary itself (`LaneType`:
  development/experiment/production/test) is always available.
- `_emit_research_composition()` is the package's ONLY crystallizer
  touchpoint: sets call it through their injected `on_mutation` callback
  after every mutating verb (replace-on-emit; NO-OP while the root is
  inactive or the crystallizer records nothing).
Data Structures:
- `_research_sets_by_name` map (set name -> ResearchSet; `default`
  guaranteed at init).
Concurrency/Threading:
- RLock plus a dedicated emission RLock (`_emission_lock`, BUG-031 2026-07-18);
  one-way lock order is emission -> root -> set -> crystallizer.
- `_emit_research_composition` serializes its whole read-and-publish body under the
  emission lock; `create_research_set` and `load_recorded_composition` take emission
  BEFORE root (set constructors fire `on_mutation` while the root lock is held), so a
  concurrent emission can no longer publish a torn or stale registry around
  hydration/creation.
  EVIDENCE: src/melder/mutation_research/mutation_research.py:590,668,3380
Key Files (C1):
- `src/melder/mutation_research/mutation_research.py`
- `src/melder/mutation_research/mutation_configuration.py`
- `src/melder/mutation_research/mutation_configuration_builder.py`
- `src/melder/mutation_research/synthesis/structural_synthesizer.py`

### Subcomponent: MutationResearch ResearchSet Package
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Hold one research network as the graph of candidate runtime futures:
  full-object version records organized into lanes, forward-only history,
  and a version-controlled organization (drawn from git, deliberately NOT
  git - no merge/rebase/checkout machinery exists).
Contract/Interface:
- `ResearchSet` facade: `register_spell` (world-entry declaration; the SHA is
  simultaneously the custody `SpellCrystal` id), `create_lane` (optionally
  anchored), `attach`/`detach` (ancestry organization only), `join`
  (divergence-aware finisher; clean fast-forward auto, anything else needs
  `force=True`; `collapse=True` moves tip-only; source lane goes terminal),
  `archive` (default lane never archives), `walk`/`history`/`heads`,
  `snapshot_network`/`restore_network` (organization rewinds; the journal
  NEVER does), `describe_composition()`/`from_payload()` (persistence seam).
- `ResearchLane`: open -> joined | archived; ordered nodes; anchor;
  set-internal `_detach_nodes` powers join transfer. GOVERNANCE
  (single-residence law, BUG-048 2026-07-18): lanes are handed out LIVE as read
  surfaces - every lane mutator is set-internal (`_add_node` / `_detach_nodes` /
  `_set_anchor` / `_mark_joined` / `_mark_archived`), so residence claims, the
  journal, snapshots, and persistence emission cannot be bypassed through a
  publicly returned lane object; public state change flows through set verbs ONLY.
  EVIDENCE: src/melder/mutation_research/research_set/research_lane.py:386-592 Lane TYPE vocabulary (2026-07-11,
  salvaged May classification): `LaneType` enum
  (development/experiment/production/test) - names stay freeform, the type
  is the policy word; freeform lanes default `experiment`, the guaranteed
  default lane is `development`; the type rides describe/from_payload
  (back-compat: pre-vocabulary payloads hydrate by that same rule),
  lane_created journal metadata, history/residency/impact join rows, and
  the room `research_create_lane(lane_type=)` command. The ONLY policy
  hook is the set's join gate (armed via `lane_type_enforcement`): a
  type-mixing join then needs the same force=True supersede the
  divergence law uses.
- `ResearchNode`: immutable reference-based record (spell_id + module_source_sha256 +
  parent ancestry; multi-parent = codegen-workshop composition).
- `GroupedResearchNode` (2026-07-11 owner ruling: its OWN node type, never
  an optional field on ResearchNode; duplication between the families
  accepted - both first-class): immutable COMPOSITION record pinning
  member spell_ids by reference; identity = content-addressed sha256 over
  the canonical (deduped, sorted) member list (identical roster = same
  identity = rediscovery); parent_group_ids = composition ancestry (own
  namespace); PURELY INFORMATIONAL (no custody crystal, no gating, never
  executes); payloads carry node_type="group" (untagged = spell node,
  back-compat by absence) + recorded-id integrity check on hydration. A
  lane of group nodes is a subsystem's timeline; lanes carry both
  families through the module-level `node_identity()` dispatch; journal
  acts group_registered/group_recomposed (composition sha in to_spell_id,
  roster+ancestry in metadata); set verbs register_group (members must be
  resident - the parents law) and recompose_group (iterate-and-add: new
  node into the SAME lane, parents=[previous]); ROOT facades
  register_group/recompose_group apply the AMBIENT CAMPAIGN stamp (parity
  law: compositions through the root stamp like runtime auto-records;
  explicit wins; rooms route through the facades), stamped compositions
  appear in campaign_view nodes beside stamped spells, and spell-grain
  custody reads pointed at a composition id refuse TEACH-GRADE (naming
  the grain + the composition reads) via _get_spell_crystal_for_read
  instead of a raw custody KeyError. POLYMORPHIC VERBS (2026-07-12 owner
  correction - one vocabulary, no redirects): the ORDINARY spell-grain
  verbs dispatch on node kind - source_view/parts_view/module_graph_view/
  module_view FAN OUT per member, part_view roster-searches first-hit
  naming the carrying member, impact_view on a composition id answers the
  group radius, diff_research on two compositions routes through the
  members engine (mixed pair refuses - no shared grain), part_diff sides
  accept composition ids (verdict names left/right members); only the
  code-grain verbs (preview-against, synthesize) refuse composition ids,
  teaching the member descent. Grouped behavior = the
  MIRRORED strategy system: group_diff/ package (GroupDiffEngine +
  GroupDiffStrategy + default MemberDiffStrategy "members": added/removed
  members + LANE-EVIDENCED version_moved pairing - never guessed) beside
  diff/. Root reads: group_view (roster + behind drift vs member lane
  tips), group_diff_research, group_impact_view (union member radii,
  internal/outbound split, CLOSURE fraction, affected_compositions
  adjacency lift), group_footprint_view (the physical shadow: union of
  member module worlds, shared-module coupling map, honest
  custody-less members), group_drift_view (the full custody drift report
  NARROWED to the footprint, counts recomputed over the subsystem),
  group_history_view (journal events touching the subsystem lane, the
  pinned members, or the members' lanes - the area's story in journal
  order), and compositions_of (the REVERSE LIFT: which current lane-tip
  compositions pin a spell; surfaced on every spell's residency_view as
  `pinned_by_compositions`); residency_view is kind-aware (group =
  runtime "informational", no custody/frame probes). Twin/bootloader:
  compositions ride lane payloads through the twin, snapshots, restore,
  and load_recorded_composition unchanged; the MRCompositionStrategy
  preflight dispatches on node_type (group identities join residence
  agreement; pinned members absent from residence warn as drift).
  EXPLICIT TWIN OBJECTS (2026-07-12 owner ruling): MutationResearchCrystal
  derives flat, value-typed, DB-storable rows for BOTH node families
  (`research_nodes` / `grouped_research_nodes`, each row carrying its
  set/lane context) from the composition AT CONSTRUCTION - blob and
  objects structurally cannot disagree; describe() carries both; storage
  handlers map the lists straight to tables; hydration keeps reading the
  composition. DOCKING-LOOP LAW (2026-07-12 live-bug fix, caught by the
  zero-mock rebirth test): MutationResearchConfiguration.activate()
  CARRIES the recorded composition FORWARD into its twin - replace-on-emit
  would otherwise wipe the record moments before virgin hydration reads
  it (config activation necessarily precedes root activation); the
  configuration owns only its property payload.
- `TransitionEntry`/`TransitionAct`: immutable world-entry events
  (lane_created/registered/staged/promoted/attached/detached/joined/
  archived/restored; NO rollback acts by design).
- Runtime-seam verbs (2026-07-11): `record_world_entry` (idempotent; the
  spellbook bind/bind_inactive seams call it on every dynamic-lane world
  entry once the root is active - rediscovery is a quiet None) and
  `record_promotion` (journal-only notch record; undeclared targets are
  declared first at the root facade). Spellbook side:
  `_record_research_world_entry` / `_record_research_promotion` peek the
  Aether-hosted root WITHOUT constructing it and no-op unless it is live.
- Residency + campaign (2026-07-11): root `residency_view(spell_id)` performs
  the query-time join the model promises - declared truth (residence + lane),
  runtime truth (frame scan via `find_index_for_spell`; selected member ->
  `active`, unselected member -> `parked`), custody probe (`stored`;
  dead/inactive crystallizer -> honest None) - a TOTAL read (only an empty id
  refuses). Root `set_active_campaign`/`clear_active_campaign`/
  `active_campaign` stamp every runtime auto-record until cleared (explicit
  stamps win); `ResearchSet.campaign_view(campaign)` gathers stamped nodes +
  events in DECLARATION ORDER (journal-driven; deterministic - lane-order
  iteration was a ULID same-millisecond tie-break flake, fixed).
- Persistence extras (2026-07-11): the composition payload carries the
  NetworkVersioner undo ring (`"network_versioner"` key), so
  `restore_network` reaches pre-death organization states after hydration or
  engine reload; the twin journal window stays bounded at 200 (owner P1
  precedent; full history rides the checkpoint sequence). `restored` journal
  events carry the snapshot address in `metadata["snapshot_address"]`.
- Threadsafety (2026-07-11, no-GIL hardening; emission hop added 2026-07-18,
  BUG-031): lock order is one-way
  spellbook -> emission -> root -> set -> child/crystallizer; every set verb notifies
  AFTER releasing its lock (no AB-BA against the root->set emission read).
  Failure compensation closes the two real races: a refused `add_node` after
  a residence claim rolls the claim back (private `_rollback_claim`; the
  public no-release law stands), and a mid-loop join refusal restores ALL
  detached nodes to the still-open source in original order (residence
  transfers only after every add). Proven by an 8-thread stress run: 960
  identities, 61 lanes, gapless journal, residence exactly equal to lane
  holdings.
- USER SURFACE (2026-07-11): the Rift rooms - CodegenCommandSystem owns the
  full 34-command `research_*` family (14 record/organization/campaign
  incl. the research_recent cold-landing read + 9
  foresight incl. the crystal-well module/part reads and the codegen-only
  `research_preview` + 3 synthesis + 8 composition:
  research_group_register/recompose/view/diff/impact/footprint/drift/
  history),
  CapabilityCommandSystem the twenty-one reads (seven record + eight
  foresight + six composition),
  `ViewSpell.describe_spell_research` / `describe_spell_source` annotate
  visible spells with research residency and recorded module source, and
  `Conduit.get_mutation_research()` is DELETED (2026-07-12: replaced by the
  borrowed `Conduit.mutation_research` / `Spellbook.mutation_research`
  accessor doors returning the world root - patch
  mutation_research_accessor_doors_2026_07_12). Both rooms ADVERTISE the
  family through `list_supported_command_methods` (discoverability law).
- `ResearchJournal`: monotonic append-only; bounded describe window;
  `from_payload` continues minting without sequence reuse.
- `ResidenceRegistry`: SINGLE RESIDENCE invariant - one SHA lives in exactly
  ONE lane network-wide, permanently; claim collisions raise the rediscovery
  signal naming the holding lane; no release verb exists.
- `NetworkVersioner`: content-addressed (canonical-JSON SHA256) organization
  snapshots with dedupe and a FIFO retention ring.
Data Structures:
- Per set: lanes by id + name index, one journal, one residence partition,
  one snapshot ring, one optional `on_mutation` callback.
Concurrency/Threading:
- Instance RLock per structure; entries/nodes are immutable value objects.
Key Files (C1):
- `src/melder/mutation_research/research_set/research_set.py`
- `src/melder/mutation_research/research_set/research_lane.py`
- `src/melder/mutation_research/research_set/research_node.py`
- `src/melder/mutation_research/research_set/transition_entry.py`
- `src/melder/mutation_research/research_set/research_journal.py`
- `src/melder/mutation_research/research_set/residence_registry.py`
- `src/melder/mutation_research/research_set/network_versioner.py`

### Subcomponent: MutationResearch Configuration
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Hold mutation-research-wide policy before the hosted root is activated.
Contract/Interface:
- `set_property(...)`, `with_defaults()`, `with_unrestricted_module_mutations(...)`,
- `validate()`, `freeze()`, `finalize()`, `activate()`
Data Structures:
- `_properties`, `available_properties`, `_frozen`, `_activated`.
Concurrency/Threading:
- Instance `RLock`.
Key Files (C1):
- `src/melder/mutation_research/mutation_configuration.py`

### Subcomponent: MutationResearch Configuration Builder
Parent Component: Aether Singleton (Global Runtime)
Purpose:
- Own one mutable mutation-research configuration during assembly and hand it
  off through one-shot builder calls.
Contract/Interface:
- `with_defaults()`, `with_unrestricted_module_mutations(...)`,
- `build()`, `finalize()`, `activate()`
Data Structures:
- `_configuration`, `_id`.
Concurrency/Threading:
- Instance `RLock`.
Key Files (C1):
- `src/melder/mutation_research/mutation_configuration_builder.py`

### Subcomponent: Meld Execution Flow
Parent Component: Meld Resolution Runtime
Purpose:
- Resolve spells by id or normalized key, execute hooks, and register instances.
Contract/Interface:
- `Meld.meld(spell_name=..., spell=..., spellframe=..., binding_name=..., spell_override=...)`.
Data Structures:
- Spellbook lookup maps and creation manager.
Concurrency/Threading:
- Meld RLock.
Key Files (C1):
- `src/melder/aether/conduit/meld/meld.py`

### Subcomponent: Meld Runtime Gating
Parent Component: Meld Resolution Runtime
Purpose:
- Enforce spell validity and change-control gating before execution.
Contract/Interface:
- `Meld._ensure_lineage_resolvable(...)` and `Meld._gated_validation_required(...)`.
Data Structures:
- SpellSystemStates lineage validity and change-control dirty-root state.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`

### Subcomponent: Creations Disposal Pipeline
Parent Component: Creations and SpellSpace
Purpose:
- Dispose instances across all existence categories in order.
Contract/Interface:
- `Creations.cleanup()`.
Data Structures:
- Existence maps for unique/many/scope.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`

### Subcomponent: LesserCreations Transfer
Parent Component: Creations and SpellSpace
Purpose:
- Historical transfer slot retained for continuity; current runtime performs
  in-place Creations rebinding during conduit upgrade.
Contract/Interface:
- `Conduit.upgrade_to_normal(...)` rebinding of the current `Creations`
  manager (`_conduit`, `_conduit_state`) and meld rewiring.
Data Structures:
- Current `Creations` manager references carried across lesser->normal state change.
Concurrency/Threading:
- Conduit lock during upgrade.
Key Files (C1):
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/creations/creations.py`

### Subcomponent: SpellSpace Scope Gate
Parent Component: Creations and SpellSpace
Purpose:
- Enforce spellspace activation for unique_per_spell_space.
Contract/Interface:
- `SpellSpace.meld()` checks active scope and delegates to Conduit.
Data Structures:
- SpellSpace id and version counter.
Concurrency/Threading:
- No explicit lock; owner Conduit lock used upstream.
Key Files (C1):
- `src/melder/aether/conduit/spell_space/spell_space.py`

### Subcomponent: SpellSystemStates Registry
Parent Component: DevOps Control Plane
Purpose:
- Track lineage validity, dependencies, dirty sets, and per-conduit resolution state.
Contract/Interface:
- `register_lineage`, `update_dependencies`, `consume_dirty_lineages`.
- `get_or_create_conduit_resolution_state`, `set_conduit_spell_validity`,
  `record_conduit_diagnostics`.
- `unregister_lineage` removes lineage state and notifies RiskManager with
  SpellValidity.cleaned to force validation gating. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:unregister_lineage.
Scope:
- Per-frame structural state with per-conduit resolution state keyed by conduit_id. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:__init__ + get_or_create_conduit_resolution_state.
Data Structures:
- `_states_by_index_id`, `_dirty_lineages`, `_resolution_by_conduit_id`.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`

### Subcomponent: Conduit Resolution State
Parent Component: DevOps Control Plane
Purpose:
- Track per-conduit resolution validity and diagnostics for Phases 5-11.
Contract/Interface:
- `get_spell_validity`, `set_spell_validity`, `get_root_validity`, `set_root_validity`,
  `record_diagnostics`, `mark_dirty`, `clear_dirty`.
Data Structures:
- `_spell_validity`, `_root_validity`, `_diagnostics`, `_dirty`,
  `_last_validated_at`, `_last_change_reason`, `_initial_validity`.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py`

### Subcomponent: ChangeControl Dirty Roots
Parent Component: DevOps Control Plane
Purpose:
- Track pending changes and dirty roots for revalidation.
Contract/Interface:
- `register_pending_change`, `is_root_dirty(conduit_id, root_id)`, `revalidate_dirty_roots(conduit_id, ...)`.
Scope:
- Per-conduit dirty roots and component-of mapping keyed by conduit_id within a frame. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:__init__ + rebuild_component_of.
Data Structures:
- `_pending_changes`, `_dirty_roots_by_conduit`, `_component_of_by_conduit`.
Concurrency/Threading:
- RLock.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`

### Subcomponent: Change-Control Revalidation
Parent Component: DevOps Control Plane
Purpose:
- Invoke revalidator for dirty roots and clear dirty flags on success.
Contract/Interface:
- `revalidate_dirty_roots(conduit_id, ...)` and `is_root_dirty(conduit_id, root_id)`.
Scope:
- Conduit-scoped revalidator invoked by ChangeControlManager; meld gating reads
  `is_root_dirty(conduit_id, root_id)` in `Meld._gated_validation_required`
  via the Aether change-control manager. EVIDENCE:
  src/melder/aether/conduit/meld/meld.py:_gated_validation_required +
  src/melder/aether/aether.py:_get_change_control_manager.
Data Structures:
- Dirty roots/spells and component-of maps keyed by conduit_id.
Concurrency/Threading:
- ChangeControlManager lock; revalidator called outside lock.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`

### Subcomponent: Transaction Strategy Registry
Parent Component: Transaction Admission Plane (Scope Acquisition)
Purpose:
- Resolve one transaction kind into the concrete strategy class that owns its
  planning and local start/end behavior.
Contract/Interface:
- `register_strategy(...)`, `resolve(...)`
- `build_start_plan(...)`, `on_start(...)`, `on_end(...)`,
  `apply_commit_delta(...)`
Data Structures:
- `_strategies_by_transaction_name`
- borrowed `ChangeControlTransactionManager` and `DevopsInformationRegistry`
Concurrency/Threading:
- Read-only during normal runtime use after default registration.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py`

### Subcomponent: Transaction Strategy Families
Parent Component: Transaction Admission Plane (Scope Acquisition)
Purpose:
- Provide the concrete family-specific planning rules for structural mutation
  transactions admitted by the mediator.
Contract/Interface:
- `BindTransactionStrategy`: pre/post-conjure bind planning
- `LinkTransactionStrategy`: conduit-link planning
- `UnlinkTransactionStrategy`: sever-link planning
- `ClusterLinkTransactionStrategy`: cluster share/unshare planning
- `TransferOwnershipTransactionStrategy`: ownership-transfer planning
- `AddToIndexTransactionStrategy`: move spell into target index
- `RemoveFromIndexTransactionStrategy`: split spell out to fresh index
- `NotchTransactionStrategy`: intra-index active-member switch
Data Structures:
- family-specific normalized metadata, scope-key sets, scope-claim tuples,
  and affected-identity sets
Concurrency/Threading:
- Static class methods only; strategy execution borrows mediator-held
  collaborators.
Key Files (C1):
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unlink_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/cluster_link_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/add_to_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/remove_from_index_transaction_strategy.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py`

### Subcomponent: SafeLogger Adapter
Parent Component: Logging and Initialization Helpers
Purpose:
- Normalize logging for stdlib and channel loggers.
Contract/Interface:
- `SafeLogger.debug/info/warning/error/critical`.
Data Structures:
- `_logger`, `_level`, `_level_name`.
Concurrency/Threading:
- No internal lock.
Key Files (C1):
- `src/melder/utilities/logger/safe_logger.py`

### Subcomponent: AetherUtilitySystem Provider Host
Parent Component: Logging and Initialization Helpers
Purpose:
- Hold the process-wide logger provider registrations used by runtime objects.
Contract/Interface:
- `register_channel_logger_resolver`, `register_default_logger`,
  `resolve_safe_logger`, `resolve_channel_logger`.
Data Structures:
- `_channel_logger_resolver`, `_default_logger`.
Concurrency/Threading:
- Singleton lock plus instance `RLock`.
Key Files (C1):
- `src/melder/aether/aether_utility_system.py`

### Subcomponent: Nexus Frame Registry and Access Policy
Parent Component: AR Runtime Surface (Nexus, Rift, RiftSpace)
Purpose:
- Realize Nexus-managed frames and enforce shared/indexed/one-per-workspace
  access policy.
Contract/Interface:
- `get_nexus_frame_for_rift`, `create_nexus_frame_for_rift`,
  `list_accessible_nexus_frame_names`.
Data Structures:
- `_frame_manager`, `_rifts_by_id`, `_rift_ids_by_name`,
  `_rift_profiles_by_name`, and `_target_frame_ref_counts`.
Invariants/Guarantees:
- Rift creation itself is frame-free.
- Nexus-managed frames are realized only through explicit frame access/create
  requests, with topology policy applied at request time.
- Nexus-facing managed create/get paths return the rooted conduit for the
  frame, not the frame object.
- `create_nexus_frame_for_rift(...)` is strict-create and raises when the
  resolved target frame already exists.
- `get_nexus_frame_for_rift(...)` is the recovery path for existing managed
  frames.
- Nexus-facing creation uses `Spellbook(...).conjure(...)` to realize the
  frame/workspace instead of injecting configuration straight into the frame
  and rooting it later.
- Raw `NexusFrameManager` creation follows the same mode contract:
  - `single` allows only the canonical shared frame name
  - `indexed` allows explicit named direct creation
  - `one_per_workspace` rejects direct manager creation in favor of the
    Rift-scoped create path
Concurrency/Threading:
- `Nexus` instance `RLock`.
Key Files (C1):
- `src/melder/nexus/nexus.py`
- `src/melder/nexus/nexus_frame_manager.py`
- `src/melder/nexus/configuration/nexus_frame_mode.py`

### Subcomponent: NexusFrameBuilder Authored Frame Surface
Parent Component: AR Runtime Surface (Nexus, Rift, RiftSpace)
Purpose:
- stage one Nexus-managed frame configuration through a fluent builder-owned
  surface before rooted creation
Contract/Interface:
- `NexusFrameManager.begin(frame_name)` returns `NexusFrameBuilder`
- `build()` returns one detached `NexusFrameConfiguration`
- `create()` delegates manager-owned rooted realization and returns `IConduit`
Invariants/Guarantees:
- defaults to `dynamic + ai_native_enabled + rift_enabled`
- root conduit defaults to `"root"` unless explicitly overridden
Key Files (C1):
- `src/melder/nexus/nexus_frame_builder.py`
- `src/melder/nexus/nexus_frame_manager.py`

### Subcomponent: Frame Descriptor Publication Manager
Parent Component: Nexus Descriptor And ACL Managers
Purpose:
- Own frame-scoped descriptor aggregates and canonical record publication.
Contract/Interface:
- `_get_or_create_frame_descriptor`, `_refresh_frame_posture_cache`,
  `_publish_frame_record`, `_publish_conduit_record`, `_publish_spell_record`,
  and corresponding remove helpers.
Data Structures:
- `_frame_descriptors_by_name`, `FrameDescriptor`, `FrameRecord`,
  `ConduitRecord`, `SpellRecord`.
Concurrency/Threading:
- Manager instance `RLock`.
Key Files (C1):
- `src/melder/nexus/frame_descriptor_manager.py`

### Subcomponent: Frame ACL Manager
Parent Component: Nexus Descriptor And ACL Managers
Purpose:
- Own frame-local ACL containers and profile registries.
Contract/Interface:
- `_ensure_frame_acl_container`, container/profile lookup helpers, and
  frame-level ACL change callback fan-out through `Nexus`.
Data Structures:
- `_frame_acl_containers_by_name`, `_frame_acl_profiles_by_name`,
  `FrameACLContainer`.
Concurrency/Threading:
- Manager instance `RLock`.
Key Files (C1):
- `src/melder/nexus/frame_acl_manager.py`

### Subcomponent: Frame ACL Builder Surface
Parent Component: Nexus Descriptor And ACL Managers
Purpose:
- own one active family-draft session across view, command, or codegen ACL
  chains for a frame-local container
Contract/Interface:
- `begin_view_change(...)`
- `begin_command_change(...)`
- `begin_codegen_change(...)`
- `apply_frame_acl_profile(...)`
- `load_json_configuration_string(...)`
- `commit_change()` / `discard_change()`
Invariants/Guarantees:
- at most one draft session is active at a time
- final install is delegated to the owning `FrameACLContainer`
Key Files (C1):
- `src/melder/nexus/acl/builder/frame_acl_builder.py`

### Subcomponent: Rift Single Space And Event Seam
Parent Component: AR Runtime Surface (Nexus, Rift, RiftSpace)
Purpose:
- Own the one primary room, per-frame contract set, per-Rift gate, and the
  refresh orchestration that keeps Rift-owned projection state and hosted room
  assets in sync.
Contract/Interface:
- `space`, `list_assigned_frame_names`, `get_selected_contract_names(...)`,
  `create_frame_link(...)`, `refresh_runtime_projections(...)`, `get_frame_viewer()`,
  and `event_configuration`.
Data Structures:
- one owned `_space`, `_is_registered`, `_is_active`, `_metadata`, one
  `FrameLinkContract` per engaged frame, one `RiftGate`, plus the room-local
  `_event_configuration`.
Concurrency/Threading:
- `Rift` uses an `RLock`; `RiftSpace` also now owns an `RLock` because it
  manages attached viewer state, event-system state, memory-system state,
  workstation state, and command-system state.
Key Files (C1):
- `src/melder/nexus/rift/rift.py`
- `src/melder/nexus/rift/rift_space/rift_space.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event_system.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event.py`
- `src/melder/nexus/rift/rift_space/static_rift_space.py`
- `src/melder/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/nexus/rift/rift_space/capability_rift_space.py`

### Subcomponent: RiftSpace Workstation
Parent Component: RiftSpace Workstation And Command Surface
Purpose:
- Store room-local strong/weak bindings and one active target.
Contract/Interface:
- `bind_object`, `bind_attribute`, `bind_method`, `set_target`,
  `cleanup_target`, and `call_target`.
Data Structures:
- Strong/weak object, attribute, and method stores plus target name/store.
Concurrency/Threading:
- Workstation instance `RLock`.
Key Files (C1):
- `src/melder/nexus/rift/rift_space/workstation.py`

### Subcomponent: Rift-Backed Frame Viewer Surface
Parent Component: AR Runtime Surface (Nexus, Rift, RiftSpace)
Purpose:
- Expose descriptor-host and frame-local viewer behavior over current
  Rift-owned view projections.
Contract/Interface:
- `FrameViewer` holds one borrowed `Rift` reference and resolves current
  `ViewProjection` objects on demand.
- `ViewMultiFrame` owns cross-frame descriptor inventory and comparison logic.
- `ViewFrame`, `ViewConduit`, and `ViewSpell` provide frame-local helper
  surfaces.
- `ViewSpell.describe_spell_research(...)` (2026-07-11) joins viewer truth
  with the research record: identity read -> spell_id -> non-constructing
  `Aether._instance` peek -> residency payload (declared/lane/runtime/
  custody) stamped `research_available=True`, or an honest
  `research_available=False` / `mutation_research_not_active` payload -
  viewing a spell never fails on research state.
- Frame-local operations require explicit `frame_name`; there is no
  default-frame routing contract.
Data Structures:
- viewer id, borrowed Rift reference, and on-demand helper instances.
Concurrency/Threading:
- `FrameViewer` and the frame-local helpers use instance `RLock` discipline.
Key Files (C1):
- `src/melder/nexus/rift/frame_viewer/frame_viewer.py`
- `src/melder/nexus/rift/frame_viewer/view_multiframe.py`
- `src/melder/nexus/rift/frame_viewer/view_frame.py`
- `src/melder/nexus/rift/frame_viewer/view_conduit.py`
- `src/melder/nexus/rift/frame_viewer/view_spell.py`
- `src/melder/nexus/rift/frame_viewer/static_frame_viewer.py`

### Subcomponent: RiftSpace Command System
Parent Component: RiftSpace Workstation And Command Surface
Purpose:
- Mediate frame-scoped runtime-object access and workstation-target execution,
  while room-specific subclasses own non-shared public commands.
Contract/Interface:
- Shared base:
  spell lookup helpers, runtime/query helpers, and
  `execute_target_method(...)`.
- Capability-owned:
  conduit discovery, link/contract-topology helpers, topology helpers, plus
  `meld(...)` and `meld_existing_spell(...)`.
- Static-owned:
  live-only spell retrieval, `meld_existing_spell(...)`, and static
  spell-status helpers.
Data Structures:
- Owning room reference and room-local workstation reference.
Concurrency/Threading:
- Command-system instance `RLock`.
Key Files (C1):
- `src/melder/nexus/rift/command_system/command_system.py`
- `src/melder/nexus/rift/command_system/static_command_system.py`
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `src/melder/nexus/rift/command_system/codegen_command_system.py`

### Subcomponent: CodegenSystem Internal Engine
Parent Component: Codegen Internal Engine
Purpose:
- own transaction construction plus validator, namespace, compiler, executor,
  and monitor collaborators for one codegen room
Contract/Interface:
- `validate_codegen_request(...)`
- `execute_codegen_request(...)`
- `_build_transaction_context(...)`
- `_build_namespace(...)`
Invariants/Guarantees:
- validation precedes execution
- namespace is built only after accepted validation
Key Files (C1):
- `src/melder/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/nexus/rift/rift_space/codegen_rift_space.py`

### Subcomponent: SpellExaminer Profile Registry
Parent Component: Spell Examination Profiles
Purpose:
- Resolve named profile builders and emit cleanable general/detailed spell
  examination profiles.
Contract/Interface:
- `register_profile_builder`, `list_profile_builder_names`, `create_profile`.
Data Structures:
- Builder registry plus emitted
  `SpellGeneralProfile` / `SpellDetailedProfile` objects.
Concurrency/Threading:
- Synchronous builder dispatch only; no independent worker model.
Key Files (C1):
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/spell_examiner.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/general_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/detailed_profile.py`

## Method-Level Call Flows (C1)
These flows describe concrete method sequences for core behaviors.

### Flow: Import -> Runtime Guardrails
1. `import melder`:
   - `melder/__init__.py` checks Python version and warns if < 3.13.
   - `_detect_nogil_mode()` calls `sys._is_gil_enabled()` and warns if GIL on.
   - `__melder_registration_guard__` singleton is instantiated.

### Flow: Spellbook Init -> SpellbookConfiguration and Logging
1. `Spellbook.__init__`:
   - Ensures Aether frame exists via `_ensure_frame`.
   - `_initialize_configuration` adopts or creates `SpellbookConfiguration`.
   - `_initialize_logging` resolves SafeLogger through
     `InitHelpers` + `AetherUtilitySystem`.
   - Initializes registries and SpellValidationSystem.

### Flow: Aether Boot -> Utility Host, Crystallizer, and Nexus
1. `Aether.__init__`:
   - Seeds a null SafeLogger.
   - Creates `AetherUtilitySystem`.
   - Creates or recovers the hosted `Crystallizer`.
   - Creates or recovers `Nexus`.
   - Does not attach a real logger during boot; later logger attachment is
     explicit through `attach_logger(...)`.
   - Automatic channel logger activation remains disabled until Aether-owned
     config enables it.

### Flow: Nexus.create_rift -> Frame Policy -> Rift Registration
1. `Nexus.create_rift(...)`:
   - Clones/consumes a finalized `RiftConfiguration`.
   - Constructs a bare `Rift` with one primary room from `space_type`.
   - Registers the live Rift in Nexus without requiring an initial target frame.
2. `Rift.create_frame_link(frame_name)`:
   - Validates target-frame policy and room-type eligibility through `Nexus`.
   - Requires descriptor truth for the requested frame.
   - Delegates Nexus-managed frame authorization back through `Nexus` when the
     target frame is Nexus-managed.
   - Ensures the frame-name ACL contract exists for the frame.
   - Updates the frame contract and synchronizes the durable room-owned viewer.

### Flow: Codegen Room Init -> Attach Internal Engine
1. `CodegenRiftSpace.__init__(...)` delegates base room setup to `RiftSpace`.
2. `CodegenRiftSpace` constructs one owned `CodegenSystem`.
3. `CodegenRiftSpace` attaches that engine to the room-owned
   `CodegenCommandSystem`.
4. Later room-facing validate/execute commands reuse the attached engine.

### Flow: Frame ACL Family Revision -> Viewer Refresh
1. One view/command/codegen family chain inside the frame ACL container
   advances or changes current selection.
2. The frame ACL container emits a frame-level ACL change callback.
3. `FrameACLManager` forwards that through `Nexus`.
4. `Nexus` finds impacted Rifts by checking whether the changed frame is
   present in each Rift's assigned frame-contract set.
5. By default, `NexusConfiguration` enables RiftGate-controlled refresh:
   - disable the impacted Rift gates
   - wait for in-flight tickets to drain
   - delegate the single-frame callback into the batch refresh primitive
   - refresh each impacted Rift once for its changed-frame subset
    - apply the refreshed projection state to the durable room viewer and
      room-owned command assets
   - reopen the impacted Rift gates
   The same config owns the drain timeout and poll interval.
6. Each impacted `Rift` asks `Nexus` for one refreshed multi-frame projection
   subset, merges it into the Rift-owned projection registry once, and then
   applies the refreshed projection state to its hosted viewer and command
   assets.

### Flow: FrameDescriptorManager Passive Publication
1. `Nexus` or a runtime publisher delegates frame/conduit/spell publication.
2. `FrameDescriptorManager` refreshes frame posture and frame-handle cache.
3. The manager publishes or replaces the canonical frame/conduit/spell record
   inside the owned `FrameDescriptor`.
4. Removal helpers delete canonical records without mutating the Rift registry.

### Flow: RiftSpace Workstation Bind -> Target -> Call
1. `Workstation.bind_object(...)`, `bind_attribute(...)`, or `bind_method(...)`
   stores one binding using explicit or default strong/weak mode.
2. `set_target(...)` marks one stored binding as the active target.
3. `call_target(...)` invokes the current callable target and may bind the
   result back into the workstation.
4. `cleanup_target(...)` acts only on the current target and then clears target
   selection.

### Flow: RiftSpace Command Surface -> Runtime Operation
1. `CommandSystem` resolves frame-scoped records and compiled command ACL state
   through the room-owned command projection.
2. The shared base command layer returns shared records/runtime objects or
   executes one shared target/workstation operation.
3. Room-specific command subclasses own any extra runtime operations that do
   not belong to every room, including conduit discovery on capability and the
   static spell-status/reuse surface on static.
4. Optional results are rebound into the workstation through `_bind_result(...)`
   when the caller requests room-local persistence.

### Flow: Codegen Command -> Engine Delegation -> Memory Emission
1. `CodegenCommandSystem.validate_codegen(...)` or `execute_codegen(...)`
   validates inputs and enters the room action-hook scope.
2. The command facade begins one command action and acquires the RiftGate
   ticket.
3. The facade requires the attached `CodegenSystem` and delegates into
   `validate_codegen_request(...)` or `execute_codegen_request(...)`.
4. `CodegenSystem` builds the transaction context and, on the execute path,
   validates before building the namespace and compiling/executing code.
5. The command facade unregisters the RiftGate ticket and emits the
   full-source codegen room-memory record when room memory is enabled.

### Flow: Bind Spell -> SpellIndex and SpellSystemStates
1. `Spellbook.bind(...)`:
   - Converts permissions and existence enums.
   - Calls `Bind._bind_logic` to create SpellIndex and Spell.
   - Attaches hooks and registers local lookup keys.
   - Registers lineage in SpellSystemStates (marks dirty).
   - If Conduit exists, stamps ownership and registers existing objects into Creations.

### Flow: Conjure -> Phases -> Conduit
1. `Spellbook.conjure(...)`:
   - Validates and freezes `SpellbookConfiguration`.
   - Binds `SpellbookConfiguration` to Aether frame.
   - Runs phases 1-4 via PhaseScheduler.
   - Runs phases 5-7 via PhaseScheduler (foundational conduit resolution).
   - Runs phases 8-11 via PhaseScheduler only when phases 5-7 report no
     resolution errors.
   - Live 8-11 output contract:
     - phase 8 `_occurrence_graph_analysis`
     - phase 9 `_spell_codegen_model`
     - phase 10 `_spell_codegen_plan`
     - phase 11 `_spell_codegen_creation`
   - Constructs a normal Conduit and registers it with Aether.
   - Fires pre/activated/post hooks and wires Conduit into spells.

### Flow: Conduit.meld -> Meld -> CreationContext -> Creations
1. `Conduit.meld(...)` validates identity inputs, fires pre-resolve hook, and delegates to Meld.
2. `Meld.meld(...)` normalizes `spell_override` (dict/list/tuple) into a map.
3. `Meld._resolve_spell(...)` resolves by spell_id (string `spell`) or by lookup key derived from `spell_name`/`spellframe`/`binding_name` via SpellInputUtils.
4. `Meld` gates validity (`_ensure_lineage_resolvable`) and executes pre-cast hooks.
5. Meld resolves or creates the instance (reuse via Creations; otherwise
   `CreationContextBuilder` consumes `_spell_codegen_creation` and returns a
   spell-bound `CreationContext` for class/method/lambda spells).
6. Creations registers newly created instances per Existence semantics.
7. `Conduit.meld(...)` fires post-resolve hook.

### Flow: Conduit.has_live_creation -> Meld Probe
1. `Conduit.has_live_creation(...)` or `describe_live_creation_status(...)`
   delegates to the owned `Meld` component.
2. `Meld._resolve_spell_for_live_creation_probe(...)` resolves the spell the
   same way `meld(...)` would.
3. `Meld._describe_spell_live_creation_status(...)` inspects live runtime
   storage only and returns presence/scope/count information without creating
   anything.

### Flow: SpellMap Default Resolution (Phase 3)
1. SpellRequirementsFinder classifies a parameter default `SpellMap` as `ParameterDIShape.SPELLMAP_DEFAULT`.
2. `CompilerPhase3._resolve_spellmap_default(...)` prefers an explicit `spell`
   target, then frame+binding lookup by iterating Spellbook `_spell_id_pool`.
3. Zero candidates raises RuntimeError; multiple candidates raise RuntimeError with disambiguation guidance.
4. The single resolved spell becomes the dependency target in the local resolution frame.

### Flow: Collection DI (list[FrameType])
1. SpellRequirementsFinder classifies `list[FrameType]` as `ParameterDIShape.COLLECTION_BY_ANNOTATION`.
2. `CompilerPhase3._resolve_collection_by_annotation(...)` scans all spells and
   matches the frame annotation (methods/lambdas allowed).
3. The resulting candidate map (possibly empty) is injected as the collection dependency.

### Flow: Meld-Time Validation Gate
1. `Meld._ensure_lineage_resolvable(...)` checks SpellSystemState validity.
2. If validity is UNKNOWN/GATED:
   - `spell.run_structural_phases()` executes under the per-spell lock.
3. If per-conduit resolution validity is UNKNOWN/GATED:
   - `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)` executes.

### Flow: Create Lesser Conduit
1. `Conduit.create_lesser_conduit(...)` fires pre-create hook.
2. Constructs lesser Conduit with inherited Spellbook/`SpellbookConfiguration`.
3. Wires root Creations and root conduit into lesser conduit.
4. Links lesser into ConduitWard lineage tree.
5. Fires activated and post-create hooks.

### Flow: Upgrade Lesser Conduit -> Normal
1. `Conduit.upgrade_to_normal(name, hooks)` checks dynamic mode and lesser state.
2. Snapshots root conduit resolution state (if available).
3. Sets state to normal, assigns name, and initializes conduit hooks.
4. Rebinds the current `Creations` manager to the upgraded conduit state.
5. Rewires Meld to use the same `Creations` manager with updated resolution conduit id.
7. `ConduitWard._convert_to_normal_conduit()` detaches parent link and resets policy.
8. `Spellbook.create_new_preset_spellbook()` rebuilds spellbook internals.
9. Seeds conduit resolution state from the former root (best-effort).
10. Registers conduit in Aether and ConduitCloud (if named).
11. Registers upgrade-supplied hooks (if provided).

### Flow: Link Conduits (Dynamic)
1. `Conduit.link(target)` validates dynamic mode and target validity.
2. `ConduitWard._link(target)` enforces policy and avoids self/lesser links.
3. `ConduitWard._create_new_contract` uses SafeGuard to lock both wards.
4. Each Spellbook creates a link contract bucket.
5. `Conduit` fires `on_conduit_post_link` hooks on success.

### Flow: Sever Conduit Link (Dynamic)
1. `Conduit.sever_link(target)` validates dynamic mode.
2. `ConduitWard._sever_link(target)` removes the contract or raises if absent.
3. Each Spellbook severs its link contract bucket.
4. `Conduit` fires `on_conduit_post_unlink` hooks on success.

### Flow: Change-Control Revalidation
1. `CompilerPhase5` rebuilds `ChangeControlManager` component-of index for a
   conduit using owned roots only.
2. `CompilerPhase5` and `CompilerPhase7` register a conduit revalidator via
   `set_revalidator(conduit_id, ...)`.
3. `ChangeControlManager.revalidate_dirty_roots(conduit_id, ...)` copies dirty roots
   for that conduit and calls the revalidator outside the lock.
4. On success, dirty roots/spells are cleared and monitoring is disabled for that conduit.
5. `Meld` gates execution via `_gated_validation_required` +
   `is_root_dirty(conduit_id, root_id)`.

### Flow: Transfer Spell Ownership (Dynamic)
1. `Conduit.transfer_spell_ownership(...)` validates dynamic mode.
2. `TransferOfOwnership.preflight()` enumerates borrowers/deps/creations.
3. `TransferOfOwnership.execute()`:
   - Marks lineage disabled (transfer_in_progress).
   - Flips registries/spellbooks under SafeGuard lock.
   - Moves or tears down creations and adjusts contracts/clusters.
   - Marks lineage dirty/gated for revalidation.

### Flow: SpellSpace Scoped Meld
1. `conduit.enter_spellspace()` creates and activates a SpellSpace.
2. `SpellSpace.meld(...)` verifies it is the active scope.
3. Delegates to `Conduit.meld(...)` for resolution.
4. `SpellSpace.reset()` clears spellspace-scoped instances and increments version.

### Flow: SpellExaminer.create_profile -> General/Detailed Profile
1. `SpellExaminer.create_profile(target, profile=...)` resolves the named
   builder from the current registry.
2. The builder constructs the binding-side profile from the raw candidate or
   bound spell.
3. When the target is a live `Spell`, the profile completes with resolution
   data.
4. The `detailed` builder adds class and callable inspector payloads on top of
   the general profile contract.

### Mermaid: Conduit Upgrade
```mermaid
sequenceDiagram
  participant LC as Lesser Conduit
  participant CR as Creations
  participant M as Meld
  participant W as ConduitWard
  participant SB as Spellbook
  participant AE as Aether
  participant CC as ConduitCloud
  LC->>LC: upgrade_to_normal()
  LC->>CR: preserve + rebind current Creations
  LC->>M: rewire meld creations/resolution root id
  LC->>W: _convert_to_normal_conduit()
  LC->>SB: create_new_preset_spellbook()
  LC->>AE: _add_conduit()
  LC->>CC: _register_conduit() (if named)
```

### Mermaid: Conjure Pipeline
```mermaid
sequenceDiagram
  participant U as User
  participant SB as Spellbook
  participant PS as PhaseScheduler
  participant C as Conduit
  U->>SB: conjure()
  SB->>SB: validate/freeze config
  SB->>PS: phases 1-4
  SB->>PS: phases 5-7
  SB->>PS: phases 8-11 (if no resolution errors)
  SB->>C: Conduit(...)
  SB-->>U: Conduit
```

### Mermaid: Meld Runtime
```mermaid
sequenceDiagram
  participant C as Conduit
  participant M as Meld
  participant CC as CreationContext
  participant P12 as Phase12 Compiled Executors
  participant CR as Creations
  C->>M: meld(spell_id/input)
  M->>CC: get/build creation context
  M->>CC: invoke _execute_*_compiled(...)
  CC->>P12: dispatch compiled lane
  P12->>CR: reuse/construct/register
  P12-->>CC: instance
  CC-->>M: instance
  M-->>C: instance
```

### Mermaid: Ownership Transfer
```mermaid
sequenceDiagram
  participant SC as Source Conduit
  participant TC as Target Conduit
  participant TO as TransferOfOwnership
  participant AE as Aether
  SC->>TO: preflight()
  SC->>TO: execute()
  TO->>SC: disable lineage (transfer_in_progress)
  TO->>AE: flip registry + spellbooks (under SafeGuard)
  TO->>SC: move/teardown creations
  TO->>SC: unshare or repoint contracts
  TO->>SC: mark lineage dirty/gated
```

## C1 Code Map (Core)
- `src/melder/__init__.py` - runtime guardrails and metadata.
- `src/melder/__melder_registration_guard__.py` - internal registration guard.
- (TAIL REPAIR 2026-07-07, melder_0: this listing's remainder was lost to a
  historic mid-write truncation predating recoverable git history; the
  dangling fragment was closed here rather than guessed at.)

## Crystallizer Persistence & Restore (promoted from patch
## restore_engine_2026_07_07 + successor lanes, 2026-07-07)

Ownership hierarchy (owner-ruled; CURRENT as of the 2026-07-10 subsystem
decomposition - see the dated section at the end of this block):
`Crystallizer` owns THREE same-rank children - `PersistenceSystem` (the
record: profiles + checkpoint ledger, in-process truth ONLY),
`AssetManagementSystem` (bytes at rest: `CrystallizerCache`, formation
files, and the `ExternalPersistenceManager` DB seam), and
`CrystalLoaderSystem` (the unfold: LoadAdmission gating (renamed from
BootMediator 2026-07-11) + RestoreEngine +
durable load state). The twin vocabulary lives at package level
(`crystallizer/crystals/`) and `crystal_analysis/` is the shared analyzer
service. Users talk to `Crystallizer` facades only.

### Record model (EMIT)
- Twins are pure-data crystals (aether, crystallizer, nexus,
  mutation_research, frame, spellbook, conduit, spell_index, contract,
  cluster, spell custody) recorded replace-on-emit into the ACTIVE
  PersistenceProfile with an insertion-ordered journal (sequence, kind, key).
- Emission factors: configuration activation/freeze is each unit's emission
  moment. Three re-entry seams cover legally pre-frozen configurations
  (spellbook conjure re-freeze, nexus enable, aether root catch-up at
  crystallizer activation - the aether structurally precedes its recorder).
  AetherUtilitySystem mutation verbs re-emit the root twin so post-activation
  logger-policy flips never drift from the record.
- EVERY snapshot is self-describing (owner ruling): the crystallizer's own
  policy twin re-emits into each seal's window (`_emit_policy_twin`, direct
  record to keep the cadence ticker out of seal paths), so one cached
  crystal names the recording policy that made it.
- Capture (`capture_segment_since`): full current twins for identities
  journaled since the mark; spell custody payloads annotate
  `custody_location`; tombstone kinds carry synthetic removal payloads;
  state switches (nexus/MR) journal their flips.
- SpellCrystal carries the full bind signature (module coordinates,
  spellframe NAME, existence/permissions names, disposal_method_names,
  profile_family) - content-derived SHA256 ids are STABLE across restore.

### Checkpoints, cache, retention
- `create_checkpoint` seals the delta window into a PersistenceCrystal
  (ULID id; per-profile checkpoint_number minted highest+1 - count-based
  minting duplicated under FIFO dropout and was fixed). Ledger retention =
  `max_persistence_crystals` (FIFO dropout).
- `verify_checkpoint_chain(profile)` - read-only fold-safety verdicts:
  intact / truncated_prefix / broken / empty, with break evidence rows and
  empty-window tolerance; full-dropout restarts detected via the first
  retained window's start.
- CrystallizerCache: profile-scoped layout
  `__crystallizer_cache__/{profile}/{checkpoint_id}.json` (atomic
  tmp+replace; legacy flat paths tolerated on read);
  `enforce_cache_retention` FIFO-caps cached files at the checkpoint limit
  on every flush (no DB emitter -> bounded disk; deeper durability is the
  user's DB opt-in).
- `reload_checkpoint_from_cache` (one id) and `reload_profile_from_cache`
  (whole profile, insert-if-absent, idempotent) - a profile's cache folder
  IS its portable form.

### Restore (RestoreEngine, all-or-nothing)
- `load_checkpoint(id)`: the target's same-profile chain detaches under the
  system lock; the single-use engine runs OUTSIDE it (replay re-enters the
  emit path). Fold = oldest-first, later-wins per (kind, key), tombstones
  mirror live eviction match rules, custody routes on custody_location;
  journal-without-payload folds to an honesty shortfall, never silently.
- Canonical stage order (owner-ruled boot order):
  aether_configuration -> crystallizer_policy (boot-time report) ->
  mutation_research (report; excluded from restore) -> nexus (reload verb +
  public enable + lifecycle replay) -> frames (posture bind BEFORE books;
  frames own the dynamic gate) -> books/binds/conjure/staged/selections ->
  links -> clusters -> contracts LAST (borrower-called naming the owning
  side; details live in the lineage owner's map under both labels).
- Fresh identities always (old->new in the report's identity map; spell
  SHAs never translate). Failure = reverse-order teardown + chained
  RuntimeError. Shortfall ledger reports everything unreplayable (hooks,
  non-hydratable targets, cluster leadership, index subscriptions, MR).

### Configuration reload lanes (owner law: recorded truth, never defaults)
- Every configuration has a JSON-payload load-and-freeze reload verb:
  SpellbookConfiguration.load_recorded_dictionary,
  AethericFrameConfiguration.from_recorded_posture,
  AetherConfiguration.from_recorded_payload,
  NexusConfiguration.load_recorded_dictionary (enum-name/collection forms
  round-trip), CrystallizerConfiguration.load_recorded_dictionary.
  Recorded values win; backfill is per-key REPORTED; callables record as
  presence flags and reload as code_participation reports; verbs seal on
  return.

### ExternalPersistenceManager (the DB opt-in)
- module asset_management/external_persistence_manager.py; ASSET-OWNED
  since the S3 decomposition (custody moved from the crystallizer root
  into AssetManagementSystem). Separate ExternalPersistenceManagerConfiguration
  carries USER callables (upload/download/list) + upload_on_flush /
  strict_uploads knobs; callables-first by owner decision (no SQLAlchemy in
  core; users own their SQL bootstrap and secrets; a first-party adapter
  package may PROVIDE callables later).
- Both flush paths ship local-cache-first then upload (lenient default:
  failures count into upload_failure_count and never break the seal lane).
- `reload_profile_from_external` = manager download_profile -> system
  insert_cached_items (generic insert-if-absent sink).

### CrystallizerBootstrap (the pod-restart lane)
- src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py
  (moved in S4): single-use fluent builder composing ONLY facades:
  activate (defaults or supplied config) -> attach manager -> local cache
  reload (fresh-ever pods legally boot empty) -> remote pull + re-flush
  into the local cache -> chain-verify gate (broken REFUSES) ->
  load_checkpoint on the newest profile ULID -> report. Its old
  with_preflight_gate knob is an accepted no-op: blocker refusal is
  STANDARD admission now (the engine gate; see the decomposition section).

## Subsystem Decomposition (promoted from patch
## crystallizer_decomposition_2026_07_09, 2026-07-10)

Canonical design anchor: artifacts/2026-07-09_crystallizer_philosophy_v3.md
(the V3 subsystem model). Owner-run validation: 614/614 across the whole
crystallizer test tree.

### The five identities (code-real paths)
- `crystallizer/crystals/` - the twin VOCABULARY at package level (S2):
  every twin + spell_crystal.py + recorded_unit_state.py. CARRIER LAW:
  crystals carry recorded truth and analysis RESULTS; they never own
  analyzers, strategy maps, or walk logic. SpellCrystal slimmed 1684->1030
  lines in S1: its constructor keeps identity/bind-signature capture and
  DELEGATES analysis to a single-use CrystalAnalyzer, storing the returned
  CrystalAnalysisResult (11 properties + describe() read the carried
  result; describe() preserves every pre-decomposition key and adds
  physical_module_fingerprints, export_surfaces, module_load_order, and
  the two AST maps).
- `crystallizer/crystal_analysis/` - the shared analyzer service (S1):
  crystal_analyzer.py (walk owner; analyze_spell_root for live spells,
  analyze_payload for RETAINED payloads - the MR re-analysis seam),
  crystal_analysis_result.py (value-only carrier), custody/ (per-authority
  strategies: synthetic text+SHA custody, user_source SHA256 FINGERPRINTS
  at bind = on-disk drift detection, site_package path law, binary/unknown
  honest leaves), strategies/ (fact passes: import/from-import extraction
  with byte-order parity to the historical extractor, export_surface NEW,
  dependency_view topological load order NEW), preflight/ (the 7 restore
  strategies + PersistenceAnalyzer, relocated).
- `crystallizer/persistence/` - the RECORD, ledger only (S3/S4):
  persistence_system.py + persistence_profile.py + persistence_crystal.py.
  Verbs: profiles, twins/journal, checkpoint minting, retention, chain
  verify, cached_item_form/forms (flush feedstock), insert_cached_items
  (the sink), capture_formation_record, detach_profile_chain (loader
  feedstock). The record touches NO disk, NO DB, and constructs NO
  engines; it calls nobody (edge law).
- `crystallizer/asset_management/` - bytes at rest (S3):
  asset_management_system.py (borrows the record; owns crystallizer_cache
  .py + external_persistence_manager(.py|_configuration.py)). FLUSH
  CONTRACT: seal (ledger) then ship - cache write, FIFO retention at the
  record's LIVE cap, then the lenient upload leg (ONE feedstock pull
  serves both legs; the old Crystallizer upload hook is absorbed).
  Reloads (cache/remote) land in the record's insert sink; formation
  FILES store/load/list here.
- `crystallizer/crystal_loader_system/` - the unfold (S4):
  crystal_loader_system.py (the owner; durable last-load state via
  describe_last_load), load_admission.py (plan_checkpoint_load /
  plan_formation_load with the canonical-kind-order window minting moved
  from the ledger / execute_plan / scope adjudication), load_plan.py
  (declarative: scope world|conduit|frame, per-kind key counts,
  inspectable before activation), restore_engine.py (moved; gained
  refuse_on_blockers), bootstrap_loader.py.

### Admission (the verdict law, S4)
Every mediated load runs plan -> map -> verdict -> execute -> remember.
The gate lives INSIDE the engine at the fold->preflight seam (the only
place owning authoritative FOLDED truth - zero fold duplication): with
refuse_on_blockers=True (every mediated load), a "blockers" verdict
raises a teach-grade RuntimeError naming the rows BEFORE any replay.
Warnings proceed and ride the report. LoadAdmission then ADJUDICATES per
scope: conduit/frame loads reclassify the scope-blind frame_posture
warnings to "expected_for_scope" in the additive "admission" payload view
{"scope","verdict","reclassified"} - raw preflight findings are never
rewritten. Facade payloads are byte-compatible supersets (the "admission"
key is additive). Proven live: the M3 boot-boundary fixture carrying a
placeholder SHA was refused by the synthetic_source_integrity blocker
until the fixture computed its real fingerprint.

### Cross-subsystem laws
- EDGE LAW (acyclic): anything imports crystals/; analysis reads
  crystals; loader reads record + invokes analysis; assets read record +
  call its sink; the record calls nobody.
- LOCK LAW: one-way (facade -> subsystem -> record -> profile); no
  subsystem-to-subsystem lock nesting; borrowers clean BEFORE the record
  (crystallizer cleanup order: loader -> assets -> record).
- Twin-kind honesty: adding a twin kind still touches record AND loader
  (record/replay are duals) - pay it via checklist, not topology claims.
- describe boundary: the record's describe() carries NO disk truth; the
  Crystallizer facade re-enriches cached_checkpoint_count from the asset
  system.

## V3 Horizon Iteration (promoted 2026-07-12 from six patch dirs:
## aether_lazy_frames_and_load_gate_2026_07_11,
## crystallizer_v3_horizon_2026_07_11, crystallizer_s2_user_source_
## retention_2026_07_11, crystallizer_s3_impact_engine_2026_07_11,
## crystallizer_external_mesh_2026_07_12, mr_restore_build_stage_2026_07_11)

Owner-run validation: full 3.14t tree green (9702 tests) plus two
--last-failed passes; every lane closed with acceptance walks (see the
completed epics/stories of 2026-07-11/12).

### Lazy frames + the Aether LoadGate (owner substrate rulings)
- `import melder` creates ZERO AethericFrames (the eager default-frame
  construction is deleted): the first Spellbook births the frame it
  names via `_ensure_frame` (spellbook.py:229, get-or-create is the
  INTENDED semantic); a collapsed configuration falls back to "default"
  via `_ensure_default_frame`, which now lazily CREATES (recreate-after-
  individual-clean matches named-frame semantics; `_ensure_frame`'s
  existing branch repairs a drifted default pointer). check_cleaned
  still refuses torn-down singletons.
- utilities/synchronization/load_gate.py - LoadGate (Cleanable):
  exclusive one-load-at-a-time acquire(label)/release();
  wait_for_passage(timeout) passes the HOLDER thread free and parks
  foreign threads (teach-grade timeout names the holding load); cleanup
  = terminal open with None TOMBSTONES (documented: parked waiters must
  re-check after waking, so no del posture on the holder slots).
- Aether hosts the gate BEFORE any frame can exist +
  acquire_load_authority(label, drain_timeout)/release_load_authority()
  (drain re-snapshots live frames per slice and counts mediator
  sessions; failed acquisition releases the gate). The gate threads
  frame -> DevOpsManager -> CCM -> TransactionMediator as an additive
  load_gate kwarg (None = ungated); the mediator checks wait_for_passage
  at BOTH new-root ingresses (begin_transaction pre-build - covers
  start_transaction and the strategy starter - and begin_frame
  pre-lock); joins never gate. NOTE: CCM.transaction_mediator is an
  accessor METHOD, not a property. The loader wraps both load verbs in
  authority spans ("the loading thread has all control").
- Posture propagation: bind_frame_configuration's two LANDING branches
  call AethericFrame._propagate_transaction_wait_posture, routing the
  canonical posture's max_transaction_wait_time_in_seconds through
  mediator.configure() - closes the captured-once-at-ctor gap (under
  lazy frames every restore rebinds posture onto a default-postured
  frame). The disable_* gates were already live-reads and needed
  nothing.

### S1 load-scope maturity (formations compose into LIVE worlds)
- LoadPlan: additive target_frame_name/skip_existing slots.
- LoadAdmission: borrows aether (None = bare-record);
  plan_formation_load(..., target_frame_name, skip_existing) rewrites
  frame identity COPY-ON-WRITE in the detached window only (frame twin
  re-key + journal frame rows + book/cluster frame_name edges;
  multi-frame windows refuse - formations are single-frame slices);
  _preflight_host reads the frame REGISTRY (never _ensure_frame - a
  probe must not birth the frame it checks): frame_missing=info,
  posture_conflict=warning, conduit/cluster name collisions=blockers via
  the PUBLIC cloud probes has_conduit_name / has_cluster_name (the
  documented _conduit_clusters private seam was retired by the
  public_cloud_seams lane, 2026-07-12 - see the three-lane section
  at the end of this doc);
  execute_plan refuses host blockers PRE-ENGINE or downgrades them to
  "skipped_existing" under the skip flag; admission view gains the
  additive "host" key.
- Engine skip lanes (skip_existing): taken conduit name -> conjure
  name=None + shortfall "conduit_name_taken_built_unnamed" (safe: names
  are never replay resolution keys); existing cluster -> REUSED, members
  join + shortfall "cluster_existed_members_joined".
- Facade restore_formation gains both params;
  compose_frame_subtree/compose_conduit_subtree DELETED (zero callers;
  capture_formation_slice is the shipped composer; NOTE marker in
  persistence_profile.py records the ruling).

### S2 physical custody (opt-in user-source TEXT retention)
- CrystallizerConfiguration.retain_user_sources (schema bool, default
  False = byte-identical pre-S2 record) threads Crystallizer ->
  SpellCrystal -> CrystalAnalyzer. Harvest: base
  SourceCustodyStrategy.harvest_payload defaults None;
  UserSourceCustodyStrategy overrides ({source_text, source_sha256,
  module_path, is_package} via the existing read+fingerprint helpers);
  the analyzer walk harvests beside the M3 synthetic harvest;
  CrystalAnalysisResult.user_module_sources rides describe() and
  analyze_payload re-folds it.
- Restore: RestoreEngine._rebuild_user_world - ABSENT files only (THE
  LIVE FILE ALWAYS WINS; sys.modules skip; dot-depth order), rebuilt
  through the SyntheticModule lifecycle (normal-verbs law; binding
  sentinel "user_source_retained"), shortfall
  "user_module_rebuilt_synthetic_from_retained_source", single import
  retry via _import_qualified_target.
- Preflight: hydration downgrades absent-module blockers to info when
  text is retained; UserSourceIntegrityStrategy: NARROWED (2026-07-12,
  source_drift_preflight lane) to record self-consistency only -
  retained-text sha mismatch = BLOCKER (tamper). Live-file drift moved
  wholesale to the dedicated SourceDriftStrategy (see the three-lane
  section at the end of this doc); CRLF-safe read_text law unchanged.

### S3 impact engine (blast radius over the manifests)
- Read seam: PersistenceProfile.describe_spell_crystals() (BOTH custody
  maps + additive "custody_state"; detached payloads only) + system
  passthrough.
- crystal_analysis/impact_engine.py - ImpactEngine: construction builds
  module->carrying-spells + module->importers reverse indexes +
  fingerprint/path maps; verbs spells_touching_module,
  blast_radius_of_module (transitive closure; honest unknown_module),
  blast_radius_of_spell (spell_id vocabulary; a spell change IS its root
  module changing), describe_source_drift (CRLF-safe re-hash ->
  unchanged|drifted|absent|unreadable + radius per non-unchanged),
  describe. Documented thread-confined: immutable post-construction.
- Facade Crystallizer.analyze_impact(module_name|spell_id|neither) -
  one question per call (both = ValueError); engine built + cleaned per
  invocation.

### External mesh lane + record versioning
- Generic kind-partitioned callables on the manager configuration:
  with_store_handler(kind, profile, unit_id, payload) /
  with_fetch_handler(kind, unit_id) / with_list_units_handler(kind,
  profile) / with_delete_handler(kind, unit_id) /
  with_stream_emissions(bool). LEGACY BRIDGE: the checkpoint verbs fall
  back to the generic lanes (upload->store_unit("checkpoint"),
  download->fetch_unit, profile list->list_units) - one handler set
  serves the whole mesh. WRITE-LANE GATES WIDENED in lockstep: validate()
  AND upload_enabled accept (upload_handler OR store_handler);
  read-only configs must disable upload_on_flush explicitly.
- Manager: store_unit lenient + store_failure_count (strict_uploads
  re-raises); fetch/list loud-refuse; delete_unit STRICT (a half-run
  retention pass must not lie). Formations ship local-then-remote at
  store_formation; reload_formations_from_external mirrors the
  checkpoint reload; apply_external_retention(profile, cap) ULID-sorted
  oldest-first deletes (facade cap defaults to
  max_persistence_crystals - the local FIFO's knob).
- EMISSION TAP (opt-in): every recorded twin streams a delta row
  {record_version, crystal_kind, payload} under a fresh event ULID.
  THREAD-SAFETY LAW: the payload captures BEFORE record() (replace-on-
  emit means a concurrent same-kind emit may clean the twin
  mid-describe) and ships AFTER (local truth leads the mirror);
  lenient + counted; untapped worlds pay one property read.
- persistence/record_version.py - RecordVersion (static authority,
  CURRENT "1.0.0", key "record_version"): stamps to_cached_item,
  capture_formation_record, and tap envelopes; check_readable refuses
  NEWER-major artifacts at from_cached_item (covers cache + external
  reloads) and load_formation_record; absent stamps read "0.0.0"
  (pre-versioning = oldest, always readable). MAJOR breaks shape, MINOR
  adds keys, PATCH documents.
- Interface contract: a twin IS the interface - emit consumes the
  object, the mesh ships its describe() dict, and that dict crosses
  JSON losslessly (proven over the family + the full
  class->json->class rehydration loop).

### MR restore build stage (twin-over handoff, executed)
- MutationResearchConfiguration.load_recorded_dictionary (reload-lane
  law; seals via activate() - the config's emission factor AND root
  activation's hard gate).
- _replay_mutation_research = BUILD stage on the canonical slot: no
  twin = NO-OP; folded "cleaned" = honest shortfall; else reload verb
  (per-key shortfalls) -> Aether()._get_mutation_research() (hosted
  accessor; an ALREADY-ACTIVE root deactivates first - live-world loads
  under the LoadGate; both acts recorded) ->
  activate(hydrate_from_record=False) (engine owns FOLDED truth) ->
  load_recorded_composition; pre-Phase-B = config-only +
  "composition_not_recorded_pre_phase_b"; "disabled" later-wins =
  activate-then-deactivate. Both first_cut shortfalls RETIRED.
- MRCompositionStrategy (9th default preflight row; the MR root now
  rides the engine preflight bundle): blockers ONLY on unparseable
  shapes (composition/set/organization/lanes/residence); warnings on
  organization/residence disagreement; spell_id vocabulary (2026-07-11
  sweep) with pre-sweep payloads tolerated as ONE named
  "pre_vocabulary_sweep_payload" warning. LoadAdmission reclassifies
  its findings expected_for_scope on conduit/frame loads (MR is a
  world-scope root).

## Three-Lane Tail (promoted 2026-07-11 from patch dirs
## public_cloud_seams_2026_07_12, source_drift_preflight_2026_07_12,
## spell_index_graft_2026_07_12; owner-directed finish)

### Public cloud seams (access-spelling law; zero behavior change)
- AethericFrame.conduit_cloud (check_cleaned property,
  aetheric_frame.py:411) + ConduitCloud.has_cluster_name(name)
  (lock-guarded membership read mirroring has_conduit_name,
  conduit_cloud.py:379). Every crystallizer reader repointed: engine
  cluster-replay + conjure skip lanes, admission _preflight_host conduit
  and cluster checks. Grep-proven zero private cloud reads remain
  crystallizer-side; the retired seam comments carry NOTE markers.
  LAW: cross-package cloud access is public-verb-only.

### Source drift at load-time preflight (10th default row)
- preflight/source_drift_strategy.py - SourceDriftStrategy
  ("source_drift"): EVERY bind-time physical_module_fingerprints entry
  with a recorded module_to_path re-hashes against disk at load,
  RETENTION-AGNOSTIC (retention-OFF worlds no longer restore blind).
  Absent file = honest warning (import may still resolve via sys.path);
  sha differs (CRLF-safe read_text) = warning
  "user_source_drifted_since_seal"; unreadable = info; unchanged =
  silent; (module, path) pairs deduplicate across crystals. Drift is
  notice, never refusal. The DEFAULT PREFLIGHT SET is now 10 rows:
  link_integrity, contract_peer, hydration, configuration_loss,
  cluster_membership, frame_posture, synthetic_source_integrity,
  user_source_integrity (tamper-only), mutation_research_composition,
  source_drift.

### Spell-index graft lane (restore grain below the conduit slice)
- Capture: PersistenceProfile.capture_index_graft(index_id) (:783) +
  system passthrough (:456) - versioned record {record_version,
  graft_kind:"spell_index", index_id, index_payload (twin describe),
  members {spell_id: {payload, custody_state}},
  members_without_custody}. Storage is the user's choice (plain dict;
  mesh or formations both carry it).
- Restore: crystal_loader_system/graft_runner.py - GraftRunner
  (single-use, Cleanable): RecordVersion gate + graft_kind refusal ->
  unconjured-host refusal (public Spellbook.conduit accessor,
  spellbook.py:5412) -> per-member overlap rule via
  host_frame.find_index_for_spell (resident member REFUSES by default;
  skip_resident=True skips + shortfall
  "member_resident_in_host_skipped"; existing indexes are NEVER
  mutated - fresh-index-only law) -> hydration via the import lane with
  failure->rebuild->retry through the shared user_world_rebuild lane ->
  selected member binds ACTIVE (bind creates the fresh index + selects)
  -> parked members conduit.bind_inactive onto it -> detached report
  {status, live_index_id, members_bound, members_parked,
  skipped_resident, shortfalls, identity}. NO LoadGate: grafts are
  user-verb activity (per-verb transactions), not world replays.
  Emissions free: bind/bind_inactive auto-record (re-recording
  covenant).
- Shared rebuild lane: crystal_loader_system/user_world_rebuild.py -
  rebuild_absent_user_modules(spell_id, crystal, on_built,
  on_shortfall): live-file-wins, sys.modules skip, dot-depth
  parents-first, SyntheticModule lifecycle, honest shortfalls. The
  engine's _rebuild_user_world DELEGATES via callbacks (identical
  built-stack + report semantics); GraftRunner uses a no-op on_built.
  The rebuild laws live in exactly one place.
- Facades: Crystallizer.capture_index_graft (:621) / graft_index
  (:647) (activation-gated; live-object facade per create_spell_crystal
  precedent).
