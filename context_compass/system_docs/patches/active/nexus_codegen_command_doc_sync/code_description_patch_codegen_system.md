# Code Description Patch: CodegenSystem

## Trigger Justification
Required because `CodegenSystem` owns a non-trivial validate/execute pipeline
with shared transaction contexts, best-effort projection resolution, validation
short-circuiting, namespace construction, compile/exec staging, and monitor
callbacks.

## Control-Flow Description
1. validate or execute request enters `CodegenSystem`
2. build a `CodegenTransactionContext`
   - validate non-empty code/frame name
   - try to resolve a `CodegenProjection`
   - derive default namespace configuration from projection policy when present
3. validation path:
   - monitor validation start
   - run validator
   - monitor validation finish
   - return context + validation result
4. execution path:
   - monitor execution start
   - run validation first
   - if validation rejects, synthesize validation-failed execution result and
     finish execution without compile/exec
   - otherwise build namespace, attach it to context, compile code, execute
     compiled code, and finish execution monitoring
5. public reporting stays on the validation reporter surface

## Edge/Error Behavior and Rollback Semantics
- empty code or frame name MUST fail fast with `ValueError`
- missing `_get_required_codegen_projection(...)` support on the attached Rift
  MUST degrade to `None` projection instead of failing transaction setup
- rejected validation MUST prevent compile/exec and return a validation-failed
  execution result
- cleanup MUST null owned collaborators and cleanup the owned monitor

## Invariants and Idempotency Expectations
- one `CodegenSystem` is owned by one room
- validate/execute calls share the same transaction-context shape
- namespace construction occurs only after successful validation in the
  execution path
- cleanup is idempotent and lock-disciplined

## Explicit Non-Goals
- redefining validator policy rules
- changing the public room-facing method surface
- moving room-memory emission into the engine root

## Validation Focus Points
- docs describe validation-before-execution ordering
- docs describe the projection -> namespace-configuration -> namespace flow
- graph/docs preserve monitor ownership under `CodegenSystem`
