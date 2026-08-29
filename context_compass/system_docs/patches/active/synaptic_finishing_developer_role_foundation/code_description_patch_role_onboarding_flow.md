# Code Description Patch: Role Onboarding Flow

## Control Flow Commitments
- onboarding resolves `general -> engineer -> synaptic_finishing_developer`
  in parent-first order
- the child role adds mandatory system-doc entries directly in its own
  `SKILLS.MD`
- the child role then loads its role-local documentation and testing skills

## Edge and Error Semantics
- if the role is registered in config but missing in top-level role-map
  guidance, discovery is degraded even if generic user-defined routing still
  works
- if the role omits direct system-doc entries, it falls back to `engineer`
  on-demand behavior and no longer satisfies the requested mandatory baseline

## Invariants and Non-Goals
- invariant: the role remains a user-defined overlay
- invariant: `active_profile` is not switched automatically
- non-goal: changing `engineer` baseline semantics

## Implementation Mapping
- config + top-level `SKILLS.md` registration implement the profile discovery path
- child `SKILLS.MD` implements the mandatory read chain
- role-local docs implement the finishing posture and deep skill behavior
