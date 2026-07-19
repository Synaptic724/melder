# architecture_patch

## Metadata
- Patch ID: frame_acl_configuration_chain
- Status: draft
- Owner: codex
- Created: 2026-04-05T08:14:08Z
- Updated: 2026-04-05T08:14:08Z

## Patch Scope and Non-Goals
- Objective:
  Add the real frame ACL configuration-chain mechanics:
  `FrameACLConfigurationChain`, chain-owned config nodes, manager façade
  methods, and Nexus façade methods.
- Non-goals:
  - deep builder DSL
  - deep validator rule engine
  - full propagation engine

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| frame_acl_configuration | modify | minimal config-node shape must support chain ownership | acl bootstrap |
| frame_acl_configuration_chain | add | own config-node history/current/head mechanics | acl bootstrap |
| frame_acl_container | modify | own the chain instead of loose current/history fields | acl bootstrap |
| frame_acl_manager | modify | façade the chain for frame-targeted access | acl bootstrap |
| nexus | modify | façade chain access at the root boundary | acl bootstrap |

## Interface and Boundary Deltas
- Boundary delta 1:
  The chain owns all configuration nodes.
- Boundary delta 2:
  The container owns the chain.
- Boundary delta 3:
  The manager façades the chain per frame target.
- Boundary delta 4:
  `Nexus` façades the manager for root-level frame ACL access.

## Cross-Component Invariants
- Invariant 1:
  Each frame container has one chain.
- Invariant 2:
  The chain starts with one default head/current config.
- Invariant 3:
  Tail trim is the only delete behavior.
- Invariant 4:
  New committed configs are inserted at the head.

## Validation Expectations and Evidence Plan
- Validation item 1:
  The chain owns the config nodes and starts with one default config.
- Evidence source 1:
  `src/melder/aether/nexus/acl/`
- Validation item 2:
  Manager/Nexus façade methods expose the chain mechanics cleanly.
- Evidence source 2:
  `src/melder/aether/nexus/frame_acl_manager.py`
  `src/melder/aether/nexus/nexus.py`

## Ticket Coverage Map
- Epic:
  EPIC-2026-04-05-frame-acl-configuration-chain
- Story:
  STORY-2026-04-05-frame-acl-configuration-chain
- Tasks:
  - TASK-2026-04-05-investigate-frame-acl-configuration-chain
  - TASK-2026-04-05-implement-frame-acl-configuration-chain

## Unknowns and Decision Requests
- UNKNOWN:
  Whether current should always follow head on commit in this slice.
- DECISION_REQUEST:
  None yet.

## Context / Handoff Summary
- What changed:
  The ACL chain now has a dedicated patch lane.
- What remains:
  Lock the semantics, then land the implementation.
- Next entrypoint:
  `component_patch_frame_acl_configuration_chain.md`
