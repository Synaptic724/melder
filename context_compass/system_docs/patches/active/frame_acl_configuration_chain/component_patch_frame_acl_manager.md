# component_patch_frame_acl_manager

## Component purpose and boundary in current architecture
`FrameACLManager` should façade the chain mechanics per frame target.

## Before/after behavior summary
- Before:
  Manager only exposed container/builder access.
- After:
  Manager also exposes current/head/list/selection/rollback mechanics over the
  frame chain.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  frame names and configuration ids
- Outputs:
  chain-derived configuration views and state changes
- Error semantics:
  missing frames/configs fail fast

## Validation expectations
- manager can target a frame and access its chain mechanics
