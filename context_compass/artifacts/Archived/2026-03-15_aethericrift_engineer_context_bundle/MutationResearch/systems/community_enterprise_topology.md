# Community and Enterprise Topology

## Purpose
Define where mutation research runs in community and enterprise deployments.

## Community Topology
- Single app instance.
- No CommandNet requirement.
- Mutation research runs in local scopes/missions only.
- Containment boundary is local scope disposal + lock release + incident emission.

Guiding phrase:
`one runtime, many scopes`

## Enterprise Topology
- Multiple zones/app instances.
- AgentNet local per zone.
- Optional CommandNet for cross-zone mission exchange.
- Research zones can run heavy mutation campaigns and return release plans.
- Primary zone remains promotion authority for production lineage.

Guiding phrase:
`many runtimes, coordinated worlds`

## Shared Rule
- Topology changes where mutation can run, not what mutation is.
- Control-plane gates remain consistent across both tiers.

