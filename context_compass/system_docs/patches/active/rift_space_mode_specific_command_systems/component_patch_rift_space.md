# Component Patch: RiftSpace

## Before
- `RiftSpace` directly constructs one generic `CommandSystem`
- room-specific behavior is forced through inline room-kind checks in the
  command-system body

## After
- `RiftSpace` builds its command surface through a room-owned factory seam
- room subclasses choose the correct command-system subclass

## Interface Deltas
- `RiftSpace.command_system` still exists and keeps the same high-level role
- construction moves from one fixed class to mode-specific composition

## State / Failure Deltas
- room mode becomes an ownership/composition concern instead of an inline
  branching concern in the generic command-system body
