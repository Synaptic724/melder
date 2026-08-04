# Story: Frame ACL Configuration Chain
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the frame ACL configuration-chain lane and left the chain mechanics landed in code.


## Metadata
- Story ID: STORY-2026-04-05-frame-acl-configuration-chain
- Epic: EPIC-2026-04-05-frame-acl-configuration-chain
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T08:14:08Z
- Updated: 2026-04-09T21:59:36Z

## User Narrative
As the project owner, I want one real ACL configuration chain per frame, so the
ACL subsystem can support current/head/history/rollback mechanics before we
deepen the rest of the ACL system.

## Value / MRP Alignment
This story gives the ACL subsystem a serious state model instead of a loose
current-plus-history placeholder. That is the minimum coherent foundation for
later builder, validator, view, and codegen propagation work.

## Ticket Contract
- ENTRY_GATE: the placeholder ACL subsystem exists and the user explicitly
  selected the chain mechanics as the next slice.
- EXECUTION_BOUNDARY: chain object, minimal config-node fields, manager/Nexus
  façade methods, and focused validation only.
- DEPENDENCIES:
  - EPIC-2026-04-05-frame-acl-configuration-chain
  - TASK-2026-04-04-scaffold-frame-acl-subsystem-placeholders
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- EXIT_GATE: the chain mechanics exist in code, the manager/container use them,
  and the focused tests prove head/current/rollback/trim behavior.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the chain design forces a
  broader propagation-policy choice this story should not own.

## Requirements (Functional)
- Add `FrameACLConfigurationChain`
- Make the chain own all config nodes
- Initialize with one default head/current config
- Add head insertion
- Add current selection
- Add rollback
- Add tail trimming
- Add manager and Nexus façade accessors over the chain

## Requirements (Non-Functional)
- Thread-safe
- Bounded
- Reviewable
- No overbuilt propagation logic in this story

## Scope Boundaries
- In scope:
  - chain mechanics
  - minimal config-node mechanics needed by the chain
  - manager and Nexus façade methods
  - focused tests
- Out of scope:
  - deep builder DSL
  - deep validator rule engine
  - full propagation engine

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the chain mechanics are now landed in code and the focused
  chain/Nexus test surface is green.

## Dependencies / Related Work
- tickets/epics/2026-04-05_frame_acl_configuration_chain_epic.md
- tickets/tasks/2026-04-05_investigate_frame_acl_configuration_chain_task.md
- tickets/tasks/2026-04-05_implement_frame_acl_configuration_chain_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-05-investigate-frame-acl-configuration-chain - lock the mechanics and façade split
- [x] Task: TASK-2026-04-05-implement-frame-acl-configuration-chain - land the chain and tests
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The container owns a real chain object
- The chain starts with one default head/current config
- Manager and Nexus façade methods exist for chain access
- Focused tests prove the chain behavior

## Validation / Test Plan
- Focused unit tests for the chain object
- Focused manager/Nexus façade tests for selection/rollback/listing behavior

## UX / API / Data Notes
- This story is about ACL configuration mechanics, not final schema richness
  or propagation behavior

## Risks / Mitigations
- Risk: current/head semantics get muddled before propagation is designed
  properly.
  Mitigation: keep the chain mechanics explicit and small in this slice.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether current should always move with head on commit in this slice
- Whether rollback should be direct selection or copy-to-head later

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_acl_configuration_chain/architecture_patch.md
  - system_docs/patches/active/frame_acl_configuration_chain/component_patch_frame_acl_configuration_chain.md
  - system_docs/patches/active/frame_acl_configuration_chain/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_configuration_chain/code_description_patch_frame_acl_configuration_chain.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T08:14:08Z
  TYPE: FACT
  CLAIM: This story exists because the user wants the ACL mechanics grounded in
    a real chain before we widen the builder/validator internals. The chain
    should own all config nodes, start with one default head/current config,
    allow rollback/current selection, and use tail trimming as the only delete
    behavior.
  EVIDENCE:
  - user_instruction: "the chain owns the configuration objects"
  - user_instruction: "the chain should exist with a single empty configuration object inside it as the head"
  - user_instruction: "deletion is tailtrim thats it"
  IMPACT: We can now build a bounded, mechanical ACL state layer that later
    builder and propagation work can trust.
  NEXT: investigate the exact chain/current/head behavior and then implement it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to land the real ACL chain mechanics before more ACL
subsystem depth is added.

