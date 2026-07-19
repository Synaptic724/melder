# Code Description Patch: Frame-Bound Profile Flow

1. Rift receives a frame-specific viewer request.
2. Rift checks `FrameLinkContract` for that frame.
3. Nexus resolves:
   - `FrameDescriptor`
   - current `FrameACLConfiguration`
   - compiled ACL surface
4. Viewer builder clones the requested `FrameViewerProfile`.
5. The selected clone binds by reference to the resolved frame state.
6. Viewer execution for that frame uses the selected bound profile.
