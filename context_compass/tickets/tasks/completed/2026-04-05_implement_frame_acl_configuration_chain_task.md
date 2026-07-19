# Task: Implement Frame ACL Configuration Chain

## Metadata
- Task ID: TASK-2026-04-05-implement-frame-acl-configuration-chain
- Story: STORY-2026-04-05-frame-acl-configuration-chain
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T08:14:08Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Implement the Frame ACL configuration-chain mechanics in the moved ACL package
and add the manager/Nexus façade methods over them.

## Ticket Contract
- ENTRY_GATE: the investigation task has locked the chain semantics in notes.
- EXECUTION_BOUNDARY: chain object, minimal config-node shape, manager façade,
  Nexus façade, and focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_investigate_frame_acl_configuration_chain_task.md
  - src/melder/aether/nexus/acl/
- EXIT_GATE: the chain mechanics exist in code and the focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementation reveals a
  larger propagation-policy question than this slice should own.

## Scope Boundaries
- In scope:
  - chain object
  - minimal config-node mechanics needed by the chain
  - manager and Nexus façade methods
  - focused tests
- Out of scope:
  - deep builder DSL
  - deep validator rules
  - full propagation engine

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the chain object, minimal config-node mechanics, manager
  facades, Nexus facades, and focused tests are landed and green.

## Steps / Checklist
- [x] Implement `FrameACLConfigurationChain`
- [x] Update config/container/manager to use the chain
- [x] Add manager façade methods
- [x] Add Nexus façade methods
- [x] Add focused tests
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- chain mechanics in code
- manager and Nexus façade methods
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-05_implement_frame_acl_configuration_chain_task.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_configuration_chain.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/frame_acl_container.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/component/melder/aether/test_frame_acl_component.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the implementation sneaks in deeper propagation semantics.
  Rollback: keep this slice bounded to chain mechanics and façade methods only.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_acl_configuration_chain/architecture_patch.md
  - system_docs/patches/active/frame_acl_configuration_chain/component_patch_frame_acl_configuration_chain.md
  - system_docs/patches/active/frame_acl_configuration_chain/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_configuration_chain/code_description_patch_frame_acl_configuration_chain.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T08:29:53Z
  TYPE: FACT
  CLAIM: The implementation slice is landed. `FrameACLConfiguration` is now a
    real config-node type with chain metadata (`configuration_id`,
    `source_configuration_id`, `previous_configuration_id`, `created_at`,
    `reason`, `locked`, JSON snapshot). `FrameACLConfigurationChain` now owns
    all config nodes for a frame and supports default head/current creation,
    head insertion, current selection, rollback, list/get/has/count, tail
    trim, and `create_new_from_acl_configuration(...)`. The container now owns
    the chain instead of a loose current+history pair, and manager/Nexus façade
    methods now expose the chain mechanics per frame.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:1-318
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:1-392
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-193
  - src/melder/aether/nexus/frame_acl_manager.py:1-333
  - src/melder/aether/nexus/nexus.py:1-2100
  IMPACT: The ACL subsystem now has real configuration lifecycle mechanics
    instead of only placeholder object ownership.
  NEXT: review the chain/current/head/rollback behavior and decide whether the
    next slice should deepen builder semantics or propagation rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task landed the ACL chain mechanics and the manager/Nexus façade methods.
The chain now owns all config nodes, starts with one default head/current
config, and supports head insertion, current selection, rollback, and tail
trimming.

## Context / Handoff Summary
This task exists to land the actual chain mechanics after the investigation
task pins down the exact behavior.
