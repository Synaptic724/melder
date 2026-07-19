# Component Patch: FrameViewer

## Before
- one default active profile globally
- no explicit selected profile per frame

## After
- keeps reusable active profile templates
- stores selected bound profile per frame
- executes methods for a frame through that frame's selected bound profile
