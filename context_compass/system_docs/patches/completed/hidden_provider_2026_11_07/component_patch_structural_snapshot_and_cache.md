# component_patch_structural_snapshot_and_cache

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: `StructuralSnapshot` (structural tier rows) and the creation-cache envelope
  (`CachingSystem.CACHE_VERSION_HISTORY`; Component: Spellbook Core)
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: the structural tier stores one row per `SpellSocketDescriptor` field (10-tuple, payload format
  2) and replays phases 3-4 on a full hit; the envelope admits only the current generation (26) and release.
- Target boundary: unchanged; the rows carry the two new descriptor fields, and generation 27 retires older bundles.

## Before/After Behavior Summary
- Before: row = (param_name, position, socket_kind_name, is_collection, is_optional, target_spell_ids, dependency_key,
  contract_key, referenced_spell_ids, parameter_kind); `PAYLOAD_FORMAT` 2; generation 26 (`class_lookup_bare_spells`).
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:138, :413-426,
  :498-532 (`len(row) != 10` at :510), :535-577; src/melder/utilities/caching_system/caching_system.py:245-281.
- After:
  1. Row = the ten fields + `hidden_spell_ids` + `hidden_frame_keys` (12-tuple, both tuples of str), in
     `build_payload`, `_socket_row_well_formed` (length 12, the two new fields checked like `referenced_spell_ids`)
     and `rebuild_topology`; the class docstring's row list and "Payload schema (`PAYLOAD_FORMAT` 3)".
  2. `PAYLOAD_FORMAT` 3: a format-2 payload fails `payload_well_formed` (format and row length) and misses.
  3. `CACHE_VERSION_HISTORY[27] = "class_lookup_hidden_providers"`, with the history comment: "Version 27 retires
     bundles captured before HIDDEN_PROVIDER (TASK-2026-11-07-spellframe_ambiguity_validation_check part (a)): their
     structural rows replay a valid verdict for a consumer whose class lookup misses a class bound only under a
     spellframe or a binding name, which Phase 4 now refuses, and their socket rows lack the hidden-candidate fields
     (payload format 3). A release change already cold-starts every bundle (version 9); the bump records why, as
     versions 18, 20 and 26 did for the earlier matching-rule changes."
- Why rows must carry the fields: a valid dynamic spell's empty required `list[Class]` socket can hold
  `hidden_spell_ids` (Phase 6 names them in its WARNING); a replay without them would differ from the cold topology
  (the round-trip contract). A socket refusing its spell (UNRESOLVED_INPUT with ids) is never captured as replayable:
  `payload_well_formed` admits only `valid` and `gated`.

## Interface Deltas
- Inputs: the two descriptor fields.
- Outputs: 12-field rows; `PAYLOAD_FORMAT` 3 in every structural key; `CachingSystem.CURRENT_VERSION` 27.
- Error semantics: none (an older bundle or payload is cold, never an error).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: a full structural hit replaying "valid" for a consumer HIDDEN_PROVIDER refuses.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Lands with the descriptor fields (component_patch_compiler_phase_3.md).
2. Phase 8 signature rows (`spell_occurrence_graph_analyzer_strategy.py`) do NOT add the fields: hidden ids never
   change a plan (a spell carrying them on a single socket does not plan; an empty list injects `[]` either way).

## Validation Expectations
- Updated by design: tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py -
  `PAYLOAD_FORMAT == 2` (test_structural_key_holds_format_id_and_sorted_refs), `_good_payload`'s 10-field row and the
  `"format": 2` literals (the shape-violation parametrization, the no-sections case) -> format 3, 12 fields, plus a
  violation case for each new field (a list instead of a tuple, a non-str member);
  tests/integration/melder/spellbook/test_cache_schema_version_integration.py - `EXPECTED_CACHE_VERSION_HISTORY` gains
  27.
- Added: a round-trip test whose topology carries non-empty hidden fields; the hydrate and parity component tests'
  registry snapshots (`_registry_snapshot`, hand-built 10-field tuples) extended with the two fields, so the cold and
  replayed registries are compared on them too.
- Evidence target 1: the full suite, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (generation 27 and format 3 settled, chat 2026-11-07).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: a test pinning 26 or format 2 not found by grep (none found besides those listed).
- Next entrypoint: `StructuralSnapshot.build_payload`, then `CachingSystem.CACHE_VERSION_HISTORY`.
