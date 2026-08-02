# Component material migrated out of src_architecture.md

Extracted 2026-08-01 during the recomposition of `src_architecture.md` to its
Required Section Contract. These are component-level deep dives, which that
contract names as an anti-pattern in the architecture document.

NOTHING HERE IS DELETED. This file is the INPUT to the `src_components.md` pass.
Until that pass lands this material is absent from both canonical documents - a
deliberate, bounded, recorded gap.

Four headings arrived wrapped across two physical lines (which produces one-line
index fragments) and were unwrapped here.

## Table of Contents
- Metadata
- Scope and Intent
- Documentation Quality Standard
- DO NOT ASSUME / Unknowns Gate
- Unknowns
- Source Coverage and Evidence
- Glossary and Core Terms
- System Context (C4)
- System Boundary and External Interfaces
- Architecture Summary (C4)
- Entrypoints and Runtime Guardrails
- Boot and Configuration Sequence
- Spellbook Root Responsibilities
- Aether Global Singleton Responsibilities
- Aetheric Frame Responsibilities
- Conduit Lifecycle (Normal and Lesser)
- Binding and Registration Pipeline
- Resolution Styles and DI Shapes
- DI Resolution Contract (Spec)
- SpellCompiler and Validation Pipeline
- Resolution and Meld Pipeline
- Contracts, Policies, and Permissions
- Existence and Scoping Model
- Logging and Observability
- Ownership, Lifecycle, and Cleanup
- Operational Invariants
- Failure Modes and Error Paths
- Extension Points
- Data Flows and Sequences
- C3 and C2 Cross-Reference
- C1 Code Map (Core Only)
- Diagrams
- Information Sources
- Open Questions
- Context / Handoff Summary
- Appendix A: Deep Component Narratives (Core)
- Appendix B: Detailed Sequences and Data Flows
- Appendix C: Core File Inventory (Expanded)

## Documentation Quality Standard
This document is durable context and must stand on its own.

Rules:
- No handwaving. Every claim is grounded in source evidence or marked as unknown.
- Entry points and boot sequences are explicit and ordered.
- Ownership, lifecycle, and cleanup ordering are explicit for core components.
- Invariants, failure modes, and concurrency constraints are stated.
- ASCII and Mermaid diagrams included for core flows.
- Evidence list updated when new sources are used.

## Source Coverage and Evidence
Coverage summary (non-exhaustive):
- Package entrypoint and guardrails: `__init__.py`, the registration refusal in
  `aether/spellbook/bind/bind.py`, and the generated internal-bind manifest under
  `_build_assets/_bind_guard/` (`bind_guard.py` loader, `manifest/bind_guard_manifest.py`).
- Spellbook + binding pipeline: `spellbook.py`, `bind.py`, `spell.py`, `spell_index.py`.
- SpellbookConfiguration and system state:
  `spellbook_configuration.py`, `system_state.py`.
- SpellCompiler and validation: `spell_compiler.py`, `validation_system.py`,
  `spell_system_validation_system.py`.
- Resolution styles and DI descriptors: `spell_types.py`, `existence.py`,
  `parameter_di_shape.py`, `spell_map.py`, `spell_contract.py`,
  `resolution_style_matrix.py`.
- Validation strategies: `circular_dependency_strategy.py`,
  `binding_resolution_cycle_strategy.py`, `cycle_detection_strategy.py`,
  `contract_graph_cycle_strategy.py`.
- Aether and frames: `aether.py`, `aetheric_frame.py`.
- Package-root hardcopy docs and root helpers:
  `system_document.py`, `__architecture__.py`, `__components__.py`,
  `__graph_network__.py`, `__graph_details__.py`,
  `aether_configuration.py`, and `aether_configuration_builder.py`.
- Crystallizer root, decomposed subsystems, and module-world surfaces
  (paths current as of the 2026-07-10 decomposition): `crystallizer.py`,
  `configuration/crystallizer_configuration.py`,
  `configuration/crystallizer_configuration_builder.py`,
  `persistence/persistence_system.py`, `persistence/persistence_profile.py`,
  `persistence/persistence_crystal.py`,
  `asset_management/asset_management_system.py`,
  `asset_management/crystallizer_cache.py`,
  `crystal_loader_system/` (crystal_loader_system.py, load_admission.py,
  load_plan.py, restore_engine.py, bootstrap_loader.py),
  `crystal_analysis/` (crystal_analyzer.py + custody/strategies/preflight),
  `crystals/**` (the package-level digital-twin family incl.
  `spell_crystal.py` and `recorded_unit_state.py`), and
  `synthetic_module.py`.
- Mutation-research root and the ResearchSet package (2026-07-11 rebuild):
  `mutation_research.py`, `mutation_configuration.py`,
  `mutation_configuration_builder.py`, and `research_set/`
  (research_set.py, research_lane.py, research_node.py, transition_entry.py,
  research_journal.py, residence_registry.py, network_versioner.py).
- Nexus / AR runtime: `nexus.py`, `frame_descriptor_manager.py`,
  `frame_acl_manager.py`, `nexus_frame_builder.py`, `rift.py`,
  `rift_space.py`, room-specific `RiftSpace` types, `workstation.py`,
  `command_system/*.py`, `static_frame_viewer.py`, and `codegen_system/*`.
- Conduit runtime and contracts: `conduit.py`, `conduit_ward.py`, `policies.py`,
  `permissions.py`.
- Resolution runtime: `meld.py`, `creation_context.py`, `creations.py`, and
  `conduit_creations.py`.
- Runtime codegen/creation packaging: `spell_compiler_artifact.py`,
  `codegen_creation_system.py`, `spell_codegen_creation.py`,
  `resolution_frame.py`.
- Control plane: `spell_system_states.py`, `spell_system_state.py`,
  `spell_state.py`, `spell_state_change_reason.py`,
  `change_control_manager.py`, `dev_ops_manager.py`.
- Ownership transfer: `transfer_of_ownership.py`.
- Utilities: `cleanable.py`, `phase_scheduler.py`, `safe_logger.py`,
  `id_builder.py`, `init_helpers.py`, and `protocol_crafter.py`.

Evidence list (non-exhaustive):
- `src/melder/__init__.py`
- `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`
- `src/melder/system_document.py`
- `src/melder/__architecture__.py`
- `src/melder/__components__.py`
- `src/melder/__graph_network__.py`
- `src/melder/__graph_details__.py`
- `src/melder/aether/aether_configuration.py`
- `src/melder/aether/aether_configuration_builder.py`
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration.py`
- `src/melder/crystallizer/configuration/crystallizer_configuration_builder.py`
- `src/melder/crystallizer/persistence/persistence_system.py`
- `src/melder/crystallizer/persistence/persistence_profile.py`
- `src/melder/crystallizer/persistence/persistence_crystal.py`
- `src/melder/crystallizer/asset_management/asset_management_system.py`
- `src/melder/crystallizer/asset_management/crystallizer_cache.py`
- `src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py`
- `src/melder/crystallizer/crystal_loader_system/load_admission.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
- `src/melder/crystallizer/crystal_analysis/crystal_analyzer.py`
- `src/melder/crystallizer/crystals/recorded_unit_state.py`
- `src/melder/crystallizer/crystals/spell_crystal.py`
- `src/melder/crystallizer/crystals/spell_index_crystal.py`
- `src/melder/crystallizer/crystals/contract_crystal.py`
- `src/melder/crystallizer/synthetic_module.py`
- `src/melder/mutation_research/mutation_research.py`
- `src/melder/mutation_research/mutation_configuration.py`
- `src/melder/mutation_research/mutation_configuration_builder.py`
- `src/melder/mutation_research/research_set/research_set.py`
- `src/melder/mutation_research/research_set/research_lane.py`
- `src/melder/mutation_research/research_set/research_node.py`
- `src/melder/mutation_research/research_set/transition_entry.py`
- `src/melder/mutation_research/research_set/research_journal.py`
- `src/melder/mutation_research/research_set/residence_registry.py`
- `src/melder/mutation_research/research_set/network_versioner.py`
- `src/melder/aether/spellbook/spellbook.py:L45-L75,L2342-L2480,L2909-L3008`
- `src/melder/aether/spellbook/spellbinder.py`
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/bind/scan.py`
- `src/melder/aether/spellbook/bind/spell_index.py`
- `src/melder/aether/spellbook/spell.py:L1010-L1187`
- `src/melder/aether/spellbook/existence/existence.py`
- `src/melder/aether/spellbook/spell_types/spell_types.py`
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `src/melder/aether/spellbook/configuration/system_state.py`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:L131-L2383`
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py`
- `src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`
- `src/melder/aether/spellbook/spell_compiler/system/validation/cycle_detection_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/system/validation/contract_graph_cycle_strategy.py`
- `src/melder/mutation_research/mutation_research.py`
- `src/melder/aether/aether.py`
- `src/melder/aether/aether_utility_system.py`
- `src/melder/aether/aetheric_frame/aetheric_frame.py`
- `src/melder/nexus/nexus.py`
- `src/melder/nexus/nexus_frame_manager.py`
- `src/melder/nexus/nexus_frame_builder.py`
- `src/melder/nexus/acl/builder/frame_acl_builder.py`
- `src/melder/nexus/rift/rift.py`
- `src/melder/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/nexus/rift/codegen_system/codegen_transaction_context.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- `src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validator.py`
- `src/melder/nexus/rift/codegen_system/validation/codegen_validation_result.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_compiler.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_executor.py`
- `src/melder/nexus/rift/codegen_system/execution/codegen_execution_result.py`
- `src/melder/nexus/rift/codegen_system/observability/codegen_monitor.py`
- `src/melder/nexus/rift/frame_viewer/frame_viewer.py`
- `src/melder/nexus/rift/frame_viewer/view_multiframe.py`
- `src/melder/nexus/rift/frame_viewer/view_frame.py`
- `src/melder/nexus/rift/frame_viewer/view_conduit.py`
- `src/melder/nexus/rift/frame_viewer/view_spell.py`
- `src/melder/nexus/rift/rift_space/rift_space.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event_system.py`
- `src/melder/nexus/rift/rift_space/event_system/rift_event.py`
- `src/melder/nexus/rift/rift_space/static_rift_space.py`
- `src/melder/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/nexus/rift/rift_space/capability_rift_space.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_cluster.py`
- `src/melder/aether/aetheric_frame/conduit_cloud.py`
- `src/melder/aether/conduit/meld/meld.py:L220-L499`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py:L109-L814`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py`
- `src/melder/utilities/custom_exceptions/meld_execution_error.py:L4-L96`
- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:L1-L233`
- `src/melder/aether/spellbook/spell_compiler/dag/resolution_frame/resolution_frame.py`
- `src/melder/aether/conduit/meld/contracts/spell_map.py`
- `src/melder/aether/conduit/meld/contracts/spell_contract.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `src/melder/aether/conduit/conduit_ward/policies/policies.py`
- `src/melder/aether/conduit/conduit_ward/permissions/permissions.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
- `src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/utilities/general_base/cleanable.py`
- `src/melder/utilities/helpers/id_builder.py`
- `src/melder/utilities/helpers/init_helpers.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`
- `src/melder/utilities/logger/safe_logger.py`
- `src/melder/utilities/ai_native_support_tools/protocol_crafter.py`

## Glossary and Core Terms
- Aether: Global singleton that owns AethericFrames and global registries.
- AethericFrame: Per-frame container for conduits, registries, and dev-ops state.
- Dependency Graph Runtime (DGR): Runtime that builds and executes dependency
  graphs at resolution time, supports late binding via contracts/links, and
  enforces runtime validation gates before activation.
- Spellbook: User-facing binding and conjure surface for the DGR.
- Spell: Bound object metadata (spellframe, spell_id, existence, permissions).
- SpellIndex: Stable index (ULID) that categorizes and targets spells and holds
  the active selected spell. Version history is owned by MutationResearch.
- Conduit: Runtime scope and activation host for resolving spells via Meld.
- ConduitWard: Relationship manager for contracts, policies, and lineage links.
- Creations: Instance registry for a conduit; enforces existence semantics.
- SpellSpace: Scoped handle for unique_per_spell_space instances.
- SpellCompiler: Per-spell pipeline for requirements, graph, frame, validation.
- SpellSystemStates: Per-frame control plane for lineage topology and validity.
- ChangeControlManager: DevOps tracker for dirty roots and pending changes.
- AetherUtilitySystem: Process-wide utility host for shared providers,
  currently logger resolver/fallback registration.
- Nexus: Public singleton AR root over hidden Aether substrate state.
- FrameDescriptorManager: Nexus-owned manager for frame-scoped descriptors,
  passive publication, and Nexus-managed frame-record ownership.
- FrameACLManager: Nexus-owned manager for frame-local ACL containers,
  profile registries, and frame-level ACL change fan-out.
- NexusFrameBuilder: fluent authored-frame builder created by
  `NexusFrameManager.begin(...)` to stage one Nexus-managed frame
  configuration before rooted creation.
- FrameACLBuilder: frame-local mutable ACL authoring surface that owns one
  active view/command/codegen draft session for a `FrameACLContainer`.
- Rift: Live AR runtime object that attaches to Nexus-managed frames and
  userland target frames.
- RiftSpace: Room/workspace object owned by a Rift.
- FrameLinkContract: Rift-local frame selection contract storing the selected
  view, command, and codegen ACL family names per frame.
- FrameViewer: Rift-backed public viewer host that reads current view
  projections on demand and requires explicit `frame_name` for frame-local
  operations.
- ViewMultiFrame / ViewFrame / ViewConduit / ViewSpell: on-demand viewer helper
  surfaces above the current Rift projection state.
- Workstation: Room-local strong/weak binding canvas for saved objects,
  attributes, methods, and one active target.
- CommandSystem: Room-local mediated command layer above the
  viewer/workstation split, specialized by room mode.
- CodegenSystem: room-owned internal codegen engine that builds transaction
  contexts, validates code, builds namespaces, compiles/executes code, and
  publishes codegen lifecycle events for one `CodegenRiftSpace`.
- StaticFrameViewer: Static-room viewer overlay that filters spell-facing
  query/projection paths down to already-live spell surfaces.
- SpellExaminer profile layer: registry-backed `general` and `detailed`
  examination profiles used for richer inspection over raw candidates and live
  spells.
- Aetheric Mediator Plane: standalone, NOT-YET-WIRED top-level transaction
  plane under `aether/aetheric_mediator/`. Serializes above-frame structural
  work by scope. Imports `melder.utilities` only, never `melder.aether`.
- Mediator: the aetheric plane's root - admission, per-identity sessions,
  strategy dispatch, outcome policy, and reporting in one object.
- ClaimTable: atomic all-or-nothing, mode-aware scope-claim table. A LEAF -
  it never calls another plane component, which is what makes the plane's
  lock order provably one-way.
- ClaimMode: `x` exclusive / `s` shared / `ix` intent. DevOps' vocabulary
  verbatim. `ix` is the hierarchical parent marker: hold `ix` on the parent
  and `x` on the child, and disjoint children proceed in parallel while a
  whole-parent `x` still excludes every one of them.
- ScopeKey / ScopePrefix: canonical builders and the closed namespace
  vocabulary (`world`, `frame:<name>`, `subsystem:<name>`) for plane scope
  keys. The hierarchy is expressed by MODE, not by key shape.
- OutcomePolicy: per-transaction failure posture - `UNWIND` (run inverses and
  raise) or `LEAVE_BROKEN` (run nothing, record a residue ledger for a
  repairing agent).
- Policies: Conduit link/visibility rules used in dynamic mode.
- Permissions: Spell access levels across conduits (read/create/block).
- SpellMap: Declarative DI placeholder for explicit spell/frame/binding targets.
- SpellContract: Late-bound contract socket for dynamic linking across conduits.
- Mutation override overlay: `Spell.apply_mutation_override(...)` /
  `clear_mutation_override()`, emitting the `mutation_contract_set` /
  `mutation_contract_cleared` change reasons.
- ParameterDIShape: Phase 1 classification of how a parameter should resolve.

## Spellbook Root Responsibilities
- Owns local spell registries and lookup maps.
- Maintains owned and contracted spell_id maps for O(1) resolution by current id.
- Binds spells using `Bind` and tracks spell identifiers.
- Interfaces with Aether for shared configuration and spell registry updates.
- Starts transaction-backed SpellIndex mutation flows for active-member switch,
  move-in, and move-out operations.
- Runs SpellCompiler phases and validation before Conduit creation.
- Conjures a single Conduit per Spellbook instance.
- Provides a `SpellBinder` fluent adapter for binding.

## Aether Global Singleton Responsibilities
- Singleton root for all AethericFrames.
- Owns the default frame and a map of named frames.
- Owns one optional root `AetherConfiguration` and exposes
  create/builder/install/activate helpers that apply logger policy into
  `AetherUtilitySystem`.
- Maintains spell registries per conduit and selected-spell registries per frame.
- Binds `SpellbookConfiguration` to frames.
- Registers conduits and spell indices.
- Exposes ConduitCloud and ConduitCluster access via frame.
- Privately hosts `Nexus`, `Crystallizer`, `AetherUtilitySystem`, and the
  lazily constructed `MutationResearch` singleton root rather than exposing AR
  or mutation control through Aether's public surface directly.

## Aether Utility System Responsibilities
- Singleton utility host for shared runtime providers.
- Owns one registered channel-logger resolver and one default stdlib logger
  fallback.
- Resolves provider-backed channel loggers for runtime objects through
  `InitHelpers.resolve_channel_logger(...)`.
- Resolves explicit logger overrides through
  `InitHelpers.resolve_safe_logger(...)`.
- Replaced the old logger-factory layer; live runtime no longer depends on
  `IrisLoggerFactory` or `StdLoggerFactory`.

## Crystallizer Responsibilities
- `Crystallizer` is a hosted singleton root owned by `Aether`.
- Owns installed crystallizer configuration plus configured/activated state.
- Uses `create_spell_crystal(...)` to build one loader-facing `SpellCrystal`
  from a live spell under the installed policy.
- Keeps source-classification policy in `CrystallizerConfiguration` rather
  than on `SpellCrystal` itself.
- Since the 2026-07-10 decomposition the root is a thin facade over THREE
  same-rank children (see "Persistence Subsystem Topology" at the end of
  this doc): `PersistenceSystem` (the record), `AssetManagementSystem`
  (bytes at rest: cache, formation files, the EPM DB seam), and
  `CrystalLoaderSystem` (the admission-gated unfold).
- `SpellCrystal` is the custody-twin CARRIER for one concrete spell: it
  delegates module-world analysis to the shared `crystal_analysis` service
  and carries the returned `CrystalAnalysisResult` (V3 carrier law), while
  `SyntheticModule` is the live in-memory module embodiment used when
  crystallized code is activated into the runtime.
- The loader, analysis, and asset-management packages are REAL subsystems
  since 2026-07-10 (formerly scaffold-only). `bootstrap_manifest.py` is
  gone; the pod-boot lane is `crystal_loader_system/bootstrap_loader.py`.

## Aetheric Frame Responsibilities
Each frame owns:
- Conduits (root conduits mapped by id).
- Spell registry per conduit and aggregated selected-spell registry.
- Conduit clusters for auto-sharing roots.
- ConduitCloud for dynamic named lookup.
- DevopsInformationRegistry as the frame-local topology and transaction mirror.
- SpellSystemStates registry and DevOpsManager.
- Optional frame-owned shared `SpellbookConfiguration`.
- Narrow `AethericFrameConfiguration` posture object bound during Spellbook
  conjure.
- DevOpsManager is constructed per frame and owns ChangeControlManager + RiskManager for that frame. EVIDENCE: src/melder/aether/aetheric_frame/aetheric_frame.py:__init__ + src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:__init__.
- SpellSystemStates stores per-conduit resolution state keyed by conduit_id in addition to frame-wide structural state. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:__init__ + get_or_create_conduit_resolution_state.
- ChangeControlManager admits structural mutations (bind/link/cluster_link/transfer_ownership/unlink) through one moded scope-acquisition gate (claim modes x exclusive / s shared / ix intent); the link and cluster-membership mirrors are maintained EAGERLY at the mutation site, race-safe under held claims, so strategies need no relational commit deltas. EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py + embargo_manager/embargo_manager.py; component detail in src_components.md "Transaction Admission Plane".

## Aetheric Mediator Plane Responsibilities (BUILT, NOT WIRED)

READ THIS FIRST: `src/melder/aether/aetheric_mediator/` is a COMPLETE,
TESTED, STANDALONE package that NOTHING CURRENTLY CONSTRUCTS. `Aether` does
not build it, no subsystem submits to it, and no runtime path passes through
it. It is documented here because it exists on disk and is the intended
top-level transaction plane; it is NOT part of any live flow today. Do not
read any statement below as describing current runtime behaviour.
EVIDENCE: a repo-wide search for `aetheric_mediator` outside the package
itself returns zero source hits (tests only).

Purpose:
- Serialize TOP-LEVEL structural work across Crystallizer, MutationResearch,
  and Nexus by SCOPE rather than globally, so disjoint work proceeds in
  parallel and only true overlap waits.
- Re-express the crystallizer's global `LoadGate` as a degenerate case of a
  claim: whole-world exclusivity is `world` claimed EXCLUSIVE, while a
  frame-scoped load claims `world` INTENT plus `frame:<name>` EXCLUSIVE, so
  two disjoint frame loads coexist and a whole-world load still excludes both.

THE ISOLATION CONSTRAINT (epic constraint 4, the property everything else
rests on):
- The package imports the standard library and `melder.utilities` ONLY. It
  must never import `melder.aether`.
- That is what lets it be constructed BEFORE any `AethericFrame` can exist,
  and tested in isolation. A test in the package asserts the absence.
- Consequence for the direction of knowledge: `Aether` knows about the plane;
  the plane knows nothing about `Aether`. Subsystems ANNOUNCE themselves
  through `register_participant(...)`; the plane never reaches out. If it had
  to discover subsystems it would need the forbidden import and the whole
  isolation property would collapse.

Relationship to the DevOps change-control plane:
- This is a SECOND, HIGHER plane, not a replacement. The frame-local DevOps
  plane (`ChangeControlManager` + `TransactionMediator` + embargo manager)
  continues to own structural mutation WITHIN a frame - bind, link,
  cluster_link, transfer_ownership, unlink.
- The aetheric plane is for operations ABOVE a frame: whole-world and
  frame-scoped loads, index grafts, subsystem enable/disable, agent repair.
- The claim vocabulary is DevOps' verbatim (`x` / `s` / `ix` with the same
  compatibility matrix), so evidence written against one plane reads
  correctly against the other.
- Deliberate divergences, each with a recorded reason: scope claims are
  COMPLETE AND EXPLICIT with no implicit exclusive default; there are NO
  SCOPE HASHES; and `ChangeControlConflictManager` is not ported.
  The scope-hash divergence is PROVISIONAL and coupled to
  `EPIC-2026-08-01-conflict-manager-zombie`: the retired DevOps conflict scan
  matched on HASHES while the claim table matches on KEYS, which are
  different notions of overlap. If that epic finds hash-overlap detection was
  load-bearing, this plane inherits the same gap by construction.

Owned structure:
- `Mediator` is the plane root and the object `Aether` is intended to hold.
  It collapses the roles DevOps splits across `ChangeControlManager` (owning
  root) and `TransactionMediator` (front door), because the DevOps root
  carries frame duties - dirty roots, revalidation, risk - with no
  counterpart here.
- It owns and cleans four children: `ClaimTable`, `AdmissionOrchestrator`,
  `InformationRegistry`, `StrategyBuilder`.

OPERATIONAL LAWS (all four are load-bearing and easy to break by accident):
- LOCK ORDER IS `orchestrator._lock` -> `claim_table._condition`, and that is
  the ONLY cross-object nesting in the plane. It is one-way because
  `ClaimTable` is a LEAF: it never calls the orchestrator, the mediator, the
  registry, or a session.
- ADMIT MUST NEVER WAIT. `try_acquire` is non-blocking by design - it returns
  blocking evidence rather than parking. Bounded waiting lives in
  `Mediator._admit_with_wait`, which parks on `ClaimTable.wait_for_change`
  only AFTER admission has returned and released its lock. A thread parked
  inside `admit` would hold the exact lock `release(...)` must take to free
  the claims it is waiting for, so the plane would deadlock on the first real
  contention - the only workload it exists for.
- WAITING IS SLICED at one second per park (`Mediator._WAIT_SLICE_SECONDS`),
  ported from `TransactionMediator._admit_with_scope_wait`. The check and the
  park are two separate acquisitions of the table's condition, which is
  FORCED rather than sloppy, so a release landing between them is missed;
  slicing bounds that to one second per retry instead of the whole budget.
- ADMISSION IS ALL-OR-NOTHING. A request takes every scope it asked for or
  none, so a caller can never hold half a claim set and believe it is
  isolated.

Outcome policy (owner-specified, and the plane's distinctive behaviour):
- Every transaction carries an explicit failure posture. `UNWIND` runs
  registered inverses newest-first and raises. `LEAVE_BROKEN` runs NOTHING
  and records what was left in place, because a structural rebuild that dies
  partway leaves objects that are often individually valid and expensive to
  recreate - destroying them to reach a clean slate can cost more than
  mending them.
- `BROKEN` is a DISTINCT TERMINAL STATE, deliberately not a flavour of
  `ABORTED`. Aborted means the world was returned toward its prior shape;
  broken means it was knowingly left mid-flight for repair, with a residue
  ledger retained on the session.
- CLAIMS ARE RELEASED ON EVERY TERMINAL PATH, including `LEAVE_BROKEN`.
  Leaving the WORLD broken is the product decision; leaving the CLAIM TABLE
  broken would wedge the plane, which is a different and purely harmful
  failure.

Lifecycle contract across the package:
- Every class that is CONSTRUCTED is `Cleanable` and something named cleans
  it; every vocabulary is a `StrEnum`; the four remaining classes are static
  namespaces that are never instantiated and say so.
- `Mediator.cleanup` orders teardown BORROWERS BEFORE OWNERS - strategy
  registry, information registry, orchestrator, then the sessions that own
  the request and staged records, then the claim table LAST because its
  cleanup is what wakes any thread still parked in `wait_for_change`.
- `Identity` is CALLER-OWNED: a subsystem builds it, the plane borrows it,
  and nothing inside the package cleans one.

Known gaps, recorded rather than hidden:
- UNWIRED, as stated at the top of this section.
- `TransactionType` membership is PROVISIONAL, pending the three subsystem
  surveys.
- `ClaimTable.acquire` (the blocking variant) has ZERO production call sites
  and is retained only behind a docstring that refuses the unsafe usage; its
  disposition is an open owner decision.
- Concrete information STRATEGIES are deferred. The registry is the
  mechanism; the catalog is content.

## Nexus and Rift Responsibilities
- `Nexus` is the public singleton AR root, not `Aether`.
- `Nexus` owns:
  - hidden `Aether` reference for Nexus-managed frame realization/disposal
  - process-wide AR configuration and enabled/configured state
  - process-wide Rift creation/direct-access gates plus target-frame and
    active-Rift budget enforcement
  - Rift registry, Rift name/id indexes, named Rift profiles, deterministic
    default-name counters, and target-frame ref counts used for budget
    enforcement
  - `RiftGateController` for per-Rift admission, drain, and entry-mode control
  - `FrameDescriptorManager`, which owns one `FrameDescriptor` per frame plus
    passive frame/conduit/spell publication and Nexus-managed frame records
  - `NexusFrameManager`, which owns the authoritative Nexus-managed frame
    registry and the authored configuration metadata for those frames
  - `NexusFrameBuilder`, which is created by
    `NexusFrameManager.begin(frame_name)` and defaults authored frames to the
    only valid Nexus-managed posture: dynamic, AI-native, and Rift-enabled
  - `FrameACLManager`, which now owns one frame-local ACL container per frame
    and each container owns separate named version chains plus one
    `FrameACLBuilder` family-draft surface for:
    - view
    - command
    - codegen
  - projection compilation through `create_frame_projection_sets(...)` and
    `create_frame_projection_sets_for_rift(...)`
  - ACL-change fan-out and batch refresh orchestration through
    `_refresh_rift_projection_sets_for_frames(...)`, with
    `_on_frame_acl_changed(...)` as the thin single-frame delegate into that
    batch path
- `Nexus` currently implements three internal frame topology behaviors:
  - `single` (behaviorally shared for all Rifts)
  - `indexed` (multiple named frames; shared-by-name access)
  - `one_per_workspace` (private frame per Rift)
  - creation remains explicit; Nexus does not auto-provision frames as part of
    these mode rules
  - Nexus-facing managed creation is Spellbook-mediated and rooted by default:
    - the caller may name the root conduit explicitly
    - the default root conduit name is `"root"`
    - the public result is the rooted conduit, not the frame
  - raw `NexusFrameManager` authoring is mode-constrained:
    - `single`
      - only the canonical shared default frame name may be created directly
    - `indexed`
      - explicit named direct creation remains allowed
    - `one_per_workspace`
      - raw direct manager creation is rejected because the path has no Rift
        owner identity, so callers must use the Rift-scoped Nexus creation path
- `Rift` owns:
  - per-Rift config snapshot
  - explicit target-frame contracts only
  - one `FrameLinkContract` per engaged target frame, each storing per-frame ACL selection across
    `view`, `command`, and `codegen` families
  - exactly one primary room created from `space_type`
  - one Rift-owned `RiftGate`
  - no eager Nexus-frame attachment state at Rift creation
  - no room registry or active-space switching surface
  - registration/active flags, logger, and live metadata
  - refresh orchestration for one Rift:
    - ask Nexus for fresh projection sets for the full assigned frame set or
      one changed-frame subset
    - store the current projection state on the Rift itself
    - apply updated projection state to the hosted room assets
- `RiftSpace` owns room-local identity, metadata, the durable attached
  Rift-backed `FrameViewer` asset, room-local workstation state, room-local
  command-system state, one room-local event system, and one room-local memory
  system.
- `CodegenRiftSpace` additionally owns one internal `CodegenSystem` and
  attaches it to the room-owned `CodegenCommandSystem` during room
  initialization.
- `RiftSpace` is now an asset host, not the projection manager:
  - generic rooms create one Rift-backed `FrameViewer` during room init
  - static rooms create one Rift-backed `StaticFrameViewer` during room init
  - the viewer reads current Rift projection truth on demand instead of
    storing a second local projection registry
  - frame-local viewer operations are explicit-frame operations; the viewer
    no longer owns default-frame routing state
- `Workstation` stores room-local strong/weak object, attribute, and method
  bindings plus one active target binding.
- `CommandSystem` is the room-local mediated command base. It owns shared
  command infrastructure, shared spell/runtime query helpers, and
  workstation-target execution helpers. Room-specific subclasses now own the
  commands that do not belong to every room:
  - `CapabilityCommandSystem` owns conduit discovery, link/contract-topology
    helpers, broad manual topology mutation, plus direct spell
    activation/reuse helpers
  - `StaticCommandSystem` owns live-only spell retrieval, reuse-only spell
    activation, and static spell-status helpers
  - `CodegenCommandSystem` keeps a selected runtime-helper surface, owns the
    public `validate_codegen(...)` / `execute_codegen(...)` seams, delegates
    those actions into the attached `CodegenSystem`, emits full-source
    codegen room-memory records through the room `RiftMemorySystem`, and
    owns the FULL research command family (2026-07-11): `research_walk`/
    `research_history`/`research_heads`/`research_residency`/
    `research_diff`/`research_campaign_view` reads plus
    `research_create_lane`/`research_attach`/`research_detach`/
    `research_join`/`research_archive` organization,
    `research_set_campaign`/`research_clear_campaign`, the five
    foresight commands (2026-07-11 agent QoL kit): `research_source`,
    `research_impact`, `research_module_graph`, `research_source_drift`,
    the crystal-well reads (`research_module` dossier, `research_part`,
    `research_parts` inventory, `research_part_diff` w/ automatic
    module-grain radius; `research_diff` offers the grain choice via
    strategy source/structural/parts),
    and the codegen-only `research_preview` (read-only candidate mock;
    composes an optional frame-scoped `validate_codegen` verdict when
    `frame_name` is given), plus the three synthesis verbs
    (`research_synthesize` surgical composition + preview,
    `research_stage_ancestry`/`research_clear_staged_ancestry` ambient
    multi-parent mint), plus the five composition commands
    (GroupedResearchNode subsystems: `research_group_register`/
    `research_group_recompose` organization and `research_group_view`/
    `research_group_diff`/`research_group_impact`/
    `research_group_footprint`/`research_group_drift`/
    `research_group_history` reads) - all mediated
    through the same command-action
    idiom, reaching the Aether-hosted MutationResearch root via a
    NON-CONSTRUCTING peek with a teach-grade refusal while research is
    inactive. `CapabilityCommandSystem` carries the twenty-one research
    READS only (seven record + eight foresight + six composition; no
    preview/synthesis/group-organization - they take or produce code or
    organize the record); static rooms carry none. Both rooms ADVERTISE
    their research family in `list_supported_command_methods`.
  When room-local memory callbacks are registered, one top-level successful
  public command call emits one `RiftMemory` record through the room-owned
  `RiftMemorySystem`.
- `CodegenSystem` is the internal engine beneath that command facade. It owns:
  - per-call `CodegenTransactionContext` creation
  - `CodegenValidator`
  - `CodegenNamespaceBuilder`
  - `CodegenCompiler`
  - `CodegenExecutor`
  - `CodegenMonitor`
  It validates before execution, builds the live namespace only after accepted
  validation, and keeps lifecycle-event publication inside the monitor layer.
- `StaticFrameViewer` wraps the generic viewer only in static rooms so the
  spell-facing query/project surface stays aligned with static live-only
  semantics while still reading current projection truth from `Rift`.
- `StaticRiftSpace`, `CapabilityRiftSpace`, and `CodegenRiftSpace` are all
  live room types.
- Current room-mode split:
  - `static`
    - static viewer overlay
    - weak-by-default workstation
    - no topology mutation
    - no direct create-path spell activation
    - live-only spell-facing surface
    - static-specific status helpers
  - `capability`
    - broad manual runtime/object access
    - strong-by-default workstation
    - no codegen
    - owns conduit discovery, link/contract-topology helpers, topology
      mutation, and direct spell activation/reuse command helpers
    - lower Melder frame truth still wins
  - `codegen`
    - keeps a selected runtime-helper subset rather than capability parity
    - owns one internal `CodegenSystem` under `CodegenRiftSpace`
    - routes public validate/execute requests through `CodegenCommandSystem`
      into that engine
    - emits full-source codegen room-memory records for top-level validation
      and execution actions
- Current limitation: `Rift.on_nexus_frame_disposed(...)` is still only a
  logging seam. A real Rift-level event orchestration layer has not been
  built yet.
- ACL selection model:
  - the old frame-global bundle chain is gone
  - one frame container now owns separate named revision chains for view,
    command, and codegen
  - same-name selection is convenience only at the storage layer; the three
    family chains can hold divergent named contracts
  - the `Rift` frame-link path, however, pins a fixed same-name selection:
    `FrameLinkContract` resolves view, command, and codegen to the attached
    `frame_name` contract, materializing it from `default` when absent.
    EVIDENCE: src/melder/nexus/rift/frame_link/frame_link_contract.py:_build_selected_contract_names
    + src/melder/nexus/rift/rift.py:_ensure_frame_link_acl_contract
  - chain bumps trigger ACL-driven projection refresh through `Nexus`
  - the single-frame ACL callback delegates into the same batch refresh
    primitive used for explicit multi-frame refresh
  - `Nexus` computes the union of impacted Rifts by checking whether each
    changed frame is present in each Rift's assigned frame-contract set
  - each impacted Rift refreshes one changed-frame subset in one call
  - each affected Rift updates its own projection registry and then applies
    view/command/codegen projection state to its hosted assets
  - the refresh barrier is config-backed through `NexusConfiguration`:
    - `projection_refresh_gate_enabled`
    - `projection_refresh_gate_timeout_seconds`
    - `projection_refresh_gate_poll_interval_seconds`
  - default behavior remains:
    - block new entrants through the impacted Rift gates
    - wait for in-flight tickets to drain
    - refresh each impacted Rift once for its changed-frame subset
    - reopen the gates

## Conduit Lifecycle (Normal and Lesser)
Normal Conduits:
- Created by `Spellbook.conjure` with policy and mode.
- Register themselves and their spell indices in Aether.
- Own one `ConduitCreations` registry, one `ConduitMeld` front door, one
  `ConduitWard`, one `CreationGate`, one `SpellSpacePool`, and one
  `ConduitPool`.
- Optionally register into ConduitCloud if dynamic and named.

Lesser Conduits:
- Created by `Conduit.create_lesser_conduit`.
- Inherit Spellbook and `SpellbookConfiguration`.
- Use `ConduitCreations` too; lesser behavior is driven by conduit state,
  pooled lesser reuse, and root-lineage ids rather than by a different
  creations class.
- Are linked into the parent's ConduitWard lineage tree.
- Reuse the root conduit pool and the root-lineage resolution conduit id.

Upgrades:
- `Conduit.upgrade_to_normal` converts a lesser conduit to normal in dynamic mode:
  transfers creations, rewires Meld, converts ward state, seeds resolution state,
  and registers into Aether/ConduitCloud.

## Binding and Registration Pipeline
Binding flow (local spell):
1) `Spellbook.bind` converts permissions and existence enums.
2) `Bind._bind_logic`:
   - Rejects modules and Protocols as concrete spells.
   - Uses SpellExaminer to build a binding profile.
   - Fingerprints the profile and constructs a SpellIndex.
   - Creates a Spell with metadata (existence, permissions, spellframe).
3) Spellbook attaches hooks and registers the spell into local maps.
4) SpellSystemStates registers the lineage and marks it dirty.
5) If a Conduit exists, ownership metadata is stamped and existing objects
   are registered into Creations.
6) If a Conduit exists, Spellbook registers the new SpellIndex in Aether for
   conduit-scoped spell-id lookups.

## Spell Examination Profile Responsibilities
- `SpellExaminer` is the registry-backed reflective facade over profile
  creation.
- The built-in public profile names are `general` and `detailed`.
- Binding profiles are used during `Bind`; resolution profiles are attached
  when a live `Spell` is available; the detailed profile then adds class and
  callable inspection payloads.
- `SpellExaminer.create_profile(...)` is the stable public front door and
  delegates all work to registered builders.

## Resolution Styles and DI Shapes
Melder resolution behavior is composed from binding style, lifetime scope,
and per-parameter DI shapes.

Canonical matrix artifact:
- `src/melder/aether/spellbook/resolution_style_matrix.py` is the owner-maintained
  source of truth for SpellType x Existence support policy.
- `ResolutionStyleMatrix.BINDING_FAMILY_POLICY` is canonical.
- `ResolutionStyleMatrix.MATRIX_BY_SPELL_TYPE` is an expanded projection from
  family policy, not an independent policy table.

Binding styles (SpellType = 14):
- Class-based spells: `SPELL`, `SPELL_WITH_SPELLFRAME`,
  `SPELL_WITH_BINDING_NAME`, `SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME`.
- Method/function spells: `METHOD`, `METHOD_WITH_BINDING_NAME`,
  `METHOD_WITH_SPELLFRAME`, `METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME`.
- Lambda methods: `LAMBDA_METHOD_WITH_BINDING_NAME`,
  `LAMBDA_METHOD_WITH_SPELLFRAME`,
  `LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME`.
- Existing creations: `EXISTING_CREATION`, `EXISTING_CREATION_WITH_SPELLFRAME`,
  `EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME`.

Lifetime scopes (Existence = 6):
- `unique`, `unique_per_conduit`, `many`, `unique_per_conduit_cluster`,
  `unique_per_conduit_lineage`, `unique_per_spell_space`.

Constraints:
- Method/lambda spells must use `Existence.unique` (enforced in `Bind`).

Parameter DI shapes (Phase 1, `ParameterDIShape`) - SIX members:
- `IGNORE`, `PLAIN`, `SINGLE_BY_ANNOTATION`, `COLLECTION_BY_ANNOTATION`,
  `SPELLMAP_DEFAULT`, `SPELL_CONTRACT`.

Declarative DI descriptors:
- `SpellMap` supports four explicit shapes:
  1) `SpellMap(MyService)` (concrete-type key).
  2) `SpellMap(ILogic)` (frame-type key).
  3) `SpellMap(MyService, spellframe=ILogic, binding_name="primary")`.
  4) `SpellMap(spell=None, spellframe=ILogic, binding_name="primary")`.
- `SpellContract` declares late-bound contract sockets for dynamic mode;
  linking conduits later supplies providers.

## DI Resolution Contract (Spec)
This section records the approved DI resolution contract (19-item spec) for
Melder. It is the reference for `Conduit.meld`, `Meld.meld`, `SpellInputUtils`,
`SpellMap` semantics, and SpellCompiler resolution behavior. Where the spec
and current implementation differ, the gap is called out explicitly.

Spec overview (Sections A-H):
- Root meld entry modes:
  - By spell_id (string) and by spell object (class/function).
  - By Protocol/frame type and by binding_name for disambiguation.
  - Root-level `spell_override` payload (dict/list/tuple).
  - By SpellName string (logical name) using a `(frame_key, bind_key)` index.
- Constructor DI shapes:
  - Type-hint DI by concrete class and Protocol frame.
  - SpellMap defaults and SpellMap frame-only mode.
  - Explicit method/lambda injection only via SpellMap or root meld.
  - Existing instance spells resolved by frame type.
- Collection DI:
  - `list[FrameType]` returns all implementations in registration order.
  - No separate IIndex-like DI concept.
- SpellMap semantics:
  - SpellMap mirrors type-hint DI but allows explicit spellframe/binding.
  - Override payloads are passed directly as positional/keyword overrides.
- Spell eligibility and uniqueness:
  - Classes, callables, and existing objects are valid spell targets.
  - Existing-object spells must bind as `Existence.unique`.
  - Single DI requires exactly one provider for a frame/key; ambiguity is a
    build-time error with guidance to SpellMap or list DI.
- Deep scan:
  - Post-init SpellMap resolution is not planned; no deep scan pass is implemented.
- Existence vs resolution:
  - Resolution decides the spell id; Existence controls lifecycle/reuse.
- Spellframe types:
  - Protocols/interfaces for contract DI; strings for grouping categories.

Spec vs implementation notes:
- Spec cites 19 items but includes Sections G/H labeled Items 20-21; treat
  numbering as advisory and follow the content as authoritative.
- Decision: Post-init SpellMap deep scan is not planned; users should express
  dependencies via constructor DI (SpellMap defaults/type hints).
- Decision: Conduit.meld public contract supports spell_id, spell object,
  spellframe, and spell_name; docstrings updated to reflect this multi-entry API.
- Implementation: Phase 4 `DuplicateSpellNameStrategy` scans local + contracted
  spells by `spell_name` and raises `DUPLICATE_SPELL_NAME` errors to prevent
  name-based resolution ambiguity.

## SpellCompiler and Validation Pipeline
Phases 1-4 are structural and run before Conduit creation:
- Phase 1: Requirements extraction.
- Phase 2: Symbolic graph build.
- Phase 3: Local frame creation and dependency graph assembly.
- Phase 4: Validation via SpellValidationSystem strategies.

Dirty terminology guardrail for this pipeline:
- `SpellCompilerArtifact._phase8_11_codegen_ir_dirty` is a local
  IR-freshness bit
  ("phase8_11 export payload is stale"), not a runtime validity gate.
- This bit is set by phase8/9/10/11 artifact replacement and flushed by
  `_capture_phase8_11_codegen_ir_if_dirty()` before codegen-creation compiler
  work and on
  `codegen_ir` reads.
- Change-control dirty roots remain a separate system:
  `ChangeControlManager.is_root_dirty(conduit_id, root_id)` is the meld gate
  checked by `Meld._gated_validation_required(...)`.
- EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:529-546`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:1966-1997`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:3513-3517`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:3579-3583`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:3647-3651`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py:3780-3787`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1403-1475`
  - `src/melder/aether/conduit/meld/meld.py:502-532`

PhaseScheduler coordinates these phases using worker threads and a shared
cancellation event; broken spells trigger SpellbookValidationError.

Phase 4 strategy coverage (non-exhaustive):
- Circular/self-dependency detection and dangling dependency checks.
- Resolution frame presence and duplicate spell name detection.
- Annotation/SpellMap shape validation and parameter policy enforcement.
- Contract provider presence checks (warnings in dynamic/late-binding cases).
- Binding-resolution cycle detection and callable profile hygiene.
- Existing-creation compatibility checks.

## Resolution and Meld Pipeline
Phases 5-11 are conduit-scoped and run after Phase 1-4:
- Phase 5: Root blueprint generation (root-only map for system validation plus
  per-spell blueprints for constructed spells).
- Phase 6: System validation via SpellSystemValidationSystem.
- Phase 7: Change control integration and cleanup of phase artifacts.
- Phase 8: `SpellAnalyzer` occurrence-graph analysis.
  - publishes `_occurrence_graph_analysis`
- Phase 9: `SpellArtifactProcessor` model fitting.
  - publishes `_spell_codegen_model`
- Phase 10: `SpellCodegenPlanner` plan fitting.
  - publishes `_spell_codegen_plan`
- Phase 11: `CodegenCreationSystem` spell-static runtime packaging.
  - publishes `_spell_codegen_creation`

Artifact ownership across phases 8-11:
- `SpellCompilerArtifact` is the spell-scoped OWNER of every phase-8-to-11 slot:
  `_occurrence_graph_analysis`, `_occurrence_order_analysis`,
  `_occurrence_instance_analysis`, `_occurrence_contract_analysis`,
  `_spell_codegen_model`, `_spell_codegen_plan`, `_spell_codegen_creation`,
  `_codegen_ir`, and `_phase8_11_codegen_ir_dirty`.
- The phase systems above PUBLISH INTO those slots; they do not own them. Read a
  phase's output from the artifact, not from the system that produced it.

Existing-creation spells bypass the live Phase 8-11 group because they have no
occurrence graph, no analyzer-derived model, and no codegen-creation payload
to build. They still resolve through `CreationContextBuilder`, but that builder
uses the existing-creation route directly instead of requiring a
`SpellCodegenCreation`.

Meld runtime flow:
- Conduit delegates `meld(...)` to `Meld` and fires pre/post resolve hooks.
- The conduit-facing runtime front door is `ConduitMeld`, which owns the
  caller-conduit `ConduitCreations` store.
- Spellspace-facing runtime uses `SpellSpaceMeld`, which owns the
  spellspace-local creations store plus a reference to the owner-conduit
  creations store.
- Meld resolves the target Spell and chooses reuse vs instantiate based on Existence.
- `Conduit.has_live_creation(...)` and `describe_live_creation_status(...)`
  delegate to `Meld` for a no-create probe that mirrors meld lookup semantics.
- Meld enforces structural/resolution validity and change-control gates before execution.
- `CreationContextBuilder` consumes `artifact._spell_codegen_creation` for
  constructed spells and builds one spell-bound `CreationContext`.
- `CreationContext` dispatches the prebuilt no-overrides lane directly and
  keeps only runtime-only override specialization behavior:
  - no-overrides executor for plain meld calls
  - override specialization executor for override/mutation paths
- Codegen-creation-produced executors perform reuse/construct/register directly
  against Creations per Existence rules.

Lazy validation at meld time:
- `Meld._ensure_lineage_resolvable` re-runs structural phases (1-4) when
  SpellSystemState validity is UNKNOWN or GATED, under the per-spell lock.
- If per-conduit resolution validity is UNKNOWN or GATED, it runs phases 5-11
  via `spell._spellbook._run_resolution_phases_for_target_spell(...)`.

## Contracts, Policies, and Permissions
- ConduitWard manages contracts between conduits and lineage links.
- Policies gate link behavior (default, whitelist_all, block_all, inbound_only, outbound_only).
- Permissions on each Spell (read/create/block) govern access by borrowers.
- ConduitCluster can auto-share root spell lineages among members. Sharing uses
  a cluster-scoped `root_spell_id` (`cluster:{name}:{owner_id}:{spell_id}`) so
  cluster teardown removes only cluster-created contracts, and defaults
  permissions to `spell.permissions` (fallback "create") with optional dependency
  linking.
- Conduit link/sever operations fire `on_conduit_post_link` and
  `on_conduit_post_unlink` hooks when configured.
- `SpellContract` declares late-bound sockets in dynamic mode; conduit linking
  supplies providers and triggers revalidation (Phases 5-11).
- `ContractProviderPresenceStrategy` is the Phase-4 owner of socket validation and
  emits exactly four codes: `CONTRACT_IN_AUTOMATIC_MODE` (contracts require dynamic
  mode), `SPELL_CONTRACT_INVALID`, `SPELL_CONTRACT_AMBIGUOUS` (more than one
  provider), and the warning `SPELL_CONTRACT_MISSING_PROVIDER`.
- Ownership transfer (`Conduit.transfer_spell_ownership`) migrates spell
  stewardship between conduits in dynamic mode, with optional creation moves,
  contract/cluster unsharing, and change-control gating.

## Existence and Scoping Model
Existence defines instance lifetimes:
- unique: per AethericFrame singleton.
- unique_per_conduit: per Conduit instance.
- many: new instance per meld.
- unique_per_conduit_cluster: registered via `Creations.add_creation` keyed by
  spell_id and shared across conduits via ConduitCluster contracts.
- unique_per_conduit_lineage: shared across lineage tree.
- unique_per_spell_space: scoped to a SpellSpace.

`Creations` is now a generic scoped live-object store with two registries:
- `_creations`
  - authoritative live runtime objects
- `_disposable_creations`
  - cleanup-only disposal metadata

`ConduitCreations` is the conduit/root specialization seam over that generic
store.
SpellSpace enforces active-scope semantics and supports reset/versioning.

## Logging and Observability
- `SafeLogger` remains the one logging adapter for both stdlib and channel
  loggers.
- `AetherUtilitySystem` is now the process-wide provider host for logger
  acquisition.
- `InitHelpers.resolve_channel_logger(...)` is the primary path for runtime
  objects that want hosted/provider-backed loggers.
- `InitHelpers.resolve_safe_logger(...)` is the path for explicit logger
  attachment after object boot.
- Automatic channel logger activation is now a utility-system policy gate that
  is intended to be owned by `AetherConfiguration`; when disabled, the channel
  path returns a null `SafeLogger`.
- `Aether`, `Spellbook`, `Conduit`, `Nexus`, and `Rift` now all resolve
  logging through that provider model.
- Cleanup and teardown use best-effort logging to avoid cascading failures.

## Ownership, Lifecycle, and Cleanup
- Cleanable defines the idempotent cleanup contract.
- Spellbook cleanup:
  - Cleans spells and SpellIndex keys.
  - Cleans configuration and validators.
  - Nulls references and cleans logger last.
- Conduit cleanup:
  - Fires hooks, tears down Meld, ConduitWard, and Creations.
  - Clears hooks and logger last.
- Aether cleanup:
  - Cleans frames, resets singleton state, and cleans logger.
- AetherUtilitySystem cleanup:
  - Clears channel-resolver and default-logger providers and resets singleton
    state for tests.
- Nexus cleanup:
  - Cleans registered Rifts, Nexus frame records, and logger state.
- Rift cleanup:
  - Cleans the one owned space, owned config snapshot, owned `RiftGate`, and
    engaged `FrameLinkContract` objects, then clears Rift-local metadata and
    cleans logger last.
- Creations cleanup:
  - Calls configured disposal methods; may raise ExceptionGroup.

## Extension Points
- `SpellbookConfiguration` hooks for conduit lifecycle and meld pipeline.
- Logger provider registration through `AetherUtilitySystem` and the hosted
  `InitHelpers` resolution path.
- Spellbook binding hooks (pre/activation/post).
- Dynamic Conduit policies and ConduitCluster auto-sharing.
- Validation strategies registered in SpellValidationSystem.

## C3 and C2 Cross-Reference
Detailed C3 and C2 component descriptions are maintained in:
- `context_compass/system_docs/src_components.md`

## Runtime Type Names (Concrete, No Interface Layer)

The runtime uses CONCRETE types on these surfaces. There is no `I*` interface
layer for them; agents should type against the concrete classes:

- `RiftEvent`                  - room-local event record
- `RiftMemory`                 - room-local memory record
- `CodegenValidationResult`    - codegen validation verdict
- `CodegenExecutionResult`     - codegen execution outcome
- `CodegenTransactionContext`  - per-call codegen transaction context
- `Conduit`                    - conduit; link targets and rooted-creation returns

`Conduit.link(...)` performs a CONCRETE `isinstance(target_conduit, Conduit)`
check. A conduit-shaped object that is not a `Conduit` subclass is rejected with
"Expected Conduit-compatible object, got {type}". This is not a structural
contract and cannot be satisfied by duck typing.

EVIDENCE:
- src/melder/aether/conduit/conduit.py:4342-4344
- src/melder/nexus/nexus_frame_builder.py:255 (`create(...) -> Conduit`)
- src/melder/nexus/rift/rift_space/event_system/rift_event.py
- src/melder/nexus/rift/rift_space/memory_system/rift_memory.py
- src/melder/nexus/rift/codegen_system/validation/codegen_validation_result.py
- src/melder/nexus/rift/codegen_system/execution/codegen_execution_result.py
- src/melder/nexus/rift/codegen_system/codegen_transaction_context.py

## Open Questions
- SpellContract is now evidenced, not unknown: its sockets are validated in Phase 4
  (automatic mode -> error, missing provider -> warning), and contract-dependent
  revalidation is wired by `SpellSystemStates.mark_contract_dependents_dirty`
  callers plus meld-time resolution gating.
- The mutation override overlay is live: `Spell.apply_mutation_override` /
  `Spell.clear_mutation_override` emit the `mutation_contract_set` /
  `mutation_contract_cleared` change reasons.
- Remaining unknown: producer call sites for `SpellState.contract_violation`,
  `SpellState.mutation_candidate`, `SpellState.mutation_quarantined`, and
  `SpellState.mutation_failed` are still not present in current `src/melder`
  callsite sweeps.
  Follow-up stories:
  `STORY-2026-02-13-spellstate-advanced-flag-producers`,
  `STORY-2026-02-13-mutation-research-runtime-wiring`.
  Status: blocked (producers await the MR runtime-seam slice; the ResearchSet
  record landed 2026-07-11 but deliberately defers select/staged/promoted acts
  until the notch/bind_inactive seams are real).

## Persistence & Restore Architecture (promoted from patch restore_engine_2026_07_07 + successor lanes, 2026-07-07)

### Canonical configuration/boot order (owner-ruled)
Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch -> Nexus ->
AethericFrame -> Spellbook -> Conduit|Ward. The restore engine's stage
machine mirrors this order exactly; frames posture BEFORE books because
frames own the dynamic gate that conjure's check_system_state reads.

### EMIT model invariants
- The crystallizer is a passive sink: structural units push twins at their
  configuration lock-in and pivotal runtime points; the sink never reaches
  into emitters. Bind owns structural emission; the ONLY sanctioned
  catch-up is the aether root at crystallizer activation (a single root
  emission, never a world walk), because the aether hosts its own recorder
  and legally precedes it.
- R-A covenant: crystallizer-off worlds stay byte-identical; recording
  changes no runtime behavior.
- Every snapshot is self-describing: the recorder's policy twin rides
  every sealed window.
- Records carry plain values only; callables appear as presence flags
  (logger resolvers, DB handlers) and reload as code-participation
  reports.

### Restore invariants
- Checkpoint-shaped replay through PUBLIC verbs only - never raw map
  merges; the engine is a driver, not a surface.
- Never-rehydrate-ULIDs: fresh identities always; recorded ids live only
  in the report's translation map. Spell SHA256 ids are content-derived
  and stable, so custody replays by recorded id.
- All-or-nothing: any stage failure tears down every built unit in
  reverse order and re-raises with the cause chained.
- Re-emission is intended: the rebuilt world re-records itself into the
  fresh active profile as it comes up.
- Honesty ledger: everything unreplayable is a named shortfall (never
  silent) - hook callables, non-hydratable/synthetic bind targets
  (loader-chain M3 pending), cluster leader election, index
  subscriptions, MutationResearch.

### Durability layering
Ledger (in-process, FIFO at max_persistence_crystals) -> local cache
(profile folders under __crystallizer_cache__, FIFO file cap at the same
limit) -> user DB via ExternalPersistenceManager callables (unbounded,
explicitly the user's opt-in and operational responsibility). Boot lane:
CrystallizerBootstrap composes activation, manager attach, cache reload,
remote pull with local re-store, chain-verification gating, and
newest-checkpoint restore into one fluent, single-use chain.

## Persistence Subsystem Topology (promoted from patch crystallizer_decomposition_2026_07_09, 2026-07-10)

The 2026-07-09/10 decomposition replaced the persistence god object with
the V3 subsystem model (canonical anchor:
artifacts/2026-07-09_crystallizer_philosophy_v3.md). Owner-run 614/614
across the crystallizer test tree validates it.

Crystallizer (thin facade, byte-compatible public surface)
├── persistence/PersistenceSystem      THE RECORD - profiles, journal,
│     checkpoint minting/retention, chain verify, feedstock
│     (cached_item_forms, detach_profile_chain), the insert sink.
│     In-process truth ONLY; calls nobody; constructs no engines.
├── asset_management/AssetManagementSystem   BYTES AT REST - owns
│     CrystallizerCache + ExternalPersistenceManager; flush =
│     seal-then-ship (cache write, FIFO retention at the record's live
│     cap, lenient upload leg - one feedstock pull, both legs);
│     reloads feed the record's sink; formation files live here.
└── crystal_loader_system/CrystalLoaderSystem   THE UNFOLD - owns
      LoadAdmission (LoadPlan -> gated engine -> scope adjudication;
      renamed from BootMediator 2026-07-11),
      RestoreEngine (refuse_on_blockers at the fold->preflight seam:
      blockers refuse BEFORE any replay, teach-grade), bootstrap_loader
      (thinned; old preflight-gate knob absorbed as a no-op), and
      durable last-load state (describe_last_load).

Shared surfaces: crystallizer/crystals/ is the package-level twin
vocabulary (carrier law: crystals carry results, never analyzers);
crystallizer/crystal_analysis/ is the shared analyzer service (custody
strategies with physical SHA256 fingerprints, fact strategies incl.
export_surface + topological load order, the relocated preflight set) -
consumed by SpellCrystal at bind and by the loader's admission, and
re-runnable over RETAINED payloads (the MutationResearch seam).

Laws: EDGE (acyclic - the record calls nobody; borrowers clean before
the record), LOCK (one-way facade -> subsystem -> record -> profile),
VERDICT (blockers refuse standard, warnings proceed + report; conduit/
frame-scoped loads adjudicate expected frame-posture warnings into the
additive "admission" view without rewriting raw findings). All prior
restore invariants (all-or-nothing, never-rehydrate-ULIDs, re-emission,
shortfall honesty, R-A covenant) are unchanged.

## V3 Horizon Architecture (promoted 2026-07-12 from six patch dirs; owner-run full-tree green)

- LAZY FRAMES + LOADGATE (Aether substrate): `import melder` builds ZERO
  frames - the first Spellbook births the frame it names; collapsed
  config falls back to a lazily created "default". One Aether-hosted
  LoadGate (constructed before any frame CAN exist, so mid-load-born
  frames inherit coverage) grants a crystallizer load exclusive
  system authority: acquire+drain at load start, mediator
  wait_for_passage at every NEW-ROOT transaction start (the loading
  thread passes free; joins never gate), release in finally. The gate
  reaches mediators via an additive ctor kwarg threaded frame ->
  DevOpsManager -> CCM -> TransactionMediator. Recorded frame postures
  now PROPAGATE their transaction wait bound into the live mediator at
  bind (the disable_* gates were already live-reads).
- LOAD SCOPES MATURE: formations COMPOSE into live worlds - detached-
  window retargeting (copy-on-write; single-frame law), host preflight
  in LoadAdmission (registry reads only; collisions are blockers that
  refuse pre-engine or downgrade to "skipped_existing"), engine skip
  lanes (unnamed conjure fallback; cluster reuse). Restore units:
  world, frame slice, conduit slice.
- PHYSICAL CUSTODY (opt-in): user-source TEXT rides the SpellCrystal
  beside the M3 synthetic sources; absent files rebuild through the
  synthetic module lane (live files always win; drift/tamper are
  preflight rows). Fresh pods rebuild user-file spells from the record
  alone.
- IMPACT VIEW: ImpactEngine turns the custody manifests into blast-
  radius answers (transitive reverse-import closure; source-drift
  report) behind one read seam (describe_spell_crystals) and one facade
  (analyze_impact). Read-only by law.
- EXTERNAL MESH: ONE generic callable quartet (store/fetch/list/delete,
  kind-partitioned) carries ANY mesh unit to the user's DB - legacy
  checkpoint handlers bridge to it; formations ship at save; an opt-in
  emission tap streams every recorded twin (payload captured BEFORE
  record - the thread-safety law - shipped after); melder-driven remote
  retention is opt-in via the delete lane. Callables-first stands: the
  record stores presence flags, never code.
- RECORD VERSIONING: RecordVersion "1.0.0" stamps every durable
  artifact (cached items, formation records, tap envelopes); readers
  gate on the MAJOR (newer refuses with the upgrade instruction;
  pre-versioning reads as 0.0.0 into the tolerance lanes). The twin
  describe() dict IS the interface: classes in, lossless JSON across
  the boundary.
- MR = BUILD STAGE: checkpointed worlds unfold WITH their research
  (reload verb -> hosted root -> folded-truth activation -> wholesale
  composition rebuild; disabled/cleaned/pre-Phase-B lanes honest;
  world-scope-only with expected_for_scope adjudication on formation
  loads).

## Three-Lane Tail (promoted 2026-07-11; owner-directed finish of the public_cloud_seams, source_drift_preflight, and spell_index_graft lanes)

- PUBLIC CLOUD SEAMS: cross-package cloud access is public-verb-only.
  AethericFrame.conduit_cloud (property) + ConduitCloud.has_cluster_name
  retire the two documented private seams; every crystallizer reader
  repointed; zero behavior change (same objects, same answers).
- SOURCE DRIFT PREFLIGHT (10th default row): every load re-hashes EVERY
  bind-time module fingerprint against disk, retention-agnostic - a
  restore ANNOUNCES working-tree divergence from the sealed world before
  building anything (drift/absent = warnings, never refusal);
  UserSourceIntegrityStrategy narrows to retained-text tamper only.
- SPELL-INDEX GRAFT: restore grain below the conduit slice - ONE index
  (members + custody + selection, parked members included) captured as
  a versioned dict and re-integrated into any LIVE conjured book through
  normal verbs only (bind creates the fresh index; bind_inactive parks;
  resident members refuse or skip - existing indexes are NEVER mutated).
  Retained-text worlds rebuild through the shared user_world_rebuild
  lane the engine also delegates to. Grafts are user-verb activity: no
  LoadGate, emissions re-record freely.


# Material migrated out of src_components.md (2026-08-01)

Moved during the recomposition of `src_components.md` to its Required Section
Contract. Headings that arrived wrapped across two to five physical lines were
unwrapped. NOTHING HERE IS DELETED.

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


## Crystallizer Persistence & Restore (promoted from patch restore_engine_2026_07_07 + successor lanes, 2026-07-07)

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


## Subsystem Decomposition (promoted from patch crystallizer_decomposition_2026_07_09, 2026-07-10)

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


## V3 Horizon Iteration (promoted 2026-07-12 from six patch dirs: aether_lazy_frames_and_load_gate_2026_07_11, crystallizer_v3_horizon_2026_07_11, crystallizer_s2_user_source_ retention_2026_07_11, crystallizer_s3_impact_engine_2026_07_11, crystallizer_external_mesh_2026_07_12, mr_restore_build_stage_2026_07_11)

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


## Three-Lane Tail (promoted 2026-07-11 from patch dirs public_cloud_seams_2026_07_12, source_drift_preflight_2026_07_12, spell_index_graft_2026_07_12; owner-directed finish)

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

