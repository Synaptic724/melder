# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: spellspace_probe_many_2026_09_28
- Component: Meld Resolution Runtime (`SpellSpaceMeld` live-creation probe)
- Status: promoted
- Owner: user (agent melder_0)
- Created: 2026-09-28T00:34:00Z
- Updated: 2026-09-28T01:00:17Z

## Component Purpose and Boundary
- Current boundary: `SpellSpaceMeld._describe_spell_live_creation_status` interprets a resolved spell against
  the stores the SpellSpace door fronts, without creating anything.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: the `many` branch read `self._conduit_creations`, so a disposal-bearing `many` melded through the
  space (held in the space store) probed as not live, while a `many` melded through the owner conduit probed
  as live through the space. It reported "owner_conduit_many" and `active_spellspace_id` None.
- After: the `many` branch reads `self._spellspace_creations`: the count is the space's bucket, the kind is
  "spellspace_many", `storage_owner_conduit_id` the owner conduit and `active_spellspace_id` this space - the
  store `SpellSpaceMeld.purge` retires `many` from and every emitter registers it into through this door.

## Interface Deltas
- Inputs: none.
- Outputs: the `many` payload through a SpellSpace door, as above; keys unchanged.
- Error semantics: none.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: "Known probe inaccuracy (2026-09-27)" in Creations and SpellSpace Failure Modes.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The owner-conduit `many` objects stay visible to `Conduit.has_live_creation` (the ConduitMeld reads its
   own store); only the space door's answer changes.
2. The probe is not on the meld path; no hot path changes.

## Validation Expectations
- Test/validation item: unit tests over a stub door (space bucket of 2 -> count 2 "spellspace_many"; an
  owner-conduit bucket -> 0 through the space door); one component test with a real conduit and space.
- Evidence target: artifacts/spellspace_probe_many_20260928/ logs.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: implemented as written (0.2.8204) and promoted into the Meld Resolution Runtime entry of
  src_components; the removed failure mode is gone from Creations and SpellSpace.
- Remaining risks: an out-of-tree caller reading the old space-door `many` answer (none in this repository).
- Next entrypoint: `src/melder/aether/conduit/meld/spellspace_meld.py`, the probe's `many` branch.
