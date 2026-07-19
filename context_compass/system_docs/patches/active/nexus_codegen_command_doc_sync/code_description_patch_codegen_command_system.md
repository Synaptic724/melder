# Code Description Patch: CodegenCommandSystem

## Trigger Justification
Required because `CodegenCommandSystem` wraps the internal engine with
room-facing hooks, RiftGate ticket lifecycle, action-hook scopes, and
codegen-specific room-memory emission.

## Control-Flow Description
1. public `validate_codegen(...)` / `execute_codegen(...)` enters the command
   facade
2. validate inputs (`code`, `frame_name`)
3. enter the room action-hook scope for `codegen`
4. begin one command action and acquire the RiftGate ticket
5. under the command lock:
   - require the attached `CodegenSystem`
   - delegate into `validate_codegen_request(...)` or
     `execute_codegen_request(...)`
   - shape the returned public payload
6. finally:
   - unregister the RiftGate ticket if one was created
   - emit codegen memory when a result object exists and room memory is enabled

## Edge/Error Behavior and Rollback Semantics
- missing attached engine MUST raise `RuntimeError`
- input validation happens before delegation
- memory emission MUST be skipped when room memory is missing/disabled
- memory emission MUST fail fast if neither validation nor execution result is
  supplied to the helper

## Invariants and Idempotency Expectations
- room-facing validate/execute always delegate to the attached engine; they do
  not perform direct validation or execution work themselves
- command facade owns the public memory shape for codegen actions
- top-level command tickets are unregistered even on failure paths

## Explicit Non-Goals
- changing the selected runtime-helper subset
- moving generic shared command behavior out of `CommandSystem`
- reworking room memory infrastructure

## Validation Focus Points
- docs describe engine attachment as a required boundary
- call-flow sections mention action hook scope, RiftGate ticket lifecycle, and
  post-action memory emission
- graph/docs preserve the separation between command facade and engine root
