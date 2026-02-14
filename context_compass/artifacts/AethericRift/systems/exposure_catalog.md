# Exposure Catalog (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Provide a conduit-agnostic view of what capabilities are eligible for exposure
through Rift, so discovery/listing does not depend on a single execution surface.

## Proposed Model (PROPOSED)
- Catalog
  - Holds stable spell identity keys eligible for exposure (often lineage-anchored).
  - Holds exposure metadata (names, categories, tags, doc summaries).
  - Does not hold instances.
- Surfaces
  - Rift binds one or more surfaces (each backed by a conduit or surrogate).
  - The same catalog entry can be executed through different surfaces.
- Execution
  - Execution always happens through a chosen surface + scope context.

## Surrogate Conduits (PROPOSED)
Recommended surface form in some tickets:
- A surrogate conduit is a "front-stage" conduit that provides curated behavior
  and visibility rules.
- It exists to avoid exposing raw internal conduits directly.

## Key Invariants (PROPOSED)
- Discovery is stable even when the system evolves; identity is anchored to
  stable spell identity (often lineage).
- Rift never bypasses conduit reality; catalog is not an execution engine.

## Open Questions (UNKNOWN)
- Catalog identity rules: what is the canonical key (lineage id, spell_key,
  spell_name+frame, etc.)?
- How do we represent "surface identity" across multiple conduits so exposure
  stays comprehensible?
- Are surrogate conduits required for some environments (prod), or optional?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket111.md`

