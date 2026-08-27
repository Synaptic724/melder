# Static Frame Viewer Live Spell Filtering Architecture Patch

## Objective
Finish static room semantics on the viewer side by filtering spell-facing
viewer surfaces to already-live spells only.

## Non-Goals
- No conduit visibility redesign.
- No capability work.
- No descriptor publication redesign.

## Changed Components
- `FrameViewer`
- `StaticFrameViewer`
- `StaticRiftSpace`

## Boundary Contract
- Descriptor publication remains structural truth.
- `StaticFrameViewer` adds a live-only spell overlay on top of that truth.
- `StaticRiftSpace` composes the static viewer variant.
- Static command continues to own live-only runtime spell retrieval.

## Interface Deltas
- Add a static viewer variant.
- Static rooms attach the static viewer variant instead of the generic viewer.

## Invariants
- Frame and conduit visibility remain structural.
- Spell visibility in static becomes live-only.
- Static viewer never creates spell runtime objects.

## Migration Order
1. Add `StaticFrameViewer`.
2. Compose it from `StaticRiftSpace`.
3. Update focused tests.

## Rollback
If the overlay proves too broad, remove `StaticFrameViewer` composition and
keep the static command seam as the last stable static boundary.
