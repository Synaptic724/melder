# Task: Map named lesser conduit implications across subsystems

## Metadata
- Task ID: TASK-2026-09-06-named-conduit-cross-system-discovery
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Story: none (cross-cutting epic discovery)
- Status: review
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:44:52Z

## Objective
Map how optional lesser names/discovery interact with pooling, automatic/dynamic mode, frame root
ownership, Crystallizer recording/replay, Nexus projection/ACL/commands and other cloud consumers.

## Ticket Contract
- ENTRY_GATE: Owner approved cross-system discovery and the parent epic is recorded.
- EXECUTION_BOUNDARY: Indexed docs, complete relevant source methods/call paths, focused read-only
  checks/probes and ticket/story findings. No runtime or generated-source edits.
- DEPENDENCIES: tickets/tasks/2026-09-06_named_conduit_semantics_task.md and the parent epic's draft stories.
- EXIT_GATE: Evidence map, concrete impacts, recommended boundaries and genuine owner decisions are recorded.
- FAILURE_ESCALATION: Stop before implementing or deciding unapproved recording/lifetime/permission semantics.

## Questions
- Which consumers require roots specifically, and which really need a discovery directory?
- Is automatic naming/discovery purely metadata, or does any current gate rely on unnamed lessers?
- What happens to name/projection/identity when a lesser is created, pooled, reacquired or upgraded?
- What does Crystallizer record now: root topology, lesser topology, scope instances, or none of these?
- What does Nexus expose for lessers today, and which commands presume the selected conduit is normal?
- Does broadening cloud lookup/listing affect frame liveness, DevOps counts, clusters, lookup caches or restore?

## Steps / Checklist
- [x] Map the identified root/discovery consumers and pool/upgrade transitions.
- [x] Trace Nexus publication, visibility/ACL and command assumptions.
- [x] Trace Crystallizer emissions, root replay and name-collision consumers.
- [x] Synthesize story-level implications, validation expectations and owner decisions.

## Validation
- Prior naming evidence: three existing integration tests and an isolated probe passed.
- Two-mode pooled-name probe passed and confirmed the current stale-label/reassignment issue.
- Source-backed impact review completed; no implementation tests for the proposed feature exist yet.
- Full suite not run. Runtime source, CI and generated assets were not modified by this task.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Initial source-backed implications, probe results and owner decisions are recorded.

## Noting Behavior
Read one call path through; record factual evidence and a next single step before moving to another subsystem.

## Notes
- DATETIME: 2026-09-06T17:17:54Z
  TYPE: PLAN
  CLAIM: Reuse verified naming evidence instead of repeating it. First identify consumers of the
    frame root maps and cloud enumeration; then follow Nexus publication and Crystallizer replay.
  EVIDENCE:
  - tickets/tasks/2026-09-06_named_conduit_semantics_task.md
  - src/melder/aether/aetheric_frame/aetheric_frame.py:160-196
  IMPACT: Keep discoverability distinct from ownership and avoid scope expansion into new lifetime features.
  NEXT: Inventory and read the relevant frame/cloud consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:28:01Z
  TYPE: FACT
  CLAIM: Aether list/count/name/id facades read root-only frame maps directly; they do not route
    through ConduitCloud. Transfer-of-ownership and Nexus command surfaces call those Aether APIs.
    Conduit cleanup owns child/pool teardown separately from root unregistration. The conduit crystal
    emitter explicitly excludes lessers and automatic mode, while Nexus conduit publication accepts
    normal, lesser and pooled_lesser states when publication is enabled.
  EVIDENCE:
  - src/melder/aether/aether.py:1643-1890
  - src/melder/aether/conduit/conduit.py:443-467
  - src/melder/aether/conduit/conduit.py:756-951
  IMPACT: Broadening a cloud index alone will not broaden Aether lookup or command access. Conversely,
    broadening root maps would alter consumers beyond naming. Discovery and persistence already differ.
  NEXT: Read Nexus records/commands and the Crystallizer restore/admission consumers found by search.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: FACT
  CLAIM: Nexus frame summaries already distinguish root ids/names/counts from cloud names/counts.
    Conduit records already carry name, state, parent id, depth and root id. Passive publication is
    gated by rift_enabled, not the dynamic flag alone. Fresh lessers publish, but pooled release
    and reuse deliberately do not republish. Capability/codegen raw-name helpers first validate
    published identity and command permissions, then use root-only Aether lookup; static rooms
    deliberately reject raw conduit access. Naming must not silently change those permissions.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:222-415
  - src/melder/aether/spellbook/spellbook.py:5883-5922
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:2227-2385
  - src/melder/nexus/rift/command_system/command_system.py:1345-1428
  - src/melder/nexus/rift/command_system/capability_command_system.py:198-294
  - src/melder/nexus/rift/command_system/codegen_command_system.py:272-309
  - src/melder/nexus/rift/command_system/static_command_system.py:137-160
  IMPACT: Existing payload fields largely fit named scopes. Publication timing and the final
    live-object resolver need explicit decisions; discovery must not imply new raw-object authority.
  NEXT: Record the persistence and pool implications before synthesizing the design choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: FACT
  CLAIM: Conduit._emit_conduit_twin requires normal state, dynamic mode and active recording.
    RestoreEngine._conjure_for_book selects one recorded conduit per Spellbook and calls conjure;
    simply emitting lesser twins would not restore a child hierarchy correctly. Both host preflight
    and skip-existing replay probe cloud.has_conduit_name, so a wider discovery namespace can
    change restore collisions even if lesser scopes themselves remain unrecorded. Transfer impact
    enumeration and cluster membership are also intentionally root-oriented consumers.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:421-467
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1826-1880
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:434-544
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-814
  - src/melder/aether/aetheric_frame/conduit_cloud.py:214-254
  - src/melder/aether/aetheric_frame/conduit_cloud.py:663-707
  IMPACT: Recommended boundary is ephemeral discovery without a new crystal family or lifetime.
    Still specify restore collision rules and preserve root-only transfer/cluster contracts.
  NEXT: Synthesize recommendations and unresolved owner choices in the epic and draft stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:42:21Z
  TYPE: MEASURE
  CLAIM: An isolated pool probe passed in automatic and dynamic modes: a lesser labeled request-a
    is returned by the next acquisition as the same shell, still named request-a, and assigning
    request-b raises because the setter is write-once. This is a baseline finding, not the desired
    new behavior. All probe roots/books were cleaned; no runtime source file was changed.
  EVIDENCE:
  - Two-mode pooled-name probe (exit 0; same_shell=true, name_after_reuse=request-a, rename_rejected=true)
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit.py:1588-1630
  - src/melder/aether/conduit/conduit_pool.py:108-161
  IMPACT: Registry insertion alone would be incomplete. Unregister/clear before pool return and
    fresh name/publication on acquisition are part of the core feature contract.
  NEXT: Present the evidence-backed design boundaries and obtain owner direction before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Initial source-backed impact map is complete, not an exhaustive audit of every restore/ACL path.
Root/Aether enumeration, pool/name lifecycle, Nexus fields/publication/command gates, Crystallizer
emission/root replay/name collisions and cluster/transfer boundaries are evidenced above.
Owner must choose the contract before implementation. No source or generated-asset changes were made.
