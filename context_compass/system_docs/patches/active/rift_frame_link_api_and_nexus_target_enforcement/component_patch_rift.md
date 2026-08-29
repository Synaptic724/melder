# Component Patch: Rift Frame-Link API Cut

## Before
- `Rift.target_frame(...)` accepts `contract_name`,
  `view_contract_name`, `command_contract_name`, and
  `codegen_contract_name`.
- The method validates target-frame names, runtime posture, and descriptor
  truth, then directly creates or updates `FrameLinkContract`.
- The method never delegates Nexus-managed frame access authorization back
  through Nexus before creating the frame link.

## After
- `Rift.create_frame_link(frame_name)` is the only live frame-link creation
  method.
- The method accepts only `frame_name`.
- The method validates generic target-frame policy and runtime posture as
  before.
- When the target frame is Nexus-managed, the method must call back into Nexus
  to authorize the attachment under the active topology mode before creating the
  frame link.
- The method binds the frame link to a frame-name-selected ACL contract and
  refreshes the current projection/viewer state after successful creation.

## Validation Expectation
- Focused Rift runtime tests prove:
  - the old `target_frame(...)` seam is gone
  - Nexus-managed frame attachment is denied when topology forbids it
  - authorized frame links refresh projections/viewer state normally
