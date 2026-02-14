# Phase 9 Injection Plan Investigation (2026-01-27)

## Scope
Map how the runtime builds kwargs for each instance today so Phase 9 can
precompile injection wiring and minimize per-call work.

## Evidence Anchors
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_injection_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_override_map`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_get_contract_override_payload_for_instance`
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:execute`

## Current Runtime Injection Steps
From `_build_kwargs_for_instance`:
1) Resolve occurrence for instance key (shared vs per-path).
2) Build override map for instance (`_build_instance_override_map`):
   - Shared instances: apply overrides without path match.
   - Per-path: param_path must match occurrence path.
3) Load contract override payload for this instance (if any).
   - May include `__args__` positional override.
4) Walk dependencies from `occurrence_graph` for the occurrence:
   - Gather dependency instance results.
   - If one dependency, pass single value; else pass list.
5) Apply positional overrides (`__args__`) if present.
6) Apply contract payload key/values (excluding overridden params).
7) Apply override values for params not already set.

From `_build_kwargs_for_instance_from_plan` (Phase 9 path):
1) Resolve occurrence for instance key (shared vs per-path).
2) Build override map for instance (`_build_instance_override_map`).
3) Load contract override payload for this instance (if any).
4) Walk dependency keys from InjectionPlan and fetch instance results.
5) Apply positional overrides (`__args__`) if present.
6) Apply contract payload key/values (excluding overridden params).
7) Apply override values for params not already set.

## Inputs Required
Phase 9 needs the following inputs (from current runtime behavior):
- Occurrence graph (Phase 8 output).
- Instance plan / canonical occurrences (Phase 8 output).
- InjectionPlan instance injection mapping (Phase 9 output).
- Instance results map (runtime values from constructed dependencies).
- Override map (SocketRef -> value) from SpellOverrider.
- Contract override payloads from SpellContract resolution.

## Outputs Required
Phase 9 should emit a plan that allows:
- Fast wiring of kwargs per instance key.
- Deterministic override precedence (override map > contract payload > deps).
- Optional positional override handling.
- Safe gating so injection plans only apply when the occurrence plan is reused.

## Notes
Override behavior is still dynamic when overrides are supplied. For the
iteration that is override-free, Phase 9 can ignore override maps and
contract payloads, reducing the plan to pure dependency wiring.

The runtime currently gates both Phase 8 and Phase 9 reuse when mutation
overrides are present, and Phase 9 is only selected when a Phase 8 plan
is accepted to prevent stale wiring.

## UNKNOWNs
- How much of override routing can be precompiled without a runtime override map.
- Whether contract override payloads should be Phase 9 or Phase 10 artifacts.
