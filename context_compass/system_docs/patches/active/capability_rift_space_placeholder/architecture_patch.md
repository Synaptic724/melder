# Patch Architecture: Capability Rift Space Placeholder

## Metadata
- Patch ID: `capability_rift_space_placeholder`
- Status: active
- Updated: 2026-04-09T11:04:56Z

## Objective
Add `capability` as a first-class placeholder `RiftSpaceType` and a concrete
`CapabilityRiftSpace` runtime class.

## Core Decision
- Add the third space type now.
- Keep it placeholder-only.
- Wire primary-space creation to instantiate it.
- Do not implement capability execution semantics yet.

## Non-Goals
- capability ACL model
- capability handles
- capability method execution
