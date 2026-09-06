# Story: Expose named scopes without confusing roots, permissions or consumers

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-nexus-consumers
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:17:54Z

## User Narrative
As a user or inspection client, I want to locate a named live scope and understand its actual type,
owner and capabilities without mistaking it for a structural root.

## Ticket Contract
- ENTRY_GATE: Current Nexus/DevOps/cloud consumers are inventoried and owner agrees discovery semantics.
- EXECUTION_BOUNDARY: Relevant projections, lookup/enumeration, eligibility/ACL, command and root consumers.
- DEPENDENCIES: Directory/lifecycle story and cross-system discovery task.
- EXIT_GATE: Names, visibility and capabilities stay coherent across acquisition, pooling and upgrades.
- FAILURE_ESCALATION: No blanket normal-state relaxation or permission/eligibility bypass for discoverability.

## Requirements / Questions
- Trace present lesser-conduit projection and whether id/name searches already traverse descendants.
- Determine what is refreshed on fresh creation versus pooled acquisition/release and on name assignment.
- Keep automatic-mode metadata discovery distinct from Nexus/Rift eligibility and dynamic mutation gates.
- Preserve root-only operation contracts for bind, link, cluster membership and managed-frame bootstrap.
- Identify consumers relying on root counts, root ownership, stable ids or cloud list method semantics.
- A cloud lookup does not extend scope lifetime or bypass its existing capability restrictions.

## Source Orientation
- src/melder/aether/conduit/conduit.py: Nexus publication methods and create_lesser_conduit.
- src/melder/nexus/frame_descriptor_manager.py and frame-local projection contracts.
- src/melder/nexus/rift/frame_viewer/ and command_system/ through their component slices.
- src/melder/aether/aetheric_frame/conduit_cloud.py and DevOps information consumers.

## Tasks / Validation
Create precise consumer/projection tasks after source-backed impact discovery.
Test live/pooled/removed/renamed views, both runtime modes, id/name lookups and normal-only command rejection.

## Findings and Evidence
- Existing frame/conduit payloads already separate roots, cloud entries, names and parent/root identities.
  - src/melder/nexus/frame_descriptor_manager.py:259-415
- Publication requires rift_enabled; automatic discovery must not activate Rift or bypass ACLs.
  - src/melder/aether/spellbook/spellbook.py:5883-5922
- Fresh lesser creation publishes; soft pool release/reacquisition does not. Named transitions need
  projection consistency, with an explicit remove-versus-pooled-unnamed policy.
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:2227-2385
- Command-enabled lists use published records; raw name lookup validates publication/ACLs then calls
  root-only Aether. Decide any broader resolver explicitly and preserve the checks.
  - src/melder/nexus/rift/command_system/capability_command_system.py:198-294
  - src/melder/nexus/rift/command_system/codegen_command_system.py:272-309
  - src/melder/nexus/rift/command_system/command_system.py:1345-1428
- Static-room raw conduit access is intentionally absent; cluster membership requires normal state.
  - src/melder/nexus/rift/command_system/static_command_system.py:137-160
  - src/melder/aether/aetheric_frame/conduit_cloud.py:214-254

## Notes
- DATETIME: 2026-09-06T17:37:21Z
  TYPE: FACT
  CLAIM: Most necessary descriptor fields already exist; update emission timing and resolver
    semantics deliberately rather than inventing another descriptor or relaxing all state gates.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:259-415
  IMPACT: Naming is not new command authority or proof of root ownership.
  NEXT: Decide pooled-record treatment and the allowed named-lesser command surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Draft. Public discoverability is not new authority. Existing root-only consumers must remain root-only
unless a specific broader contract is explicitly approved.
