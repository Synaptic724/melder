# Research: Override + mutation patching

Date: 2026-01-25

## Scope
Document how overrides and mutation overlays are represented today so a
compiled plan can either patch or fall back correctly.

## Evidence
- src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator
- src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider
- src/melder/spellbook/spell_crafter/dag/target_spec.py:TargetSpec
- src/melder/spellbook/spell_crafter/dag/dag_index.py:DagIndex, DagTargetingEngine
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_detect_any_overrides
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_override_map
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_record_contract_override

## Findings
- SpellOverrider parses TargetSpec keys into socket-level override maps using
  DagTargetingEngine and specificity precedence (PATH > UNIQUE > BROADCAST).
- GraphMutator rewires MutationContract sockets by cloning the DAG and
  returning a new RootResolutionBlueprint.
- TargetSpec supports PATH (a>b>c), UNIQUE (*param), and BROADCAST (**param)
  targeting modes.
- DagIndex indexes SocketRef entries by exact path and param name and is used by
  DagTargetingEngine to resolve TargetSpec keys.
- MeldEngine records SpellContract overrides per occurrence and per spell id
  for later application when building kwargs.

## Unknowns
- UNKNOWN: How contract override payloads should map into a compiled plan
  (per-occurrence vs per-spell), especially for shared existences.
  - Why it matters: override correctness for shared instances depends on
    canonical occurrence selection.
  - Where to investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:
    _record_contract_override and _get_contract_override_payload_for_instance.
  - Status: uninvestigated.

- UNKNOWN: Whether override patching needs distinct handling for occurrence paths
  vs canonical shared occurrences in a compiled plan.
  - Why it matters: incorrect mapping could violate override semantics for
    Existence.many or shared existences.
  - Where to investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:
    _build_instance_override_map and _validate_shared_override_targets.
  - Status: uninvestigated.
