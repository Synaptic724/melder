# component_patch_conduit_ward

## Component purpose and boundary in current architecture
`ConduitWard` is the authoritative relationship manager for conduit peer
contracts and lesser-conduit lineage.

## Before/after behavior summary
- Before:
  `_link(...)` enforced lesser/self/dynamic/policy checks but did not
  explicitly reject target conduits from a different frame.
- After:
  `_link(...)` also enforces same-frame equality using the existing
  `_aetheric_frame` stored on each conduit.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  source conduit ward + target conduit
- Outputs:
  successful peer contract creation only when both conduits belong to the same
  frame
- Error semantics:
  linking across different frame names raises a runtime error with an explicit
  frame-mismatch message

## State and lifecycle deltas
- No new owned state.
- Uses existing conduit-local `_aetheric_frame` metadata.

## Failure mode deltas
- Cross-frame peer link attempts now fail fast at `_link(...)`.

## Dependency and ordering constraints
- Guard belongs in `_link(...)`, before `_create_new_contract(...)`.
- No `Aether` lookup is required for the basic equality check.

## Validation expectations
- `_link(...)` must reject different frame names.
- Existing same-frame link tests must continue to behave normally.
- `sever_link(...)` remains unchanged.

## Unknowns and open decisions
- Whether future architecture should ever allow deliberate cross-frame peer
  contracts.
