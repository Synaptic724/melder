# Code Description Patch: Rift Frame-Link Creation Flow

## Control Flow Commitment
1. `Rift.create_frame_link(frame_name)` receives one explicit target frame name.
2. The method validates:
   - non-empty name
   - target-frame allow/deny policy
   - room-type runtime posture
   - descriptor truth
3. If the target frame is Nexus-managed, the method delegates authorization to
   Nexus before creating the frame link.
4. The method ensures a frame-name-selected ACL contract exists for the frame.
5. The method creates the `FrameLinkContract` if absent.
6. The method refreshes projection/viewer state after a successful link.

## Edge / Error Semantics
- Empty frame names remain `ValueError`.
- Missing descriptor truth remains `ValueError`.
- Unauthorized Nexus-managed frame attachment remains `ValueError` and must
  originate from the Nexus topology path, not from a silent fallback.
- Missing frame-name ACL contract must be handled explicitly by materializing a
  same-name snapshot or by failing fast; no implicit `"default"` fallback from
  the public seam.

## Idempotency / Reentrancy
- Re-linking an already-linked frame should remain non-destructive.
- Re-linking must not duplicate target-frame ref counts.
- Re-linking must keep the selected frame-link contract name stable.

## Explicit Non-Goals
- No multi-contract selection UI/API at the Rift frame-link seam.
- No automatic Nexus-managed frame creation during frame-link creation.
