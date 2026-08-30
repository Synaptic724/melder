# component_patch_conduit

## Component purpose and boundary in current architecture
`Conduit` remains the owner of root/lesser lineage, peer links, and contract
topology. In this patch it becomes a private producer of canonical Nexus
conduit updates only for the conduit states worth surfacing directly.

## Before/after behavior summary
- Before:
  `Conduit` owned its lifecycle and link topology locally, but Nexus had no
  canonical conduit record surface.
- After:
  root conduits publish canonical `ConduitRecord`s into Nexus, and later
  link/sever/cleanup operations update those records. Lesser conduits remain
  derived by lineage walking unless later promoted to normal.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  root conjure, link, sever, cleanup, and later lesser->normal promotion
- Outputs:
  private calls into Nexus conduit publication/update/remove methods
- Error semantics:
  if the frame is not publishable, conduit publication returns early

## State and lifecycle deltas
- Root conduits may cache `_nexus_publish_enabled`
- Ordinary lesser conduits are not published in the first slice
- Root link/sever updates should rewrite peer ids in the canonical record
- Root cleanup removes the canonical conduit record

## Failure mode deltas
- Publishing every lesser conduit would create unnecessary churn and store
  overhead.
- Duplicating frame posture fields on the conduit record would blur source of
  truth between frame posture and conduit topology.

## Dependency and ordering constraints
- Root conduit publication depends on successful Spellbook conjure
- Link/sever publication should only happen after the underlying ConduitWard
  operation succeeds
- Cleanup removal must happen on the root/normal publication surface only

## Validation expectations
- Root conduit publication works on conjure
- link/sever rewrites peer ids deterministically
- cleanup removes the canonical root conduit record

## Unknowns and open decisions
- Exact lesser->normal promotion publish semantics if that path becomes active
  in this slice
