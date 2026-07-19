# Code Description Patch: Codegen Namespace Flow

## Control Flow
1. `CodegenSystem._build_transaction_context(...)`
   - creates transaction context
   - derives namespace configuration
2. `CodegenSystem._build_namespace(...)`
   - asks `CodegenNamespaceBuilder` to build one live namespace from the
     configuration and room/runtime state
3. `CodegenNamespaceBuilder`
   - runs room-objects strategy
   - runs workstation strategy
   - runs command strategy
   - runs target strategy
   - merges those globals into one `CodegenNamespace`
4. `CodegenSystem.execute_codegen(...)`
   - stores the built namespace on the transaction context
   - later execution work will consume that object

## Edge / Error Semantics
- Missing active target does not fail namespace assembly.
- `target` becomes `None` when no target is selected.
- Builder requires non-None `CodegenNamespaceConfiguration`.

## Idempotency / Lifecycle
- Builder strategies are owned by the builder.
- `CodegenSystem.cleanup()` drops the owned builder reference with the rest of
  the root engine state.

## Non-Goals
- No direct locals for all workstation bindings.
- No builtins strategy yet.

