# component_patch_nexus

## Component purpose and boundary in current architecture
`Nexus` remains the singleton root for Rift-domain behavior, but this patch
extends it with a second responsibility: passive canonical record hosting for
frame/conduit/spell data before interactive enablement.

## Before/after behavior summary
- Before:
  `Nexus` only owned interactive/configured/enabled Rift-facing behavior.
  There was no canonical frame/conduit/spell store for the viewer layer.
- After:
  `Nexus` also owns a canonical living-record store plus private publication
  methods. Interactive enablement still gates Rift/public interaction, but not
  record hosting.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  private record publication calls from internal runtime producers
- Outputs:
  updated canonical records and indexes inside Nexus
- Error semantics:
  non-publishable frames short-circuit quietly/cheaply; malformed record/update
  input should fail fast inside Nexus private methods

## State and lifecycle deltas
- New Nexus-owned canonical store:
  - frame records
  - conduit records
  - spell records
  - supporting indexes
- New fast frame posture lookup for publishability
- Existing `_enabled` continues to mean interactive-enabled only

## Failure mode deltas
- Conflating passive ingest with `_require_enabled()` would reintroduce the
  original chicken-and-egg problem.
- Letting producers mutate Nexus store internals directly would split canonical
  ownership and make debugging harder.

## Dependency and ordering constraints
- Depends on bound `AethericFrameConfiguration` being present for the frame
- `FrameRecord` publication should happen before conduit/spell publication for
  a newly conjured frame
- Private publish methods must remain internal-only

## Validation expectations
- Nexus can accept canonical updates before interactive enablement
- Publishability is derived from frame posture, not from `_enabled`
- Store/index ownership stays inside Nexus

## Unknowns and open decisions
- Whether the first store shape should live in a helper object
  (`NexusCanonicalStore`) or as private fields on `Nexus`
