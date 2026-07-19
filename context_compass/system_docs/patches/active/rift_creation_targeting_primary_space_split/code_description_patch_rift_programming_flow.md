# Code Description Patch: Rift Programming Flow

1. `Nexus.create_rift(...)` creates and registers a bare `Rift`.
2. The new `Rift` programs one primary space from its configured `space_type`.
3. No target frames are attached during bare Rift creation.
4. `Rift.target_frame(...)` later:
   - asks Nexus to validate frame legality for the Rift's chosen `space_type`
   - registers the frame on the frame-link contract
   - refreshes the attached viewer from descriptor + current ACL state
5. Illegal dynamic targeting fails fast and does not create a fallback second workspace.
