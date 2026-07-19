# code_description_patch_frame_descriptor_manager

## Trigger justification (why this file is required)
This migration changes ownership and control flow for a whole frame-scoped
subsystem, not a single helper. We need an explicit control-flow contract so
the extraction does not leave partial dual ownership behind.

## Control-flow description (pseudocode level, not production code)
1. `Nexus` receives a frame-scoped request or publish event.
2. `Nexus` delegates the frame-scoped operation into
   `FrameDescriptorManager`.
3. The manager acquires its own `RLock`.
4. The manager resolves/creates the descriptor as needed.
5. The manager updates descriptor-owned frame/conduit/spell or Nexus-frame
   state.
6. `Nexus` continues with any remaining façade/root-level behavior.

## Edge/error behavior and rollback semantics
- Missing descriptor:
  create it inside the manager only.
- Partial migration ambiguity:
  fail the slice; do not leave dual ownership.
- Manager invariant break:
  fail fast inside the manager boundary.

## Invariants and idempotency expectations
- One descriptor dictionary owner: the manager.
- One frame-scoped state mutation owner: the manager.
- `Nexus` remains the semantic façade/root.
- Multi-step mutations are lock-guarded at the manager boundary.

## Explicit non-goals
- This file does not define final ACL schema.
- This file does not define final viewer contracts.
- This file does not define target-frame onboarding semantics beyond current
  internal behavior.

## Validation focus points
- validate delegation from `Nexus` into the manager
- validate manager lock coverage on multi-step mutations
- validate old direct descriptor-store paths are removed
