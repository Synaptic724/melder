# Component Patch: CommandSystem

## Before
- `CommandSystem` exposed direct conduit/spell getters but lacked the generic
  conduit-discovery query helpers.
- The conduit getters were named `get_conduit_object_by_*`.

## After
- `CommandSystem` exposes conduit discovery/query helpers:
  - list ids
  - list names
  - count
  - has by id
  - has by name
  - find id by name
- The conduit getters are renamed to:
  - `get_conduit_by_id`
  - `get_conduit_by_name`

## Contract
- Query helpers stay on the command surface because the room/agent needs them.
- Ownership still remains below the command layer.
- ACL and room-mode behavior continues to apply underneath the renamed getters.

## Validation Expectations
- Focused command/Nexus tests should prove query behavior plus renamed getter
  behavior.
