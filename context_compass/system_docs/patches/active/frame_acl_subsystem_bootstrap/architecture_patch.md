# architecture_patch

## Metadata
- Patch ID: frame_acl_subsystem_bootstrap
- Status: draft
- Owner: codex
- Created: 2026-04-04T21:59:53Z
- Updated: 2026-04-04T21:59:53Z

## Patch Scope and Non-Goals
- Objective:
  Add the first Nexus/descriptor-backed Frame ACL subsystem placeholders:
  `FrameACLManager`, `FrameACLContainer`, `FrameACLBuilder`,
  `FrameACLConfiguration`, and `FrameACLValidator`.
- Non-goals:
  - final ACL propagation engine
  - final JSON schema details
  - final Rift/view/codegen consumer integration

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| nexus | modify | own one frame ACL manager at the root boundary | nexus |
| frame_descriptor_manager | modify | ensure descriptor creation also provisions the matching ACL container | nexus |
| frame_acl_manager | add | own frame-name keyed ACL containers and frame-scoped ACL subsystem control | nexus |
| frame_acl_container | add | hold unique frame ACL objects for one frame | manager |
| frame_acl_builder | add | represent one mutable builder object for that frame | container |
| frame_acl_configuration | add | represent the current frame ACL config placeholder | container |
| frame_acl_validator | add | represent frame-scoped ACL validation placeholder | container |

## Interface and Boundary Deltas
- Boundary delta 1:
  `Nexus` remains faÃ§ade/root and does not directly own ACL object internals.
- Boundary delta 2:
  `Nexus` owns the ACL manager.
- Boundary delta 3:
  `FrameACLManager` owns `frame_name -> FrameACLContainer`.
- Boundary delta 4:
  Descriptor creation should also ensure the manager creates the matching frame
  ACL container with defaults.
- Boundary delta 5:
  The container owns the unique frame-scoped ACL objects including the single
  builder object for that frame.

## Cross-Component Invariants
- Invariant 1:
  `Nexus` owns one ACL manager.
- Invariant 2:
  One ACL manager owns one ACL container per frame target in its dictionary.
- Invariant 3:
  One ACL container owns one builder object for that frame.
- Invariant 4:
  The placeholder slice should not pretend to be a full ACL propagation system.

## Migration and Rollout Order
1. Update ACL tickets and active patch docs.
2. Add placeholder ACL classes.
3. Wire the manager into `Nexus` and keep descriptor-triggered container creation.
4. Add focused tests for the ownership chain and builder singleton behavior.

## Validation Expectations and Evidence Plan
- Validation item 1:
  `Nexus` owns one ACL manager and descriptor creation also provisions the
  matching ACL container.
- Evidence source 1:
  `src/melder/aether/nexus/nexus.py`
  `src/melder/aether/nexus/frame_descriptor_manager.py`
- Validation item 2:
  Manager owns one container and the container returns the same builder object.
- Evidence source 2:
  placeholder ACL subsystem files + focused unit tests

## Ticket Coverage Map
- Epic:
  EPIC-2026-04-02-rift-profile-surface-and-access-model
- Story:
  STORY-2026-04-04-frame-acl-subsystem-bootstrap
- Tasks:
  - TASK-2026-04-04-scaffold-frame-acl-subsystem-placeholders

## Unknowns and Decision Requests
- UNKNOWN:
  Exact placeholder method surface on the builder/config/validator objects.
- DECISION_REQUEST:
  None yet.

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded placeholder implementation lane.
- What remains:
  Scaffold the object chain and keep the slice structural.
- Next entrypoint:
  `component_patch_frame_acl_manager.md`
