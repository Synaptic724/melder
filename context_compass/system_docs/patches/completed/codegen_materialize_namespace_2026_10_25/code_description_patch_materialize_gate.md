# Code-description patch: the materialize name gate

## Metadata
- Patch ID: codegen_materialize_namespace_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T11:34:22Z
- Updated: 2026-10-25T11:34:22Z
- Ticket: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20), parent
  EPIC-2026-10-25-codegen_room_policy_defects

## Trigger justification
- A policy-gate pipeline changes: materialize gains a name gate between validation and publication.

## Control flow
1. Argument checks (unchanged ValueErrors).
2. `validate_codegen_request`; a rejection returns as before.
3. `_refuse_materialize_name(name, context)` returns the first reason: already in `sys.modules`; under `melder`;
   stdlib root; installed root; under a denied generation root; generation roots declared and none covers it.
   The surface is `context.projection.compiled_access_surface`, absent for the no-projection default (no rule).
4. `build_materialize_builtins(context)` merged as `__builtins__` before `materialize`.
5. Parent names absent from `sys.modules` and the registry are noted; `materialize`; on exception the module is
   cleaned, then each noted shell deepest first, and the exception propagates.

## Edge and error semantics
- Refusal messages name the module name and the reason; installed names are read per call.

## Invariants and idempotency
- No registry, `sys.modules` or parent mutation happens before step 5.

## Explicit non-goals
- Re-materializing a live name (cleanup first, or a new name).
