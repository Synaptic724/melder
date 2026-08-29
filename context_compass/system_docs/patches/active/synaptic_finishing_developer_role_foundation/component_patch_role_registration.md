# Component Patch: Role Registration

## Component Purpose and Boundary in Current Architecture
This slice wires the new role into Context Compass without changing the current
default profile or shared baseline roles.

## Before/After Behavior Summary
Before:
- `synaptic_finishing_developer` does not exist in config or top-level role
  routing

After:
- the role is present in config profile lists and role map
- the role is explicitly discoverable from top-level `SKILLS.md`
- the role has its own user-defined overlay folder and `SKILLS.MD`

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - new role name
  - user-defined role path
- Outputs:
  - selectable profile
  - resolvable profile `SKILLS.MD`
- Error semantics:
  - none beyond normal onboarding failure if wiring is incomplete

## State and Lifecycle Deltas
- add new profile-list entries
- add new role-map entry
- keep `active_profile` unchanged

## Dependency and Ordering Constraints
- registration depends on a valid user-defined folder and `SKILLS.MD`
- `SKILLS.MD` must inherit from `agent_onboarding/default/engineer/SKILLS.MD`

## Validation Expectations
- config shows the new role in:
  - `available_profiles`
  - `user_defined_profiles`
  - `allowed_post_onboarding_profiles`
  - `router.profile_readme_policy`
  - `router.roles`
- top-level `SKILLS.md` shows the new role explicitly

## Unknowns and Open Decisions
- UNKNOWN: whether explicit top-level listing should eventually replace the
  generic `user_defined/*` note for all custom profiles
