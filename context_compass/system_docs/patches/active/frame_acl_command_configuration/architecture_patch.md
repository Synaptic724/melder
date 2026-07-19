# Architecture Patch: Frame ACL Command Configuration

## Patch Scope and Non-Goals
Scope:
- add `FrameACLCommandConfiguration` as a typed sibling inside
  `FrameACLConfiguration`
- extend the validator so command configuration is validated separately
- keep the bundle-selection model unchanged

Non-goals:
- static/capability runtime execution
- viewer/runtime warning pipeline
- independent view/command/codegen selection

## Changed-Components Matrix
| component | change |
|---|---|
| `FrameACLCommandConfiguration` | new typed command-config object |
| `FrameACLConfiguration` | bundle gains `command_configuration` |
| `FrameACLValidator` | validates command config separately |
| `FrameACLBuilder` | seeds/edits command config in the bundle |

## Interface and Boundary Deltas
- `FrameACLConfiguration` MUST carry:
  - `view_configuration`
  - `command_configuration`
  - `codegen_configuration`
- `FrameACLValidator.validate_configuration(...)` MUST validate all three typed
  children.
- The frame link / Rift named-contract selection seam MUST remain one selected
  bundle name per frame.

## Cross-Component Invariants
- One `FrameACLContainer` per frame remains the owning shell.
- One named `FrameACLConfiguration` remains the selected set/bundle.
- Command policy MUST stay distinct from codegen policy.
- Codegen ACL behavior MUST NOT be repurposed as command permission truth.

## Migration / Rollout Order
1. Add the new typed command config object.
2. Extend the bundle/root config object to carry it.
3. Extend validator and builder.
4. Update interfaces and focused tests.

## Rollback Strategy
- If command config destabilizes the bundle, remove the new sibling and restore
  the two-child bundle shape.
- Do not alter named-contract selection semantics in this slice.

## Validation Expectations and Evidence Plan
- Focused unit coverage over ACL bundle/validator/builder paths.
- Evidence target:
  - new config file
  - bundle file
  - validator file
  - builder file
  - updated tests

## Ticket Coverage Map
- epic:
  - `tickets/epics/2026-04-11_frame_scoped_contract_registries_and_rift_binding_epic.md`
- story:
  - `tickets/stories/2026-04-11_extend_frame_acl_bundle_with_command_configuration_story.md`
- task:
  - `tickets/tasks/2026-04-11_add_frame_acl_command_configuration_and_validation_task.md`

## Unknowns and Decision Requests
- UNKNOWN: exact allowed command-operation families for the first validator cut
- UNKNOWN: whether compiler metadata should expose command profile identity in
  the same slice or later
