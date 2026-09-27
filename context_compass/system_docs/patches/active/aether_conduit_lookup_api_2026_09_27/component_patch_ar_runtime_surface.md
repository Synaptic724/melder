# Component patch: AR Runtime Surface (Nexus, Rift, RiftSpace) - static viewer owner lookup (2026-09-27)

## Before
- `StaticFrameViewer._get_owner_conduit` tried Aether's root lookup, then walked roots and wards itself through
  Aether's private frame fields.

## After
- It returns `Aether.get_conduit_by_id(conduit_id, frame_name)` (LIVE) and None on ValueError, as before for a
  missing frame or id.

## Interface / state / failure deltas
- None; the private frame reach-in is removed.

## Validation expectations
- Static viewer and frame-viewer suites green unchanged.
