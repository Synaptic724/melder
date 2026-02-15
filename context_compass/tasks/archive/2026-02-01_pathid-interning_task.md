# Task: Implement PathId interning for socket and occurrence paths

- Completed: 2026-02-01
- Summary: PathId registry and path-id handling are wired through socket/occurrence paths,
  with tests updated for the new representation and component docs noting PathId usage.

## Metadata
- Task ID: TASK-2026-02-01-pathid-interning
- Story: STORY-2026-02-01-pathid-interning
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-01

## Objective
Replace tuple-based path expansion in Phase 5/8 with PathId interning while
preserving override targeting behavior and diagnostics.

## Scope Boundaries
- In scope:
  - Add per-blueprint PathId registry.
  - Migrate SocketRef/DagIndex to path_id storage and lookup.
  - Update Phase 5 socket overlay, Phase 8 occurrence planning, patch maps,
    override/mutation targeting, and diagnostics.
  - Update tests that assert param_path tuple behavior.
- Out of scope:
  - Other conjure hotpath changes or unrelated refactors.

## Steps / Checklist
- [x] Implement PathId registry and integrate into RootResolutionBlueprint/DagIndex.
- [x] Update SocketRef creation and consumers to use path_id.
- [x] Migrate Phase 5 socket overlay and Phase 8 occurrence planning to PathId extension.
- [x] Update patch map construction and diagnostics to materialize paths only when needed.
- [x] Update tests for new path-id representation and run targeted checks (user-run).

## Deliverables
- PathId-backed socket and occurrence path handling in core spell_crafter pipeline.
- Updated tests and docs where path tuple assumptions existed.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/dag/dag_index.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- `src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- Related tests under `tests/`

## Validation
- Agent-ran:
  - `python -m pytest tests\integration\melder\spellbook\test_spellbook_integration_validation_system.py::test_spell_validation_phase6_reports_socket_ref_index_mismatch tests\unit\melder\aether\conduit\meld\meld_engine\test_meld_engine.py::test_apply_mutation_overrides_requires_blueprint tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_execute_applies_patch_maps_for_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_merges_context_and_override_map tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_ignores_non_dict_context_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_filters_non_root_or_deep_paths tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_ignores_non_root_override_map_entries tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_empty_inputs_return_empty tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_execute_blueprint_ignores_non_dict_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_rejects_non_iterable_args`
- User-reported: tests run (details UNKNOWN).

## Risks / Rollback Notes
- Risk: missed path_id conversion leading to incorrect override targeting.
  Rollback: revert to tuple-based param_path handling in SocketRef/DagIndex.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Completed; ticket ready to archive.

