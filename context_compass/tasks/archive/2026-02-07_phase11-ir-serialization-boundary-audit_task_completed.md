Completed: 2026-02-08
Summary: Delivered Audit Phase11 IR Serialization Boundary and Object Leakage scope, updated validation notes, and confirmed acceptance.

# Task: Audit Phase11 IR Serialization Boundary and Object Leakage

## Metadata
- Task ID: TASK-2026-02-07-phase11-ir-serialization-boundary-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Audit Phase11 export and compiler inputs to identify where IR still carries live
objects/callables instead of schema-only data.

## Scope Boundaries
- In scope:
- Audit `phase8_11.execution.*` payload field types and serializability.
- Audit no-overrides compiler consumption of `steps`/`transient_plan`.
- Inventory override compiler/runtime dependencies on live `ExecutionPlan`.
- Define schema-only boundary rules and migration requirements.
- Out of scope:
- Implementing serializer/compiler changes.

## Steps / Checklist
- [x] Build field-type matrix for Phase11 variant payloads.
- [x] Mark non-serializable fields (objects, callables, mutable refs).
- [x] Map each non-serializable field to consumer usage sites.
- [x] Produce migration spec to schema-only payloads with signatures.

## Deliverables
- Evidence matrix: field -> runtime type -> consumer -> risk.
- Schema-only Phase11 boundary spec and migration checklist.
- Evidence matrix:
  - `phase8_11.execution.<variant>.plan_variant` -> `Optional[str]` -> metadata/signature only -> serializable, low risk.
  - `phase8_11.execution.<variant>.root_spell_id` -> `Optional[str]` -> no-overrides compile root resolution -> serializable, low risk.
  - `phase8_11.execution.<variant>.step_count` -> `int` -> compile precondition checks -> serializable, low risk.
  - `phase8_11.execution.<variant>.step_spell_ids` -> `Tuple[str, ...]` -> signature/fingerprint only -> serializable, low risk.
  - `phase8_11.execution.<variant>.transient_signature` -> `Optional[str]` -> compile cache invalidation only -> serializable, low risk.
  - `phase8_11.execution.<variant>.signature` -> `Optional[str]` -> compile cache invalidation only -> serializable, low risk.
  - `phase8_11.execution.<variant>.transient_plan` -> `Optional[Tuple[..., List[Any], ...]]` -> `compile_phase12_no_overrides_executor` unrolled source path -> non-serializable due callable/object targets (`transient_plan[2]`), high risk.
  - `phase8_11.execution.<variant>.steps` -> `Tuple[ExecutionPlanStep, ...]` -> `compile_phase12_no_overrides_executor` step-plan + transient error paths -> non-serializable live object graph, high risk.
- Consumer map:
  - No-overrides compiler consumes live `steps` and `transient_plan` directly (`src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`).
  - Overrides compiler/runtime bypasses IR and consumes live plan objects (`src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`, `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`).
- Migration checklist:
  - Export schema-only step rows and transient arrays (no callables/object refs) in Phase11 payload builder.
  - Add compiler adapters that resolve spell runtime objects from spell_id lookup, not from IR payload objects.
  - Keep legacy `steps`/`transient_plan` fields during cutover behind explicit precedence, then remove.
  - Add parity tests asserting schema path emits identical no-overrides behavior/signatures.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/`

## Validation
- Static source audit only; no runtime tests required for evidence capture.

## Risks / Rollback Notes
- Risk: live object coupling blocks true full-AOT and deterministic artifacts.
- Mitigation: enforce schema-only IR boundary and explicit compiler adapters.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added after pass found `phase8_11.execution.no_overrides` still exports live
`ExecutionPlanStep` objects and transient call targets, and compilers consume
those objects directly. Audit confirms the boundary is still object-coupled in
both no-overrides and overrides codegen paths and defines a schema-only
migration sequence.

