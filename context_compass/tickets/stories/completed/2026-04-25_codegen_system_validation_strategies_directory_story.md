# Story: Implement Codegen System Validation Strategies Directory
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the five validation strategy families
  landed and the validator became materially policy-governed instead of
  syntax-only.

## Metadata
- Story ID: STORY-2026-04-25-codegen-system-validation-strategies-directory
- Epic: EPIC-2026-04-25-implement-codegen-system-runtime
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## User Narrative
As an engineer, I want validation strategies split by rule family, so that the
validator stays composable and policy changes do not collapse into one giant
AST file.

## Value / MRP Alignment
The validator is first-class, and its rule families are also first-class.
Strategies keep validation MRP-sized but still extensible.

## Ticket Contract
- ENTRY_GATE: the validation directory story is staged and the validator
  already has a clear ownership boundary.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/strategies/`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_codegen_ast_structure_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_import_policy_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_builtin_policy_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_name_resolution_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_attribute_access_strategy_py_task.md`
- EXIT_GATE: the validator strategy family is fully ticketed and ready to
  implement.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any strategy boundary proves
  artificial during implementation.

## Requirements (Functional)
- Implement AST structure validation strategy.
- Implement import policy validation strategy.
- Implement builtins policy validation strategy.
- Implement name-resolution validation strategy.
- Implement attribute-access validation strategy.

## Requirements (Non-Functional)
- Keep strategies cohesive and non-overlapping.
- Avoid one fallback "misc strategy" bucket.

## Scope Boundaries
- In scope:
  - validation strategies only
- Out of scope:
  - validator orchestration
  - namespace policies
  - execution

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the validation strategy family is explicit enough to stage
  separately from the validator wrapper.

## Dependencies / Related Work
- `tickets/stories/2026-04-25_codegen_system_validation_directory_story.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-implement-codegen-ast-structure-strategy-py - implement structural AST checks
- [ ] Task: TASK-2026-04-25-implement-codegen-import-policy-strategy-py - implement import policy checks
- [ ] Task: TASK-2026-04-25-implement-codegen-builtin-policy-strategy-py - implement builtins policy checks
- [ ] Task: TASK-2026-04-25-implement-codegen-name-resolution-strategy-py - implement namespace name checks
- [ ] Task: TASK-2026-04-25-implement-codegen-attribute-access-strategy-py - implement attribute access checks
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Every planned validation strategy file has a task.
- Strategy responsibilities are distinct and non-overlapping.

## Validation / Test Plan
- Focused strategy tests plus validator integration tests.

## UX / API / Data Notes
- Strategies are internal only and are consumed by `CodegenValidator`.

## Risks / Mitigations
- Risk: strategy boundaries get blurred and duplicate checks.
  Mitigation: keep one specific rule family per file.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether builtins policy and name resolution stay separate if both touch
  namespace-exposed symbols.

## Decision Log
- 2026-04-25: validation strategies stay as a separate directory and story.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_validation_strategies/architecture_patch.md
  - system_docs/patches/active/codegen_validation_strategies/component_patch_codegen_validation_strategies.md
  - system_docs/patches/active/codegen_validation_strategies/component_patch_codegen_validator_strategy_wiring.md
  - system_docs/patches/active/codegen_validation_strategies/code_description_patch_codegen_validation_strategy_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the first strategy slice is merged into canonical
  docs or intentionally superseded.

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: The strategy family should follow the actual rule axes already agreed:
    structure, imports, builtins, name resolution, and attribute access.
  EVIDENCE:
  - user_instruction: agreement on validator strategies and deeper layout
  IMPACT: The validator file can stay small and orchestration-focused.
  NEXT: stage the five strategy tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: The first strategy slice will implement all five staged files because
    they are one coherent validator-policy family and the current validator is
    still too weak to govern codegen meaningfully.
  EVIDENCE:
  - system_docs/patches/active/codegen_validation_strategies/architecture_patch.md:1-24
  - system_docs/patches/active/codegen_validation_strategies/component_patch_codegen_validation_strategies.md:1-16
  IMPACT: This slice is the next best governance tranche after execution.
  NEXT: implement the strategy files and wire `CodegenValidator` to consume them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: FACT
  CLAIM: The validation-strategy slice is now implemented. The validator now
    composes five real rule-family files:
    AST structure, import policy, builtin policy, name resolution, and
    attribute access. Name resolution now allows locally assigned names so the
    validator still matches normal agent coding style while rejecting unknown
    namespace reads.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py:1-82
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:1-78
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:1-96
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:1-73
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_attribute_access_strategy.py:1-56
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:1-127
  IMPACT: Validation is now materially governed instead of only syntax-aware.
  NEXT: move to observability or broaden builtins/namespace policy later if needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: MEASURE
  CLAIM: The focused codegen ring is green after the validation-strategy slice landed.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_attribute_access_strategy.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_result.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `27 passed, 105 deselected`
  IMPACT: The strategy family is stable enough to hand off to the next subsystem slice.
  NEXT: ask whether to continue directly into observability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the validation strategy directory beneath the validator.
