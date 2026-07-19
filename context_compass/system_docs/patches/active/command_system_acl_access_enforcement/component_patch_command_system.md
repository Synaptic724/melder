# Component Patch: CommandSystem

## Before
- command-system performs no ACL enforcement
- selected-target and direct getter paths always resolve when runtime objects exist

## After
- selected-target and direct getter paths enforce compiled command ACL state
- spell fetches gate on `spell_index_id`
- workstation-bound objects remain outside post-bind ACL policing

## Interface Deltas
- command getters fail fast when frame/conduit/spell access is not enabled

## State / Failure Deltas
- ACL-denied access now raises before returning the object
