# Patch Architecture: Rift Frame-Link API And Nexus Target Enforcement

## Objective
Replace the public Rift frame-attachment API with
`create_frame_link(frame_name)`, remove caller-selected ACL contract names from
that seam, and make Nexus-managed frame attachment obey Nexus topology rules at
link-creation time.

## Non-Goals
- Redesigning the broader frame ACL registry model.
- Reworking room/workstation ownership.
- Replacing the current projection compilation pipeline.
- Rewriting retained historical patch docs.

## Boundary
- In scope:
  - `Rift` frame-link API surface
  - `FrameLinkContract` constructor/update surface
  - Nexus-managed frame authorization during attachment
  - frame-name contract materialization for attachment
  - `IRift` and direct test/doc call-site updates
- Out of scope:
  - unrelated Nexus frame creation APIs
  - generic ACL builder/container redesign
  - command-system redesign

## Invariants
- `Nexus` remains the public AR root and the owner of Nexus-managed frame
  topology rules.
- `Rift` remains the owner of explicit frame-link contracts and the current
  projection registry.
- `FrameLinkContract` remains a Rift-local contract record, not a topology
  policy owner.
- Generic non-Nexus target frames still go through the existing target-frame
  name/runtime/descriptor checks.
- Nexus-managed target frames must additionally pass Nexus topology
  authorization before a frame link is created.

## Required Deltas
- Remove `Rift.target_frame(...)` from the live public/runtime contract.
- Add `Rift.create_frame_link(frame_name)` as the only frame-link creation API.
- Remove `contract_name`, `view_contract_name`, `command_contract_name`, and
  `codegen_contract_name` from the frame-link creation seam.
- Simplify `FrameLinkContract` so the selected contract defaults to the target
  `frame_name` and is no longer caller-configurable through the public seam.
- When the target frame is Nexus-managed, delegate attachment authorization
  back through `Nexus` before the frame link is created.
- Ensure a same-name ACL contract exists for the targeted `frame_name` before
  the Rift binds to it.

## Migration Order
1. Add the new task routing + patch docs.
2. Patch `FrameLinkContract` to remove caller-selected contract parameters.
3. Patch `Rift` to replace `target_frame(...)` with
   `create_frame_link(frame_name)`.
4. Add/adjust the Nexus-side attachment authorization seam used by Rift.
5. Update interface and direct call sites.
6. Update focused tests.
7. Update live architecture/components docs.

## Rollback Constraints
- Do not leave both `target_frame(...)` and `create_frame_link(...)` live.
- Do not silently fall back to the reserved `"default"` ACL name from the new
  public seam; if same-name materialization is required, do it explicitly.
