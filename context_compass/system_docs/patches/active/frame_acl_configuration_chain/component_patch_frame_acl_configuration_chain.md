# component_patch_frame_acl_configuration_chain

## Component purpose and boundary in current architecture
`FrameACLConfigurationChain` owns the config-node history for one frame ACL
container.

## Before/after behavior summary
- Before:
  Container held one current config plus a loose history list.
- After:
  Container owns one explicit chain object that owns all config nodes.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  locked configuration nodes
- Outputs:
  head/current/list/get/rollback semantics
- Error semantics:
  invalid config ids should fail fast

## State and lifecycle deltas
- chain owns:
  - head id
  - current id
  - config nodes by id
  - history limit

## Validation expectations
- new configs insert at the head
- tail trimming is bounded and deterministic
- list order is newest-first
