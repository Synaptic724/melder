# Component Patch: Rift

## Before
- Rift is created with non-empty target-frame names already attached.
- Primary space creation is not part of the creation/programming flow.
- Viewer attachment is separate and optional after the fact.

## After
- Rift may start with no target frames.
- Rift programs one primary space immediately from `space_type`.
- Target-frame attachment is an explicit Rift action.
- Successful targeting refreshes the space-attached viewer.
