# RiftLesserConduit (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Some drafts define "RiftLesserConduit" as a scoped sub-universe under a domain,
used to create finer-grained lifetime boundaries (per experiment, per mission,
per workflow) without polluting the primary conduit lifetime.

This may map directly to Melder's lesser conduit concept, or be a wrapper.

## Responsibilities (PROPOSED)
- Provide isolated scopes/lifetimes for a smaller working set.
- Allow cleanup/teardown of a workflow without destroying the domain's entire
  universe.

## Relationship to RiftConduit / Conduit (PROPOSED)
- Lesser conduits are created from a parent conduit and inherit configuration.
- Strong references live inside the lesser conduit for objects created there.
- The parent domain routes to either the primary conduit or a lesser conduit
  depending on scope selection rules.

## Open Questions (UNKNOWN)
- Do we need an explicit RiftLesserConduit type, or reuse Conduit.create_lesser_conduit?
- What is the caller-facing handle for selecting a lesser conduit/scope?
- How do ACL tiers apply to lesser conduits (lab vs prod isolation)?

## Sources
- `context_compass/artifacts/aethericriftticket85.md`

