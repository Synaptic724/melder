# component_patch_rift_space

## Component purpose and boundary in current architecture
`RiftSpace` is the base room contract. `StaticRiftSpace` and
`DynamicRiftSpace` are the operator-facing concrete room surfaces. Together
they own the target registries, workspace-local metadata, cleanup semantics,
and the operational surface the agent uses.

## Before/after behavior summary
- Before:
  Workspace semantics were mixed with older domain/workstation/context ideas.
- After:
  `RiftSpace` is the base room contract and `StaticRiftSpace` /
  `DynamicRiftSpace` are the clear room surfaces over the local root-conduit
  reality created by the normal Melder Spellbook/conjure path.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  imported targets, local targets, configuration, code blocks
- Outputs:
  visible target registries, execution results, cleanup effects
- Error semantics:
  invalid target access, missing names, or invalid room state should fail as
  workspace-level errors

## State and lifecycle deltas
- Holds `attributes` and `methods` registries
- Holds metadata for those targets
- Exposes conduits and other allowed objects from the configured frame into the
  room surface
- Cleanup clears local transient targets and local room state
- Does not own broader substrate lifetime truth
- Uses the backing root conduit owned by the Rift; it does not invent its own
  independent substrate lifecycle

## Failure mode deltas
- Ambient Python-state leakage makes the room lose its target semantics
- Failure to clear local transient targets causes room sludge

## Dependency and ordering constraints
- Depends on `AethericRift` core
- Depends on root conduit availability
- Must exist before meaningful codegen flow can be exercised

## Validation expectations
- Room surfaces must expose declared targets cleanly
- `StaticRiftSpace` and `DynamicRiftSpace` must diverge in room semantics
- Cleanup behavior must preserve the local-vs-imported distinction

## Unknowns and open decisions
- Exact occupancy/session model still leaves room for future refinement
