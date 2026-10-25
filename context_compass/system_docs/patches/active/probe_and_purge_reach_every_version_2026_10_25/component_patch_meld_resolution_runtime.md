# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: probe_and_purge_reach_every_version_2026_10_25
- Component: Meld Resolution Runtime - the Meld base, ConduitMeld and SpellSpaceMeld
  (`src/melder/aether/conduit/meld/meld.py`, `conduit_meld.py`, `spellspace_meld.py`)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T03:03:37Z
- Updated: 2026-10-25T03:03:37Z

## Component Purpose and Boundary
- Current boundary: purge and the live-creation probes discover their target through `Meld._resolve_spell`, the
  meld lookup. Its spell_id branch, `_resolve_spell_by_id`, reads the Book's active pool, its active versions and
  each lender's active copies - lock-free, the maps the Meld holds by reference - and raises KeyError for anything
  else, a parked version and a parked borrowed copy included. Store selection and authority come after discovery
  and read only the Spell (existence, owner stamp): `ConduitMeld._get_purge_creations` and the doors'
  `_describe_spell_live_creation_status`; `SpellSpaceMeld.purge` keeps its two lifetimes and its own store.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:605-672
  - src/melder/aether/conduit/meld/meld.py:673-730
  - src/melder/aether/conduit/meld/meld.py:2067-2187
  - src/melder/aether/conduit/meld/conduit_meld.py:150-281
  - src/melder/aether/conduit/meld/conduit_meld.py:892-956
  - src/melder/aether/conduit/meld/conduit_meld.py:987-1116
  - src/melder/aether/conduit/meld/spellspace_meld.py:174-240
  - src/melder/aether/conduit/meld/spellspace_meld.py:836-1051
- Target boundary: the doors that build nothing discover a spell_id through `_resolve_probe_target` - the active
  read first, then the Book's visible-version lookup - and every other selector through `_resolve_spell` as
  before; the doors that build keep `_resolve_spell` unchanged.

## Before/After Behavior Summary
- Before: `purge(spell_id=<parked>)`, `has_live_creation(spell=<parked>)` and
  `describe_live_creation_status(spell=<parked>)` raise KeyError; an agent notches back to check or retire an old
  version's objects. A `unique` version with no owner store makes purge raise AttributeError.
- After: they answer for that version - its own entries in the store its existence and stamp select, its own pool
  for a managed version, its own object for an existing-object version - and a `unique` version with no owner
  store is refused with a RuntimeError naming it. Every meld door and every non-spell_id selector is unchanged.

## Interface Deltas
- Inputs: unchanged.
- Outputs: purge returns the parked version's retired count; the probes return its status payload.
- New internal methods: `Meld._resolve_visible_version_by_id(spell_id) -> Spell` and
  `Meld._resolve_probe_target(*, spell, spell_name, spellframe, binding_name) -> Spell`.
- Error semantics: KeyError "[MELD] No spell found with spell_id: <id>" unchanged for an id no visible version
  carries (the active read's own KeyError is re-raised); the R6 RuntimeError from `_get_purge_creations`.

## State and Lifecycle Deltas
- Owned state changes: none. No cache, no new map, no new lock.
- Lifecycle/cleanup changes: none. The helpers run under `check_cleaned` of the Meld (through
  `_resolve_purge_spell`) and of the Book (in the lookup).

## Failure Mode Deltas
- Removed failure mode: KeyError for a parked version's or a parked borrowed copy's spell_id in purge and the probes.
- Changed failure mode: purge of a `unique` version with no owner store raises RuntimeError (was AttributeError
  "'NoneType' object has no attribute 'owner_conduit_id'").
- New failure mode: none. A miss now takes the Book lock alone (code_description_patch).

## Dependency and Ordering Constraints
1. Needs `Spellbook._find_visible_version` (component_patch_spellbook_core).
2. `_resolve_purge_spell` keeps its order: the cleaned check, the `purge_all` checks, the instance-to-class step,
   then discovery.

## Validation Expectations
- Test/validation item 1: the component file's F1-F14, F17 and F19-F22 tests.
- Test/validation item 2: the integration file's F15 race, from the lender and from an index-link borrower.
- Evidence target 1: tests/component/melder/aether/conduit/test_conduit_component_probe_and_purge_reach_every_version.py
- Evidence target 2: tests/integration/melder/conduit/test_conduit_integration_probe_and_purge_during_notches.py

## Unknowns and Open Decisions
- UNKNOWN: whether a unit stub reaches the miss path (architecture_patch).
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: the miss path's Book lock under user code holding a spell lock (code_description_patch).
- Next entrypoint: `Meld._resolve_purge_spell`.
