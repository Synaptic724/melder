# Phase 9 InjectionPlan Schema (Draft, 2026-01-27)

## Scope
Define the InjectionPlan artifact that replaces per-call kwargs construction
in `MeldEngine._build_kwargs_for_instance` with a precompiled wiring plan.

## Evidence References
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_injection_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_override_map`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_get_contract_override_payload_for_instance`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:execute`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_injection_plan`

## InjectionPlan (Draft Schema)
This is a plan for how to build kwargs for each instance key. The runtime still
supplies instance results and optional override payloads.

```
InjectionPlan:
  root_spell_id: str
  instance_injections: Dict[_InstanceKey, InjectionSpec]

InjectionSpec:
  param_sources: Dict[str, ParamSource]
  allow_list_aggregation: bool
  uses_positional_override: bool

ParamSource:
  kind: "dependency" | "override" | "contract"
  dependency_keys: List[_InstanceKey] | None
  override_key: str | None
  contract_key: str | None
```

## Field Notes (Evidence Mapping)
- `instance_injections` corresponds to the loop in `_build_kwargs_for_instance`
  over dependencies and override maps.
- `dependency_keys` correspond to occurrences for a param and their instance keys.
- `override_key` corresponds to the override map param name.
- `contract_key` corresponds to contract payload keys used in `_build_kwargs_for_instance`.

## Inputs Required To Compile InjectionPlan
Observed inputs used by current runtime:
- Occurrence graph + instance plan (Phase 8 outputs).
- Spell metadata / parameter names (requirements or resolution frame).
- Socket refs and contract defaults to identify contract payload keys.

## Runtime Inputs Still Required
Even with InjectionPlan, runtime must provide:
- Instance results map for dependency values.
- Override map (if overrides are enabled).
- Contract override payloads (if contracts supply overrides).
- A valid OccurrencePlan (Phase 8) so instance keys stay in sync with wiring.

## Storage Location
- Root SpellCrafter (`_injection_plan_phase9`), built after Phase 8 and cleaned
  alongside Phase 8 artifacts.

## Invalidation / Signature Inputs (Draft)
Candidate invalidation inputs:
- OccurrencePlan changes (Phase 8).
- Resolution frame or requirements changes (Phase 1-3).
- Contract socket changes or spellframe wiring.
- Mutation overrides: plan reuse is gated off when mutation overrides are present.

## Open Questions
- How to represent multi-value dependency aggregation (list vs single).
- Whether override and contract payload handling should remain Phase 9 or be deferred to Phase 10.
