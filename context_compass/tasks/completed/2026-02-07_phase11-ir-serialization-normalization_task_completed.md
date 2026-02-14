Completed: 2026-02-08
Summary: Delivered Normalize Phase11 IR to Schema-Only Serializable Payloads scope, updated validation notes, and confirmed acceptance.

# Task: Normalize Phase11 IR to Schema-Only Serializable Payloads

## Metadata
- Task ID: TASK-2026-02-07-phase11-ir-serialization-normalization
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Replace live-object Phase11 payload segments with schema-only serializable data
that fully drives no-overrides/override codegen without plan object coupling.

## Scope Boundaries
- In scope:
- Export normalized step rows and transient-plan arrays without callables.
- Remove `ExecutionPlanStep`/call-target object leakage from IR payloads.
- Update no-overrides compiler to consume normalized schema.
- Ensure signature coverage includes all normalized Phase11 semantics.
- Out of scope:
- Runtime behavior changes unrelated to payload boundary conversion.

## Steps / Checklist
- [x] Define normalized step/transient schema from audit output.
- [x] Implement schema export in Phase11 payload builder.
- [x] Update compilers to consume schema-only payloads.
- [x] Add fail-fast validation for missing/invalid required schema fields.
- [x] Add regression tests for serialization and compile parity.
- [x] Retire legacy object payload fields (`steps`, `transient_plan`) after cutover.

## Deliverables
- Schema-only Phase11 payload export.
- Compiler consumers updated to schema contract.
- Regression tests for schema validation and parity.
- Proposed normalized schema contract:
  - `execution.<variant>.steps_rows`: tuple of dict rows containing only primitives/tuples
    - `instance_key`, `spell_id`, `existence`, `creations_target_kind`, `shared_instance`
    - `dependency_resolution_order` (tuple of `(param_name, dependency_instance_keys)` tuples)
    - `override_match_prefix`, `override_match_prefix_len`, `override_keys`
    - `use_spell_lock_hint`, `must_register`, `uses_positional_override`
    - `contract_positional_override`, `has_contract_payload`, `contract_payload_items`
  - `execution.<variant>.transient_schema`: dict of primitive arrays
    - `step_count`, `root_step_index`, `call_modes`, `dep1..dep8` index arrays
    - no callable/object targets in payload
  - `execution.<variant>.required_schema_version`: explicit schema version marker

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 166 passed.

## Risks / Rollback Notes
- Risk: schema conversion misses semantics currently implicit in live objects.
- Mitigation: field-by-field consumer matrix and parity tests before cutover.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implementation follow-on to remove object leakage at the IR boundary and make
Phase11 payloads portable, deterministic, and full-codegen ready.
Audit output confirms object leakage in current `steps` and `transient_plan`
fields. Follow-on implementation is split into additional tickets so export,
no-overrides consumer, and overrides consumer migrations can land incrementally.
`steps_rows` + `steps_rows_signature` export is now landed and no-overrides/
overrides schema consumer migrations are in place. Final retirement landed:
Phase11 IR no longer emits `steps` or `transient_plan`, no-overrides transient
codegen now consumes schema-only `transient_schema`, and compile wiring enforces
schema-only step rows.

