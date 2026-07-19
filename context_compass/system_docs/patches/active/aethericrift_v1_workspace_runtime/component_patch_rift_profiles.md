# component_patch_rift_profiles

## Component purpose and boundary in current architecture
The AR profile stack defines capability/exposure behavior:
- `RiftProfile`
- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`

It is distinct from `RiftConfiguration`, which defines runtime behavior.

## Before/after behavior summary
- Before:
  Profile language drifted across older `FrameProfile` / `ConduitProfile` /
  AI-profile concepts.
- After:
  The active profile model is the narrower stack above, with no active
  `ConduitProfile` in the top-level AR model.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  frame posture, spellbook defaults, per-spell overrides
- Outputs:
  aggregate exposure/capability picture for the Rift/room
- Error semantics:
  contradictory profile state should surface as configuration/profile merge
  errors rather than silent widening of access

## State and lifecycle deltas
- Profiles shape exposure and behavior
- Config shapes runtime mechanics
- This distinction must remain explicit
- `AethericFrameProfile` should reflect the posture of frame-owned substrate
  services (`ConduitCloud`, `MutationResearch`, `DevOpsManager`) when that
  posture matters to AR
- Profiles should shape what part of the configured frame's exposed conduit/object
  surface becomes visible inside the room
- Profile merge order is frame defaults -> spellbook refinement -> spell final
  override
- `AethericRiftSystem` should maintain the aggregate profile view and invalidate
  it when underlying substrate profile truth changes

## Failure mode deltas
- Mixing config and profile concerns makes the room incoherent
- Reviving dead profile concepts (such as conduit profile) would reintroduce
  design drift

## Dependency and ordering constraints
- Feeds `RiftValidationSystem`
- Shapes what can be exposed into the workspace

## Validation expectations
- The aggregate profile stack matches the active top-level object folder
- `RiftConfiguration` is not treated as the ACL profile
- Profiles are treated as exposure/setup policy, not as a fake Python sandbox

## Unknowns and open decisions
- Exact merge semantics between the profile layers can remain iterative during
  implementation as long as the layering itself remains intact
