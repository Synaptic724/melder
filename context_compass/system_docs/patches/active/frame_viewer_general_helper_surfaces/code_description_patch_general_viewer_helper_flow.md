# Code Description Patch: General Viewer Helper Flow

1. `FrameViewer` resolves the selected bound `general` profile for a frame.
2. The `general` profile holds:
   - `view_frame`
   - `view_conduit`
   - `view_spell`
3. Each helper reads the bound descriptor + ACL state by reference.
4. Tool calls route through the profile into the relevant helper object.
5. Returned data stays ACL-filtered and descriptor-driven.
