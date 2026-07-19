# Component Patch: FrameACLCompiler

## Before
- compiles visible spell record keys only
- no resolved spell-index target output

## After
- compiles visible spell record keys for viewer consumers
- also compiles resolved visible spell-index ids for later runtime consumers

## Interface Deltas
- compiled ACL surface grows spell-index outputs beside record-key outputs

## State / Failure Deltas
- viewer path remains record-key compatible
- command/codegen/runtime consumers can start consuming spell-index ids later
