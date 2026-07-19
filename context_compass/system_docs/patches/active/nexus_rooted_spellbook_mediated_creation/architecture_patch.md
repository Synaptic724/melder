# Patch Architecture: Nexus Rooted Spellbook-Mediated Creation

## Objective
Replace the current frame-first Nexus-managed creation path with a
Spellbook-mediated, root-conduit-first flow that returns the rooted conduit.

## Non-Goals
- Auto-provisioning Nexus frames in general.
- Reworking unrelated frame-link, viewer, or ACL semantics.
- Broad lower-runtime redesign outside what this change proves necessary.

## Boundary
- In scope:
  - Nexus/Rift-facing Nexus creation APIs
  - frame-manager creation order
  - root-conduit naming
  - conduit-returning result shape
  - focused tests/docs
- Out of scope:
  - unrelated AR/runtime surfaces
  - general frame auto-provisioning

## Invariants
- Nexus-facing creation remains explicit.
- The creation path must go through `Spellbook`, not direct frame config injection alone.
- Nexus-facing creation must yield a usable rooted conduit immediately.
- The frame itself should still become available through the normal runtime and descriptor surfaces after creation, but it is not the public return value.

## Required Deltas
- Replace direct frame-first realization in `NexusFrameManager` with a
  Spellbook-mediated rooted creation helper.
- Make root-conduit creation the default, not an optional afterthought.
- Let the caller provide a root-conduit name and define the fallback default clearly.
- Update `Rift.create_nexus_frame(...)` / `Nexus.create_nexus_frame_for_rift(...)`
  to return the rooted conduit.
