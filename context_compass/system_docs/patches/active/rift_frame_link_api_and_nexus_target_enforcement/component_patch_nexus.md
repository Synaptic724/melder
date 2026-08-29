# Component Patch: Nexus-Managed Frame Authorization For Frame Links

## Before
- Nexus-owned frame topology rules exist in `NexusFrameManager` for:
  - `get_frame_for_rift(...)`
  - `create_frame_for_rift(...)`
  - `list_accessible_frame_names_for_rift(...)`
- The Rift frame-link creation path does not use that topology contract when a
  caller directly targets a Nexus-managed frame name.

## After
- Nexus remains the owner of Nexus-managed frame topology rules.
- Rift attachment to a Nexus-managed frame must go through a Nexus-owned
  authorization path before the frame link is created.
- The authorization path must reject:
  - non-shared names in `single`
  - other Rifts' private frames in `one_per_workspace`
  - missing managed frames that have not been explicitly created

## Validation Expectation
- Focused Nexus/Rift tests prove frame-link creation respects
  `single`, `indexed`, and `one_per_workspace` visibility for
  Nexus-managed frames.
