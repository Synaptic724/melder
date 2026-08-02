# Epic: Implement Codegen System Runtime

## Metadata
- Epic ID: EPIC-2026-04-25-implement-codegen-system-runtime
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z
- Target Window: 2026-Q2
- Related Program/Initiative: Codegen room execution layer over the completed
  capability substrate

## Problem / Opportunity
The codegen investigation lane is now explicit enough to implement, but the
runtime package is still empty and the current room surface is only a slim
facade:
- `CodegenCommandSystem` already owns the selected runtime helper surface plus
  placeholder `validate_codegen(...)` / `execute_codegen(...)`.
- `CodegenProjection` already carries frame descriptor truth, detached ACL
  configuration, and compiled access surface state.
- `src/melder/aether/nexus/rift/codegen_system/` still contains only
  `__init__.py`.

So the actual missing work is no longer "what is codegen?" It is the real
runtime package:
- validation subsystem
- namespace subsystem
- execution subsystem
- observability subsystem
- orchestration layer that composes them

## MRP Alignment (Most Reasonable Product)
The MRP is not a placeholder exec seam and not a giant room command family.

The MRP is:
- a thin public room facade
- one internal codegen runtime package
- explicit validation, namespace, execution, and observability subsystems
- one internal transaction context per validate/execute call
- no artifact/session workflow API

That gives us a coherent, governable codegen runtime that can grow without
rewriting the public room surface later.

## Ticket Contract
- ENTRY_GATE: the investigation epic already reconstructed the codegen
  baseline, the user accepted the `codegen_system/` package direction, and the
  user explicitly asked for the implementation epic/story/task decomposition.
- EXECUTION_BOUNDARY: implementation planning for the `codegen_system/`
  package only; no code edits in this epic.
- DEPENDENCIES:
  - `tickets/epics/2026-04-22_investigate_codegen_foundation_acl_and_validation_strategy_epic.md`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py`
  - `src/melder/aether/nexus/rift/projection/codegen_projection.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md`
- EXIT_GATE: one implementation epic exists, one story exists per
  `codegen_system` directory boundary, one task exists per planned non-init
  Python file, and the board routes the new implementation lane cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the package decomposition
  needs to be re-cut before code work starts.

## Goals (Outcomes)
- Stage one implementation epic for the full `codegen_system` package.
- Stage one story per real directory boundary in that package.
- Stage one task per planned non-`__init__.py` Python file.
- Make the implementation order explicit enough that code work can start from
  the root orchestration layer and proceed directory by directory.

## Non-Goals (Explicit Exclusions)
- Implementing the codegen runtime in this epic.
- Reopening the command-ownership refactor.
- Expanding the public room command surface beyond the already-selected helper
  set plus `validate_codegen(...)` / `execute_codegen(...)`.
- Designing a public artifact/session/transaction API.

## Scope Boundaries
- In scope:
  - `codegen_system/` package planning
  - file-level decomposition
  - story/task routing
  - board and epic linkage
- Out of scope:
  - source implementation
  - tests beyond planning references
  - unrelated AR/runtime tickets

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the investigation lane is mature enough that the next
  valid step is explicit implementation decomposition rather than more abstract
  design talk.

## Success Metrics
- One ready implementation epic exists for `codegen_system/`.
- Seven ready directory stories exist.
- One ready task exists for every planned non-`__init__.py` Python file.
- The board points at the implementation epic as the next codegen execution lane.

## Requirements (Functional + Non-Functional)
- Functional:
  - define the top-level orchestration package
  - define validation, namespace, execution, and observability directories
  - define one internal transaction-context file
  - define file-level responsibilities without overlap
  - keep the public room facade thin
- Non-functional:
  - no handwaving
  - no implementation in this epic
  - no fake task explosion over `__init__.py` files
  - keep directory/file ownership coherent

## Constraints / Assumptions
- `__init__.py` files stay empty/minimal per profile policy and do not need
  standalone implementation tasks.
- `CodegenCommandSystem` remains the public room facade.
- `CodegenSystem` is the orchestration object, not the whole subsystem.
- Validation returns `CodegenValidationResult`.
- Execution returns `CodegenExecutionResult`.
- Logging/history/monitoring matter, but they remain internal implementation
  concerns rather than new public commands.

## Dependencies / External References
- `src/melder/aether/nexus/rift/codegen_system/`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/aether/nexus/rift/projection/codegen_projection.py`
- `src/melder/aether/nexus/rift/rift.py`
- `codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md`
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Stage root + validation package stories and tasks.
      Success means orchestration, transaction context, validator, validation
      result, validation reporter, and validation strategies are all ticketed.
- [ ] Milestone 2: Stage namespace + execution package stories and tasks.
      Success means namespace configuration/build/output and compile/execute
      runtime pieces are all ticketed.
- [ ] Milestone 3: Stage observability package stories and tasks.
      Success means transaction logging, history recording, and monitoring are
      all ticketed and the board routes the codegen implementation lane.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-25-codegen-system-root-directory - root orchestration
      and transaction context
- [x] Story: STORY-2026-04-25-codegen-system-validation-directory - validator
      results and reporting
- [x] Story: STORY-2026-04-25-codegen-system-validation-strategies-directory -
      validation strategy family
- [x] Story: STORY-2026-04-25-codegen-system-namespace-directory - namespace
      objects and builder
- [ ] Story: STORY-2026-04-25-codegen-system-namespace-strategies-directory -
      namespace exposure strategies
- [x] Story: STORY-2026-04-25-codegen-system-execution-directory - compile and
      execution runtime
- [ ] Story: STORY-2026-04-25-codegen-system-observability-directory -
      logging/history/monitoring

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-root-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-validation-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-validation-strategies-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-namespace-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-namespace-strategies-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-execution-directory
- [ ] Task: Complete story STORY-2026-04-25-codegen-system-observability-directory
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The implementation epic exists and is routed.
- Every planned non-init codegen runtime file has a task.
- Every directory boundary has a story.
- The investigation epic now has a concrete downstream implementation lane.

## Risks / Mitigations
- Risk: the package is over-segmented into meaningless files.
  Mitigation: keep one file per real responsibility and keep `__init__.py`
  out of standalone task planning.
- Risk: validation/namespace/execution responsibilities overlap.
  Mitigation: enforce directory-level ownership in the story/task contracts.
- Risk: observability turns into a vague hook bucket.
  Mitigation: make logger/history/monitor three explicit files with separate jobs.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Planning-only validation in this epic.
- Validation quality is:
  - decomposition coherence
  - file-to-story coverage
  - board/ticket routing correctness

## Rollout / Adoption Plan
- Create the implementation epic.
- Create one story per directory.
- Create one task per planned file.
- Route the board to the new codegen implementation epic.
- Start implementation from the root directory story first.

## Open Questions
- Whether `codegen_monitor.py` should own overwatch and sentinel bridging
  directly or whether that later wants a second internal file.
- Whether `codegen_name_resolution_strategy.py` should validate against
  namespace configuration only or also the compiled access surface directly.

## Decision Log
- 2026-04-25: Implementation decomposition is ready to stage; the next codegen
  move is package/file execution planning, not more abstract discussion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: DECISION
  CLAIM: The codegen implementation package should be staged as seven directory
    stories and one task per planned non-init Python file. `__init__.py` files
    are intentionally excluded from standalone tasks because the profile policy
    forbids export-wiring behavior there and the package markers are not the
    real implementation work.
  EVIDENCE:
  - user_instruction: "begin making an epic, stories for each directory and all the tasks for each py file"
  - src/melder/aether/nexus/rift/codegen_system/__init__.py:1-1
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:43-57
  IMPACT: The planning lane can stay explicit without creating meaningless init-only tasks.
  NEXT: create the directory stories and file tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic stages the full codegen implementation decomposition for the
`codegen_system/` package. It is the downstream execution lane from the
investigation epic and should hand the next prompt directly into the root
directory story.
