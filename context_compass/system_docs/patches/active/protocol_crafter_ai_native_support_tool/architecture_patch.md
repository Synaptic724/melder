# Architecture Patch: Protocol Crafter AI-Native Support Tool

## Objective
Add a dedicated AI-native support utility for crafting protocol code and
updating interface files.

## Non-Goals
- No generalized code-rewrite framework.
- No repo-wide import rewrites.
- No protocol synchronization engine.

## Changed Components
- new `ai_native_support_tools` package
- `ProtocolCrafter`
- focused tests

## Invariants
- generation remains best-effort and source-shape driven
- generated methods use `...` bodies
- add/remove helpers stay bounded to protocol-block append/removal
