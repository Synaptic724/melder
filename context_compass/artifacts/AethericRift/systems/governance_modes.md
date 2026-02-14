# Governance and AI Usage Modes (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Capture the recurring "AI usage modes" framing used to shape domains, ACL tiers,
and safe defaults for what AI is allowed to do.

## Proposed Modes (PROPOSED)

### Observation
- Intended for prod-like domains.
- Primarily VIEW-tier actions:
  - describe/list
  - read-only attr access
  - safe status/health methods

### Intervention (Incident Response)
- Intended for ops/control domains.
- VIEW + bounded STATE-tier:
  - restart pools
  - tweak safe knobs
  - open incidents
- No GRAPH/topology mutations in prod by default.

### Reconstruction (Lab Repro)
- Intended for lab domains.
- VIEW/STATE/GRAPH allowed (lab only):
  - clone or rebuild blueprints in lab
  - replay traces
  - aggressive introspection

### Mutation (Graph Changes Under Control)
- Intended for mutation lab domains.
- GRAPH-tier actions:
  - propose/apply graph changes under explicit control
  - validate by rerunning repro workloads
  - open change requests with evidence

## Enforcement Mechanisms (UNKNOWN)
Open question: where do these modes live?
- In ACL tiers (VIEW/STATE/GRAPH)?
- In domain wiring (which spells/surfaces are attached)?
- In CommandOps governance and policy enforcement?
- In audit/incident systems (monitor and gate dangerous ops)?

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

