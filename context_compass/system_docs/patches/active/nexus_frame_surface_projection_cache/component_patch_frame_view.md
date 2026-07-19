# Frame View Component Patch

## Before
- `FrameView` only supports direct construction from compiled access output.

## After
- `FrameView` supports detached cloning for safe cache returns.
- owned links remain detached clones too.
