# Dialog Resolutions - Fast Path Meld Plan

## Scope
Captures decisions and notes from dialog about a fast-path meld plan. This file
records design inputs and code observations; not all items are verified.

## User Directions (Design Inputs)
- Store compiled phase plans on SpellCrafter and on the Spell.
  Status: design input. UNKNOWN: implementation and lifecycle details.
- Meld fast path should execute a simple structure using Creations and only
  pay the dynamic costs (overrides, mutation, validity gates) when needed.

## Code Observations (Evidence)
- MeldEngine rebuilds occurrence graph, execution order, and instance plan on
  every call when a blueprint exists.
  EVIDENCE: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:212
  EVIDENCE: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:496
  EVIDENCE: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:594
  EVIDENCE: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:1363
- MeldRuntime builds a per-call ResolutionFrame and applies GraphMutator +
  SpellOverrider when a root blueprint exists.
  EVIDENCE: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:59
  EVIDENCE: src/melder/aether/conduit/meld/overrides/graph_mutator.py:53
  EVIDENCE: src/melder/aether/conduit/meld/overrides/spell_overrider.py:52
- Phase 5 generates RootResolutionBlueprint with ordered_node_ids and socket refs.
  EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:39
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py:136
- SpellCrafter reset/cleanup releases Phase 1-4 and Phase 6 artifacts but keeps
  Phase 5 artifacts intact.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:382

## Open Questions
- Where should compiled plans live so they survive phase cleanup and remain
  accessible to meld runtime?
  Investigate: src/melder/spellbook/spellbook.py:3364
  Investigate: src/melder/spellbook/spell_crafter/spell_crafter.py:382
- What invalidation signature is required to avoid stale plans when wiring or
  validity changes?
  Investigate: src/melder/aether/conduit/meld/meld.py:364
  Investigate: src/melder/aether/conduit/meld/meld.py:482
- SpellContract sockets: is the fast path eligible when contracts are present,
  or should it always fall back?
  Investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Benchmark Note (User-Provided, Unverified)
- User supplied benchmark tables comparing Melder vs other DI libraries on
  2026-01-26 and cited test files test_deep_other_di.py and
  test_conduit_integration_perf_deep_graphs.py. UNKNOWN: verify outputs and
  file locations in repo.

## Evidence Index
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/overrides/graph_mutator.py
- src/melder/aether/conduit/meld/overrides/spell_overrider.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spellbook.py
