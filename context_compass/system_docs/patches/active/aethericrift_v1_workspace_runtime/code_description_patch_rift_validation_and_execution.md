# code_description_patch_rift_validation_and_execution

## Trigger justification (why this file is required)
The current AR v1 design has a non-trivial control-flow split:
- code comes in as strings
- validation/classification happens first
- `StaticRiftSpace` and `DynamicRiftSpace` diverge at local construction access
- local workspace construction must remain distinct from canonical mutation

That is implementation-guiding enough to warrant a code-description patch.

## Control-flow description (pseudocode level, not production code)
1. Operator submits code string to the room.
2. `RiftValidationSystem` parses AST.
3. Validate syntax.
4. Validate names/member paths against `RiftAttribute` / `RiftMethod`
   registries.
5. Classify request intent.
6. If request is invalid, reject before execution.
7. If request is valid:
   - run in the workspace context
   - use the backing root conduit that was created through the normal Melder
     Spellbook/conjure lifecycle
   - if in `StaticRiftSpace`, do not permit conduit-backed local construction
   - if in `DynamicRiftSpace`, permit conduit-backed local construction
8. If execution yields local helper objects or methods:
   - bind them into the workspace only when the room/configuration allows it
9. If work crosses canonical mutation boundary:
   - stop treating it as ordinary local room work and route into the MR path

## Edge/error behavior and rollback semantics
- Invalid syntax fails fast.
- Invalid room target or member path fails fast.
- Disallowed static-room construction fails before or during execution based
  on the validated mode/operation path.
- Failed local construction remains local and should be cleaned/discarded in the
  room.
- Canonical mutation is not silently inferred from ordinary local helper work.

## Invariants and idempotency expectations
- The declared room target model is the only normal target universe.
- `StaticRiftSpace` does not expose local conduit-backed construction.
- `DynamicRiftSpace` may expose it.
- Local room construction does not automatically imply canonical mutation.
- Validation runs before execution every time unless a future caching layer
  explicitly preserves equivalence.

## Explicit non-goals
- This file does not define transport/API protocol.
- This file does not define full external sentinel behavior.
- This file does not define MutationResearch internals.

## Validation focus points
- Validate the room target model is the execution universe.
- Validate the `StaticRiftSpace` versus `DynamicRiftSpace` split is implemented honestly.
- Validate local helper creation and registration stay in-room unless promoted.
