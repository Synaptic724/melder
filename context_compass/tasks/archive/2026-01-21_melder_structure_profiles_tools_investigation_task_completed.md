- Completed: 2026-01-22
- Summary: Documented structure profile truth sources, schema sketch, and tooling query outputs.

# Task: Investigate structure profile data sources and schema

## Metadata
- Task ID: TASK-2026-01-21-melder-structure-profiles-tools-investigation
- Story: STORY-2026-01-21-melder-structure-profiles-tools
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22

## Objective
Inventory existing runtime signals (spells, resolution evidence, contracts,
maps) and draft a minimal structure profile schema with truth/derived separation.

## Scope Boundaries
- In scope:
  - Identify available truth sources in Spellbook/Conduit/Aether.
  - Propose schema for frame/conduit/spellbook profiles.
  - Define provenance and confidence fields for derived hints.
- Out of scope:
  - Code changes.
  - Implementation of profiles or tool queries.

## Steps / Checklist
- [x] Inventory runtime data sources and their access points.
- [x] Draft schema for structure profiles (truth vs derived).
- [x] Propose tool query outputs and ranking inputs.
- [x] Record open questions and assumptions.

## Deliverables
- Investigation notes added to the task Context / Handoff Summary.

## Files / Paths Impacted
- Documentation only (this task ticket).

## Validation
- Not run (investigation-only).

## Risks / Rollback Notes
- Risk: Missing data sources at runtime.
  - Mitigation: call out gaps explicitly.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Verification status (2026-01-22):
  - Verified current registry ownership and fields for AethericFrame, Spellbook, ConduitWard/Contract/Detail, ConduitCluster, SpellSystemStates/SpellSystemState/ConduitResolutionState, SpellLocalTopology, SpellRequirements/SpellParameterRequirement, and SpellMap/SpellContract/MutationContract using the cited source files below.
- Truth data sources (runtime registries):
  - Frame registries: `AethericFrame` owns `_conduits`, `_spell_registry` (conduit_id -> set[SpellIndex]), `_version_registry`, `_conduit_clusters`, `_spell_system_states`, and `DevOpsManager`. (`src/melder/aether/aetheric_frame.py`)
  - Spellbook registries: `_spells` (SpellIndex -> Spell), `_lookup_spells`, `_spell_versions`, `_contracted_spells` per peer conduit, `_lookup_contracted_spells`, `_contracted_versions`. (`src/melder/spellbook/spellbook.py`)
  - ConduitWard contract graph: `_initiated_index`, `_received_index`, `_contracts` (Contract objects); `Contract` holds per-ward `Detail` maps with SpellIndex, spell_id, permissions, contract_type, sources. (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`, `src/melder/aether/conduit/conduit_ward/contract/contract.py`, `src/melder/aether/conduit/conduit_ward/contract/details.py`)
  - ConduitCluster membership + shared roots: `members`, `shared_spells`, `auto_link_dependencies`. (`src/melder/aether/conduit/conduit_cluster.py`)
  - SpellSystemStates: `SpellSystemState` per lineage (direct dependencies/dependents, validity, flags), `_local_topologies` per spell id, collection dependency indices per spellbook, and `ConduitResolutionState` per conduit. (`src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`, `src/melder/aether/dev_ops/spell_system_states/spell_system_state.py`, `src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py`)
  - SpellLocalTopology: sockets with `dependency_key`, `contract_key`, `target_spell_ids`, `socket_kind`, collection flags. (`src/melder/spellbook/spell_crafter/topology/spell_local_topology.py`)
  - SpellRequirements: parameter annotations, DI shape, collection element annotation, SpellMap defaults. (`src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements.py`, `src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_parameter_requirements.py`)
  - Explicit maps/contracts: `SpellMap`, `SpellContract`, `MutationContract` for explicit dependency intent. (`src/melder/aether/conduit/meld/contracts/spell_map.py`, `src/melder/aether/conduit/meld/contracts/spell_contract.py`, `src/melder/aether/conduit/meld/contracts/mutation_contract.py`)
- Minimal schema sketch (truth vs derived):
  - FrameStructureProfile: frame id/name, conduit list, spell registry snapshot, lineage graph, contract/link edges, cluster membership; keep `truth` and `derived` sections separate.
  - ConduitStructureProfile: conduit id/state/policy, owned/borrowed spells, inbound/outbound links, resolution validity snapshot.
  - SpellStructureRecord: spell_id + lineage id, owner conduit, binding key (frame_key/binding_name), existence, spell_type, permissions, dependencies (SpellSystemState + SpellLocalTopology), contract sockets, SpellMap defaults.
  - StructureHint: kind, description, confidence, provenance (source + method), scope (frame/conduit/spellbook).
- Tool output sketch + ranking inputs:
  - `describe_spell_structure(spell_id)` built from SpellLocalTopology sockets + SpellSystemState edges + contract links.
  - `find_related_spells(spell_id, k)` uses shared dependencies, shared contracts, lineage proximity, and fan-in/out (graph metrics).
  - `explain_dependency_path(root, target)` uses SpellSystemState direct dependencies and SpellLocalTopology edges.
  - `list_subsystems()` uses cluster membership plus derived community detection (graph only).
  - `recommend_next_inspection(spell_id)` uses topological neighbors and contract peers.
- Gaps / open questions:
  - No co-resolution frequency or runtime call graph today; derived hints should be graph-based and marked low confidence.
  - Many truth sources are internal/private; structure profile builder likely needs to live in-core or expose new read-only accessors.
  - AI profiles are explicitly disallowed for now; structure profiles should not depend on AI profile pipeline.
  - SpellMap/SpellContract intent is available at parameter requirement time; decide whether to store in structure profile or re-derive per request.
