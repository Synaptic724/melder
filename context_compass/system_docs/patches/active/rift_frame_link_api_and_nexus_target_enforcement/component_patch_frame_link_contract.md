# Component Patch: FrameLinkContract Simplification

## Before
- `FrameLinkContract` accepts a convenience `contract_name` plus optional
  per-family `view_contract_name`, `command_contract_name`, and
  `codegen_contract_name`.
- The class exposes both same-name and per-family setter surfaces.

## After
- `FrameLinkContract` is created with the owning Rift id and target frame name.
- The selected ACL contract defaults to the target `frame_name` across all
  three families.
- Caller-provided per-family contract selection is removed from the live
  constructor/update seam.
- The class remains a per-frame contract record, not a policy router.

## Validation Expectation
- Focused unit tests prove constructor validation still holds and the selected
  contract defaults to the frame name for all three families.
