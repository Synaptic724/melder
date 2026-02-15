# Story: PathId interning for socket and occurrence paths

- Completed: 2026-02-01
- Summary: PathId interning is integrated for socket/occurrence paths with
  tests updated to use path ids and component docs noting PathRegistry usage.

## Metadata
- Story ID: STORY-2026-02-01-pathid-interning
- Epic: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-01

## User Narrative
As a runtime maintainer, I want path segments interned into stable PathIds so that
Phase 5 and Phase 8 stop allocating path tuples on every socket/occurrence,
reducing conjure overhead and memory churn without changing targeting semantics.

## Value / MRP Alignment
This keeps the conjure pipeline fast and predictable by eliminating avoidable
allocation hot spots while preserving stable override behavior and diagnostics.

## Requirements (Functional)
- Introduce a per-blueprint PathId registry that interns path segments without
  any module-level cache.
- SocketRef stores a path_id (not a param_path tuple), and DagIndex indexes by
  path_id while still supporting TargetSpec PATH lookups from segment strings.
- Phase 5 socket overlay and Phase 8 occurrence planning use PathId extension
  instead of tuple concatenation.
- Diagnostics and override key formatting still render human-readable paths.
- Override/mutation targeting behavior remains unchanged for PATH/UNIQUE/BROADCAST.

## Requirements (Non-Functional)
- No public API shape changes.
- No module-level mutable state or global caches.
- Keep hot-path allocations minimal; only materialize tuple paths for
  diagnostics or external string keys.

## Scope Boundaries
- In scope:
  - PathId registry implementation and integration across SocketRef, DagIndex,
    root blueprint building, occurrence planning, patch map building, and
    override/mutation targeting.
  - Test updates for new path-id representation.
- Out of scope:
  - Other conjure optimizations unrelated to path churn.
  - Changes to TargetSpec syntax or override payload shapes.

## Dependencies / Related Work
- Root blueprint overlay: `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- DagIndex/SocketRef: `src/melder/spellbook/spell_crafter/dag/dag_index.py`
- Occurrence planning: `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- Patch maps: `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-01-pathid-interning - Replace tuple paths with PathIds in Phase 5/8 and update targeting.

## Acceptance Criteria
- Phase 5 socket overlay no longer allocates path tuples via path + (segment,).
- Phase 8 occurrence planning uses PathIds for path extension and comparison.
- Override targeting still accepts PATH strings and produces the same matching
  behavior and error messages.
- Tests updated to reflect path-id representation.

## Validation / Test Plan
- Agent-ran:
  - `python -m pytest tests\integration\melder\spellbook\test_spellbook_integration_validation_system.py::test_spell_validation_phase6_reports_socket_ref_index_mismatch tests\unit\melder\aether\conduit\meld\meld_engine\test_meld_engine.py::test_apply_mutation_overrides_requires_blueprint tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_execute_applies_patch_maps_for_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_merges_context_and_override_map tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_ignores_non_dict_context_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_filters_non_root_or_deep_paths tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_ignores_non_root_override_map_entries tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_empty_inputs_return_empty tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_execute_blueprint_ignores_non_dict_overrides tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context.py::test_build_frame_overrides_rejects_non_iterable_args`
- User-reported: tests run (details UNKNOWN).

## UX / API / Data Notes
- Internal-only change; external override syntax and errors remain unchanged.

## Risks / Mitigations
- Risk: missed call sites that still assume param_path tuples.
  Mitigation: exhaustive search for `param_path` and `OccurrenceKey` usages and
  update tests accordingly.

## Open Questions
- None.

## Decision Log
- 2026-02-01: Implement PathId interning for socket and occurrence paths to
  remove tuple churn in Phase 5 and Phase 8.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Completed; ticket ready to archive.

