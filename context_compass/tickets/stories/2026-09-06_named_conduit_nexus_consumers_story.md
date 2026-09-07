# Story: Expose named scopes without confusing roots, permissions or consumers

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-nexus-consumers
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1, updater_0
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-07T11:46:34Z

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
- Reuse ConduitRecord/ConduitDescriptorPayload name, state, parent, root and depth fields.
  The source does not indicate a need for a second named flag or a new record family.
- Keep frame-summary cloud names/counts current at named acquisition and release while preserving root counts.
- Update published name/state/parent data for pooled reuse; cloud registration alone does not update records.
- Distinguish same-id payload replacement from compiled visible/enabled id membership changes.
  Projections borrow live descriptors but own detached allowed-id sets.
- If pool return removes a record, reconcile compiled ids: ViewFrame currently raises on missing records.
  If a pooled record is retained unnamed, define its visibility explicitly and clear its prior scope metadata.
- Preserve existing ACL/raw-object gates when replacing the named command getter's root-only final lookup.
  The current id getter already has a recursive lesser fallback and is a candidate shared resolver.
- Forward the creation-time optional name through any supported Nexus lesser-creation command wrapper.
- Verify restored named lesser structure follows the same publication and permission contract as live creation.

## Source Orientation
- src/melder/aether/conduit/conduit.py: Nexus publication methods and create_lesser_conduit.
- src/melder/nexus/frame_descriptor_manager.py and frame-local projection contracts.
- src/melder/nexus/rift/frame_viewer/ and command_system/ through their component slices.
- src/melder/aether/aetheric_frame/conduit_cloud.py and DevOps information consumers.

## Tasks / Validation
Create precise consumer/projection tasks after source-backed impact discovery.
Test live/pooled/removed/reacquired views, each selected mode, id/name lookups and normal-only command rejection.
Test existing compiled projections when a known pooled id gains/loses a name and when membership changes.

## Findings and Evidence
- Existing frame/conduit payloads already separate roots, cloud entries, names and parent/root identities.
  - src/melder/nexus/frame_descriptor_manager.py:259-415
- Publication requires rift_enabled; discovery must follow frame eligibility and ACL policy.
  - src/melder/nexus/frame_descriptor_manager.py:222-257
- Fresh lesser creation publishes; soft pool release/reacquisition does not. Named transitions need
  projection consistency, with an explicit remove-versus-pooled-unnamed policy.
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:2227-2385
- Command-enabled lists use published records; raw name lookup validates publication/ACLs then calls
  root-only Aether. The raw capability cloud getter returns the cloud, so only that route follows cloud directly.
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

- DATETIME: 2026-09-07T11:46:34Z
  TYPE: FACT
  CLAIM: Deep source reading establishes where cloud is sufficient: raw cloud access and the
    frame-summary cloud-name capture. Viewer/command named reads instead require published records
    and compiled ACL membership; capability/codegen final named resolution uses Aether root maps.
    Existing descriptor fields already express names and lesser ancestry. Projections borrow live
    descriptors, but allowed-id sets are compiled; removal can leave a viewer-visible dangling id.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:259-497
  - src/melder/nexus/rift/command_system/capability_command_system.py:141-463
  - src/melder/nexus/rift/command_system/command_system.py:194-250
  - src/melder/nexus/rift/command_system/command_system.py:1345-1428
  - src/melder/nexus/rift/projection/command_projection.py:65-164
  - src/melder/nexus/rift/projection/view_projection.py:65-151
  - src/melder/nexus/rift/frame_viewer/view_frame.py:2182-2303
  - src/melder/nexus/acl/frame_acl_compiler.py:340-383
  - src/melder/nexus/acl/frame_acl_compiler.py:687-768
  IMPACT: Target publication and resolver integration; avoid inventing new naming state or assuming
    every payload change requires a full ACL rebuild. Pool-record treatment must account for existing projections.
  NEXT: Select pooled record visibility and membership refresh behavior, then map exact consumer edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Existing Nexus fields can describe named lessers. Cloud alone does not serve published named queries.
Use the recorded source distinctions to select publication, pooled-record and resolver behavior while
preserving ACLs and root-only capabilities. Structural restore must feed the same resulting contract.
