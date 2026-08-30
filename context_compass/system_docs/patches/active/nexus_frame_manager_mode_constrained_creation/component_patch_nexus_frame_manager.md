# Component Patch: NexusFrameManager Raw Creation Rules

## Before
- `NexusFrameManager.create(...)` and `create_dynamic_frame(...)` validate the
  authored frame posture and generic frame-count budget.
- Those paths do not constrain raw creation by `nexus_frame_mode`.

## After
- Raw manager creation is mode-constrained:
  - `single`
    - only the canonical shared default frame name is allowed
  - `one_per_workspace`
    - raw manager creation is rejected because the path carries no Rift owner
  - `indexed`
    - explicit named creation remains allowed
- Rift-scoped creation APIs remain the owner-aware path for
  `one_per_workspace`.

## Validation Expectation
- Focused tests prove raw manager creation now respects the mode contract
  without regressing the existing Rift-facing Nexus frame behavior.
