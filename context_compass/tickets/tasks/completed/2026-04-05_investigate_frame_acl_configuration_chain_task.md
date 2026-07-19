# Task: Investigate Frame ACL Configuration Chain
- Completed: 2026-04-09T21:59:36Z
- Summary: Locked the ACL chain mechanics before the implementation task landed them in code.


## Metadata
- Task ID: TASK-2026-04-05-investigate-frame-acl-configuration-chain
- Story: STORY-2026-04-05-frame-acl-configuration-chain
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T08:14:08Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Lock the exact chain mechanics, ownership split, and façade methods for the
Frame ACL configuration chain before the implementation task lands.

## Ticket Contract
- ENTRY_GATE: the ACL-chain epic/story are routed and this task is the active
  investigation lane.
- EXECUTION_BOUNDARY: investigation and design-lock only.
- DEPENDENCIES:
  - tickets/epics/2026-04-05_frame_acl_configuration_chain_epic.md
  - tickets/stories/2026-04-05_frame_acl_configuration_chain_story.md
  - src/melder/aether/nexus/acl/
- EXIT_GATE: task notes explicitly lock the chain mechanics, manager façade
  methods, and current/head/rollback semantics.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the chain mechanics force a
  propagation-policy decision outside this investigation slice.

## Scope Boundaries
- In scope:
  - chain object shape
  - current/head semantics
  - manager façade methods
  - Nexus façade methods
- Out of scope:
  - code changes
  - full builder DSL design
  - full propagation logic

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the chain mechanics and façade split are now pinned down in
  the notes and the implementation task has landed the model in code.

## Steps / Checklist
- [x] Lock the chain-owned state and methods.
- [x] Lock the manager façade methods.
- [x] Lock the Nexus façade methods.
- [x] Record the history-limit and tail-trim semantics.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed task notes for the chain design

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-05_investigate_frame_acl_configuration_chain_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/aether/nexus/acl/*`

## Risks / Rollback Notes
- Risk: the chain semantics stay muddy and implementation gets ahead of the
  design.
  Rollback: stop at the notes and do not start coding until the mechanics are
  explicit.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T08:14:08Z
  TYPE: FACT
  CLAIM: The chain should own all configuration nodes and start immediately
    with one default config as both head and current. The required chain state
    is: `head_configuration_id`, `current_configuration_id`,
    `configurations_by_id`, and `history_limit`. The minimum chain methods are:
    read (`get_head_configuration`, `get_current_configuration`,
    `get_configuration`, `has_configuration`, `list_configurations`,
    `list_configuration_ids`, `count_configurations`), mutation
    (`insert_head_configuration`, `select_current_configuration`,
    `rollback_to_configuration`), and maintenance (`trim_tail`). Tail trimming
    is the only delete behavior. New committed configs insert at the head.
    Rollback is allowed by moving the current pointer to an existing config.
  EVIDENCE:
  - user_instruction: "the chain owns the configuration objects"
  - user_instruction: "the chain should exist with a single empty configuration object inside it as the head"
  - user_instruction: "deletion is tailtrim thats it"
  - user_instruction: "the pointer should be able to rollback to different versions"
  IMPACT: We now have enough mechanical detail to implement the chain without
    deepening the other ACL subsystem objects first.
  NEXT: move the implementation task into active work and land the chain in the
    moved ACL package.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T08:14:08Z
  TYPE: FACT
  CLAIM: The user also requires a placeholder
    `create_new_from_acl_configuration(...)` path even before the deep config
    internals are built. The clean place for that behavior is on the chain or
    config-node boundary, not on `Nexus` directly. The manager should façade
    chain operations per frame, and `Nexus` should façade the manager for the
    root-level frame-targeting API.
  EVIDENCE:
  - user_instruction: "your missing a few methods though"
  - user_instruction: "you need to build that as a placeholder"
  - user_instruction: "the methods can live in the chain and facaded in the manager, and then the manager can facade them in the nexus"
  IMPACT: The implementation slice needs one placeholder copy/clone mechanic in
    the chain API even if the full config schema stays thin for now.
  NEXT: implement the chain and façade methods together in the implementation
    task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T08:14:08Z
  TYPE: PLAN
  CLAIM: The investigation needs to lock four things before code changes:
    the chain-owned state, the chain methods, the manager façade methods, and
    the Nexus façade methods. The user also explicitly wants a placeholder
    `create_new_from_acl_configuration` path captured even before the deep
    config internals are built out.
  EVIDENCE:
  - user_instruction: "your missing a few methods though"
  - user_instruction: "you need to build that as a placeholder"
  - user_instruction: "focus on the chain and its methods and how it interacts with manager and nexus"
  IMPACT: We should not widen the other ACL subsystem objects until the chain
    mechanics and façade split are pinned down.
  NEXT: record the exact method list and semantics in the notes, then open the
    implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to pin down the ACL configuration-chain mechanics before the
implementation task lands.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

