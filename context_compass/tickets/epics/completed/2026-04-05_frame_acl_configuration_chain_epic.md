# Epic: Build Frame ACL Configuration Chain
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the frame ACL configuration-chain epic and archived the landed chain foundation.


## Metadata
- Epic ID: EPIC-2026-04-05-frame-acl-configuration-chain
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T08:14:08Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift Profile Surface And Access Model

## Problem / Opportunity
The placeholder ACL subsystem now has the right ownership shape, but the
actual configuration mechanics are still too weak. We need one real
configuration chain per frame that:
- starts with one default head config
- supports head insertion for new configs
- supports current selection and rollback
- supports bounded tail trimming
- gives `Nexus` and the frame ACL manager a clean façade over those mechanics

Without this layer, the builder/config/validator objects exist but do not yet
have a serious configuration lifecycle to operate on.

## MRP Alignment (Most Reasonable Product)
This is MRP-critical because ACL state needs one coherent lifecycle before
FrameView, FrameViewer, codegen validation, and later propagation can build on
it. The goal is not a giant ACL engine. The goal is one stable chain model
that is good enough to support current/rollback/history mechanics cleanly.

## Ticket Contract
- ENTRY_GATE: the placeholder ACL subsystem exists and the user explicitly
  approved building the chain mechanics before deepening builder/validator
  internals.
- EXECUTION_BOUNDARY: chain object, minimal config-node fields, manager/Nexus
  façade methods, and focused validation only.
- DEPENDENCIES:
  - tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
  - tickets/stories/2026-04-04_frame_acl_subsystem_bootstrap_story.md
  - src/melder/aether/nexus/acl/
- EXIT_GATE: the chain exists in code, containers own it, manager/Nexus façade
  methods exist, and focused tests prove head/current/rollback/trim behavior.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the chain mechanics force a
  bigger propagation-policy choice than this slice should own.

## Goals (Outcomes)
- Add `FrameACLConfigurationChain`
- Make the chain own all configuration nodes
- Start each frame with one default head/current config
- Support head insertion, current selection, rollback, and tail trimming
- Add manager and Nexus façade methods over those mechanics

## Non-Goals (Explicit Exclusions)
- Deep builder DSL design
- Deep validator rule engine
- Full ACL propagation to Rift/view/codegen

## Scope Boundaries
- In scope:
- chain mechanics
- minimal config-node mechanics needed by the chain
- manager and Nexus façade methods
- focused tests
- Out of scope:
- full ACL schema design
- full propagation engine
- workstation/codegen integration

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants the chain mechanics built now,
  before further deepening the other ACL subsystem objects.

## Success Metrics
- Every frame ACL container owns one chain
- The chain starts with one default head/current config
- Rollback and selection work cleanly
- Tail trimming is bounded and deterministic
- Nexus can target a frame and ask for current/head/list/rollback mechanics

## Requirements (Functional + Non-Functional)
- Functional:
  - one chain per frame container
  - all configs live inside the chain
  - head insertion for new committed configs
  - current selection
  - rollback to historical configs
  - bounded tail trimming
- Non-functional:
  - thread-safe
  - simple
  - reviewable
  - no overbuilt propagation logic in this slice

## Constraints / Assumptions
- Tail deletion is the only delete behavior
- Configs in the chain should be locked once committed
- Builder/validator can remain thin while the chain mechanics land
- The chain should be able to list configs newest-first

## Dependencies / External References
- `src/melder/aether/nexus/acl/`
- `tickets/artifacts/nexus_acl_builder_and_persistence_model.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation and method split are documented in the task notes.
- [ ] Milestone 2: Chain mechanics land in code with manager/container wiring.
- [ ] Milestone 3: Focused tests prove current/head/rollback/trim behavior.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-05-frame-acl-configuration-chain - implement the
      chain mechanics and façade methods

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-05-frame-acl-configuration-chain
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `FrameACLConfigurationChain` exists and owns all config nodes
- containers use the chain instead of a loose current+history pair
- manager and Nexus façade methods exist for the chain lifecycle
- focused tests pass for the chain boundary

## Risks / Mitigations
- Risk: chain mechanics sprawl into the full propagation engine.
  Mitigation: keep this lane focused on history/current/head mechanics only.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused unit tests for the chain object
- Focused manager/container/Nexus façade tests for chain access and rollback

## Rollout / Adoption Plan
- Investigate and lock the chain model
- Implement it in the moved ACL package
- Wire manager and Nexus façade methods
- Validate before moving on to deeper builder/validator work

## Open Questions
- Whether current should always follow head on commit or only after later
  propagation
- Whether rollback should be a direct current-pointer move or a new head copy

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
  TYPE: PLAN
  CLAIM: The next ACL slice should stop widening the placeholder subsystem and
    instead build the chain mechanics that everything else will depend on. The
    user wants one chain per frame, all configuration nodes owned by that
    chain, one default head/current config at initialization, head insertion for
    new configs, rollback/current selection, and automatic tail trimming only.
  EVIDENCE:
  - user_instruction: "the chain owns the configuration objects"
  - user_instruction: "the chain should exist with a single empty configuration object inside it as the head"
  - user_instruction: "deletion is tailtrim thats it"
  IMPACT: We now have a bounded mechanical slice that should land before deeper
    ACL schema and propagation work.
  NEXT: create the story/task and patch-doc lane, document the exact chain
    mechanics, then implement them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to add the real ACL configuration-chain mechanics before
deeper builder/validator or propagation work continues.

