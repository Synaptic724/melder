# component_patch_aether_singleton

## Metadata
- Patch ID: host_read_surface_2026_09_29
- Component: Aether Singleton (Global Runtime) - Aether Frame Registry
- Status: archived without promotion (owner turn-in, 2026-09-29)
- Owner: user (agent melder_0)
- Created: 2026-09-29T21:27:17Z
- Updated: 2026-09-29T22:26:28Z

## Component Purpose and Boundary
- Current boundary: Aether owns the frame registry; frames are created by `_ensure_frame` (Spellbook, Nexus,
  restore) and `_create_frame` (Nexus managed); every public frame-scoped call resolves through
  `_get_existing_frame`, which creates "default" when it is missing.
- Target boundary: unchanged, plus three public lookups that read the registry without creating anything.

## Before/After Behavior Summary
- Before: no public call returned a frame; a host read `Aether._aetheric_frames` under `Aether._lock`.
- After: `find_frame(name)` returns the registered live frame or None; `get_frame(name)` returns it or raises
  ValueError ("Aetheric frame 'X' does not exist." plus how to create or probe it); `list_frame_names()` returns
  the live frames' names in registration order. A registered frame that already reads `cleaned` is absent.

## Interface Deltas
- Inputs: `aetheric_frame_name: str` (no default) for find/get; none for list.
- Outputs: `Optional[AethericFrame]`, `AethericFrame`, `tuple[str, ...]`.
- Error semantics: TypeError naming the call for a non-string name; ValueError from `get_frame` when absent;
  RuntimeError once Aether is cleaned.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none. No frame is created, sealed or detached by a lookup.

## Failure Mode Deltas
- New failure mode: `get_frame` ValueError for an absent frame (a lookup, not a creation failure).
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. No lock: `find_frame` is one `dict.get`; `list_frame_names` iterates one `dict.copy()`. This keeps the lookups
   off the Aether -> Nexus lock order that `_detach_cleaned_frame` establishes.
2. `check_cleaned()` runs first because cleanup deletes the registry after marking Aether cleaned.

## Validation Expectations
- Test/validation item: absent frame -> None / ValueError, "default" not created by any lookup, the Aether
  configuration stays unsealed after lookups on a fresh world, registration order, cleaned frames absent,
  non-string names, cleaned Aether, concurrent creation while listing.
- Evidence target: artifacts/host_read_surface_20260929/ logs.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: landed at 0.2.8208 as specified (`Aether.find_frame`, `get_frame`, `list_frame_names` and `_find_registered_frame`; src/melder/aether/aether.py:1687-1835), with the tests this patch lists.
  Not promoted into the canonical system documents: the owner turned the lane in first.
- Remaining risks: none known.
- Next entrypoint: `src/melder/aether/aether.py`, the lookup family after `_resolve_lookup_frame`.
- Promotion owner: tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
