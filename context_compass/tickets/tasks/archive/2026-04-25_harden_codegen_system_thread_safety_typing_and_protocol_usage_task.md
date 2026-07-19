# Task: Harden Codegen System Thread Safety Typing And Protocol Usage

## Metadata
- Task ID: TASK-2026-04-25-harden-codegen-system-thread-safety-typing-and-protocol-usage
- Story:
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-04-25T11:35:22Z
- Updated: 2026-04-26T20:06:02Z

## Objective
Review the built `codegen_system` files and harden them to the repository's
thread-safety, cleanup, typing, and interface standards.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a full hardening pass across the
  built `codegen_system` files, including `_lock` ownership, cleanup
  discipline, `check_cleaned()` usage, stronger type hints, and protocol use
  for externally supplied collaborators.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/utilities/interfaces/interfaces.py`
  - base onboarding docs only where the new interface/protocol rule should be
    recorded
  - directly affected unit coverage in `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - `codex/context_compass/tickets/epics/2026-04-25_implement_codegen_system_runtime_epic.md`
  - `src/melder/utilities/general_base/cleanable.py`
  - `src/melder/utilities/interfaces/interfaces.py`
- EXIT_GATE: the built `codegen_system` classes follow the repository cleanup
  and locking pattern consistently enough that no owned mutable state object
  remains unguarded, collaborator `Any`/`object` hints are replaced by
  existing or new protocols where justified, and the focused codegen ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested “all objects”
  rule would force obviously immutable value objects into fake cleanup
  ownership that hurts clarity more than it helps.

## Scope Boundaries
- In scope:
  - thread-safe cleanup hardening for built `codegen_system` classes
  - stronger typing across the built codegen files
  - protocol/interface additions where external collaborators are passed in
  - synaptic overlay documentation updates for the protocol-usage rule
- Out of scope:
  - new codegen features
  - new workflow/buffer semantics
  - unrelated AR/runtime refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a broad codegen-system
  hardening pass and clarified the interface/protocol expectation.

## Steps / Checklist
- [ ] Inventory the built `codegen_system` classes and classify mutable state owners versus value objects.
- [ ] Harden the state-owning classes to the repo cleanup/lock pattern.
- [ ] Replace weak `Any`/`object` collaborator hints with existing or new protocols where justified.
- [ ] Update synaptic overlay docs to record the protocol-usage rule.
- [ ] Add/update focused unit coverage.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- hardened `codegen_system` classes
- stronger protocol-based typing where justified
- synaptic overlay doc update for protocol usage
- focused validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/rift/codegen_system/
- src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD
- codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/interfaces.md
- tests/unit/melder/aether/test_nexus.py

## Validation
- Executed:
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py src/melder/aether/nexus/rift/codegen_system/codegen_system.py src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace.py src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_room_objects_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_workstation_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_command_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_result.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_reporter.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_attribute_access_strategy.py src/melder/aether/nexus/rift/codegen_system/execution/codegen_execution_result.py src/melder/aether/nexus/rift/codegen_system/execution/codegen_compiler.py src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py src/melder/aether/nexus/rift/command_system/codegen_command_system.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"`
- Result:
  - `30 passed, 105 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: applying cleanup/lock machinery indiscriminately to immutable value
  objects creates fake lifecycle semantics.
  Rollback: keep a narrow exception boundary for truly immutable value objects
  if direct evidence shows cleanup ownership would be artificial.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-25T11:35:22Z
  TYPE: FACT
  CLAIM: The built `codegen_system` tree still contains broad `Any` / `object`
    collaborator hints and several state-owning classes that do not follow the
    repository's standard lock-and-cleanup pattern yet. Existing collaborator
    interfaces already cover part of the surface (`IRift`, `IRiftSpace`,
    `ICodegenRiftSpace`, `IWorkstation`, `ICommandSystem`), but the codegen
    files are not using them consistently.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-378
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-103
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_room_objects_strategy.py:1-59
  - src/melder/utilities/interfaces/interfaces.py:6858-8048
  IMPACT: We need a deliberate hardening pass, not piecemeal opportunistic edits.
  NEXT: classify which codegen classes are real mutable state owners and which
    are immutable value objects before touching the cleanup model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T11:54:04Z
  TYPE: DECISION
  CLAIM: The hardening pass now follows one explicit rule: state-owning and
    cross-file service objects in `codegen_system` should implement
    `Cleanable`, own an instance `RLock`, and use `check_cleaned()` on public
    methods/properties. Existing collaborator protocols should be preferred
    over `Any`/`object`, and new codegen-specific protocols are justified for
    cross-file codegen boundary objects used outside their defining file.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:1-129
  - src/melder/utilities/interfaces/interfaces.py:7669-7904
  - user_instruction: "you need a _lock obj RLock in each file because this whole system must be thread safe"
  - user_instruction: "if the object isn't built in the code we're using but its passed in thats a cannidate for a protocol"
  IMPACT: The refactor can stay coherent instead of mixing cleanup hardening
    and protocol typing ad hoc per file.
  NEXT: finish syncing the board and then return the hardened slice for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T11:54:04Z
  TYPE: FACT
  CLAIM: The built `codegen_system` files are now materially harder on
    lifecycle and typing. Cross-file codegen value/config objects now carry the
    repo cleanup/lock pattern, state-owning services/strategies now own locks
    and cleanup paths, `IRift` now exposes the codegen projection seam, new
    codegen boundary protocols exist in `interfaces.py`, and the room-facing
    codegen classes now use those interfaces instead of broad `object`/`Any`
    collaborators.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:7669-7909
  - src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py:1-219
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-396
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-142
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:1-168
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-692
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:211-237
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/interfaces.md:1-16
  IMPACT: The codegen runtime no longer carries the early-foundation shortcuts
    around collaborator typing and state-owner lifecycle semantics.
  NEXT: let the user decide whether to close this hardening task or point at a
    remaining codegen file that still feels under-hardened.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T20:06:02Z
  TYPE: FACT
  CLAIM: The ticket header was stale against the live board state. The lane is
    already routed as `review` on `attention_board.md`, but the task metadata
    still lacked `Agent Name` and still declared `in_progress`.
  EVIDENCE:
  - codex/context_compass/attention_board.md:25-25
  - codex/context_compass/tickets/tasks/2026-04-25_harden_codegen_system_thread_safety_typing_and_protocol_usage_task.md:1-12
  IMPACT: The task header needs lightweight normalization so the ticket and the
    live board no longer disagree about current ownership and state.
  NEXT: keep the task in `review` until the user either accepts closure or
    requests one more bounded hardening follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This task owns the broad hardening pass across the built `codegen_system`
files.
