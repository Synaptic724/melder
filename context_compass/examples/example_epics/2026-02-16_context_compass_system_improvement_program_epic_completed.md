

Completed: 2026-02-17T11:57:04Z
Summary: Closed by explicit user directive to close all currently open tickets.

# Epic: Context Compass System Improvement Program

## Metadata
- Epic ID: EPIC-2026-02-16-context-compass-system-improvement-program
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16T21:30:00Z
- Updated: 2026-02-17T11:57:04Z
- Target Window: 2026-Q2
- Related Program/Initiative: Context Compass Core Reliability and Evolution

## Problem / Opportunity
`context_compass` is policy-rich and operationally mature, but it lacks a single,
current program epic that:
- maps the system abstractly end-to-end in one place,
- defines a shared improvement rubric for prioritization,
- and drives flat-file-safe enhancement execution as a continuous program.

## MRP Alignment (Most Reasonable Product)
The MRP is a durable improvement program that keeps the existing local
text/flat-file operating model while improving clarity, consistency, and
execution effectiveness.

This epic prioritizes:
- system understanding first,
- evidence-based opportunity scoring second,
- implementation of high-value improvements third.

## Ticket Contract
- ENTRY_GATE: epic lane is routed and story set is defined with IDs.
- EXECUTION_BOUNDARY: context_compass process/docs/ticketing surfaces only.
- DEPENDENCIES: story lanes and policy anchors listed in this epic.
- EXIT_GATE: required stories accepted and closure sync completed.
- FAILURE_ESCALATION: cross-story conflicts are raised as `DECISION_REQUEST` or
  `CONFLICT`.

## Abstract System Definition
At an abstract level, `context_compass` operates as a documentation-native
control plane:
- `attention_board.md` routes active work.
- `tickets/epics/`, `tickets/stories/`, and `tickets/tasks/` hold durable execution memory.
- `WORKFLOW.md` defines ticket lifecycle and microcycle execution gates.
- `agent_onboarding/` defines policy/certification and behavioral standards.
- `system_docs/src_architecture.md` and
  `system_docs/src_components.md` provide re-entry-safe system context.

## Goals (Outcomes)
- Produce a current abstract map of how `context_compass` works.
- Define a robust rubric for scoring improvement opportunities.
- Use rubric outputs to prioritize and execute enhancements.
- Keep all improvements compatible with local text-based flat-file workflows.

## Non-Goals (Explicit Exclusions)
- Replacing ticket/docs workflows with external databases or SaaS tooling.
- Introducing binary-only planning artifacts.
- Broad repository refactors outside context_compass scope.

## Scope Boundaries
- In scope:
- `context_compass` process/docs/ticketing architecture and improvement planning.
- Rubric design, scoring, and prioritized enhancement backlog generation.
- Flat-file-safe enhancement tasks and implementation follow-ons.
- Out of scope:
- Unrelated runtime/library optimization work outside `context_compass`.
- Migration from markdown/ticket workflows to non-text state systems.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user requested closing all tickets as done.
  story/task lanes were opened.

## Success Metrics
- Story 1 delivers an evidence-backed abstract system map.
- Story 2 delivers a weighted rubric and scored opportunity register.
- Ticket design and cross-system interaction model is documented with lifecycle
  transitions and execution gates.
- At least one prioritized enhancement tranche is ready for execution with
  explicit acceptance criteria.

## Requirements (Functional + Non-Functional)
- Functional:
  - Define abstract system behavior, boundaries, and operating flows.
  - Define and document a multi-dimension improvement rubric.
  - Score improvement opportunities and prioritize implementation order.
- Non-functional:
  - Maintain flat-file, text-first workflows.
  - Keep all claims evidence-backed or explicitly UNKNOWN.
  - Keep artifacts compaction-safe and resume-friendly.

## Constraints / Assumptions
- Constraints:
  - Ticket microcycle gates remain mandatory.
  - Unknowns gate remains mandatory.
  - Existing documentation-first workflow remains canonical.
- Assumptions:
  - Current context_compass artifacts are sufficient to build a first scoring
    rubric without external tooling.

## Dependencies / External References
- `context_compass/README.md`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/default/general/skills/workflow.md`
- `context_compass/agent_onboarding/default/general/skills/attention_board.md`
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/agent_onboarding/default/general/skills/context_protocol.md`
- `context_compass/agent_onboarding/default/general/skills/ticketing.md`
- `context_compass/agent_onboarding/default/general/skills/unknowns_gate_reference.md`
- `context_compass/agent_onboarding/default/general/policies/ctx_autonomy_policy.md`

## Milestones (Track Progress)
- [x] Milestone 1: Abstract system map finalized and reviewed.
- [x] Milestone 2: Rubric defined with weights, scoring rules, and examples.
- [x] Milestone 3: Opportunity register scored and prioritized.
- [x] Milestone 4: First enhancement tranche specified for execution.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-16-context-compass-abstract-system-mapping - Map how context_compass works abstractly and document operating model.
- [x] Story: STORY-2026-02-16-context-compass-improvement-rubric-and-opportunity-investigation - Design rubric, score opportunities, and prepare enhancement tranche.
- [x] Story: STORY-2026-02-16-context-compass-ticket-design-and-system-interaction-model - Define ticket design contract, lifecycle state machine, and system interaction model.
- [x] Story: STORY-2026-02-16-context-compass-artifact-store-and-pointer-protocol - Define artifact store, pointer protocol, and closure cleanup rules.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-16-context-compass-abstract-system-mapping.
- [x] Task: Complete story STORY-2026-02-16-context-compass-improvement-rubric-and-opportunity-investigation.
- [x] Task: Complete story STORY-2026-02-16-context-compass-ticket-design-and-system-interaction-model.
- [x] Task: Complete story STORY-2026-02-16-context-compass-artifact-store-and-pointer-protocol.
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.
- [x] Task: Keep attention-board routing synchronized with active story/task.

## Acceptance Criteria (Epic Done)
- Abstract system map exists with concrete boundaries, flows, and responsibilities.
- Rubric includes dimensions, weights, scoring scale, and decision rules.
- Opportunity register is ranked and tied to concrete follow-on work.
- User confirms this improvement program and first tranche acceptance criteria.

## Risks / Mitigations
- Risk: rubric becomes too theoretical and not actionable.
  Mitigation: require direct mapping from rubric scores to prioritized tasks.
- Risk: improvement scope drifts into non-context_compass domains.
  Mitigation: enforce strict scope boundaries in story/task definitions.
- Risk: enhancements accidentally undermine flat-file workflow.
  Mitigation: include flat-file compatibility checks in every acceptance set.

## Applicable Anti-Patterns
- [x] No epic-state changes without story/task evidence.
- [x] No closure while required stories are incomplete or unaccepted.
- [x] No program-level claims without ticket-note evidence pointers.

## Validation / Test Approach
- Documentation validation via evidence-backed notes and consistency checks
  against `README.md`, `SKILLS.MD`, and `WORKFLOW.md`.
- Process validation via ticket microcycle and attention-board routing updates.
- Implementation validation for follow-on tasks: explicit test/report status
  with truthful "Not run" reporting where applicable.

## Rollout / Adoption Plan
- Execute Story 1 first to produce shared abstract model.
- Execute Story 2 next to define rubric and prioritize opportunities.
- Open implementation tasks from top-ranked opportunities.
- Run small, reviewable enhancement tranches with ticketed evidence.

## Open Questions
- Which rubric dimensions should be weighted highest for near-term wins?
- How many enhancement slices should be in the first implementation tranche?
- Which existing docs need immediate harmonization after abstract mapping?

## Decision Log
- 2026-02-16: Epic opened to run a dedicated context_compass improvement program.
- 2026-02-16: Program order set to mapping first, rubric/opportunity second.

## Noting Behavior
- Focus notes on program direction, cross-story sequencing, and tranche
  tradeoffs.
- Reference story/task evidence for tactical details.
- Keep notes append-only and UNKNOWN-first.

## Notes
- DATETIME: 2026-02-16T21:30:00Z
  TYPE: DECISION
  CLAIM: This epic preserves the repository's flat-file control-plane model while introducing structured improvement planning.
  EVIDENCE: context_compass/README.md:5-10, context_compass/SKILLS.MD:5-57, context_compass/agent_onboarding/default/general/skills/workflow.md:30-37
  IMPACT: Improvement work can proceed without changing canonical storage/workflow surfaces.
  NEXT: Execute Story 1 and capture an evidence-backed abstract system map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T21:59:00Z
  TYPE: MEASURE
  CLAIM: First implementation tranche under this epic delivered board schema upgrades (`mode/outcome/exit_signal`, `SWITCH_TRIGGER`, `RESUME_HIERARCHY`) and DateTime-default standardization for templates and active policy artifacts.
  EVIDENCE: context_compass/tickets/tasks/2026-02-16_attention_board_resume_hierarchy_switch_trigger_schema_task.md:1-52, context_compass/tickets/tasks/2026-02-16_datetime_default_standardization_task.md:1-55, context_compass/agent_onboarding/default/general/skills/attention_board.md:15-30
  IMPACT: Core context-compass coordination surfaces now expose richer tactical continuity while preserving compact board semantics and defaulting new work to DateTime.
  NEXT: Confirm acceptance and decide whether to open a full historical DateTime migration follow-on task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T21:02:09Z
  TYPE: DECISION
  CLAIM: Added a dedicated artifact-protocol story to define artifact board
    indexing, ticket pointer standards, and closure cleanup behavior while
    keeping `attention_board.md` ticket-only.
  EVIDENCE:
  - context_compass/tickets/stories/2026-02-16_context_compass_artifact_store_and_pointer_protocol_story.md:1-115
  - context_compass/artifacts/README.md:1-30
  IMPACT: Artifact handling is now a first-class improvement lane instead of
    ad-hoc ticket prose.
  NEXT: Execute the first artifact task and wire protocol sections across docs
    and templates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T21:11:28Z
  TYPE: MEASURE
  CLAIM: Artifact protocol story delivered all three implementation tasks to
    review state in one pass.
  EVIDENCE:
  - context_compass/tickets/stories/2026-02-16_context_compass_artifact_store_and_pointer_protocol_story.md:113-124
  - context_compass/tickets/tasks/2026-02-16_artifact_board_and_store_contract_task.md:5-7
  - context_compass/tickets/tasks/2026-02-16_ticket_artifact_pointer_template_and_policy_task.md:5-7
  - context_compass/tickets/tasks/2026-02-16_artifact_lifecycle_cleanup_and_closure_sync_task.md:5-7
  IMPACT: Program now includes a concrete artifact-handling subsystem ready for
    acceptance review.
  NEXT: Walk through artifact protocol deliverables with user and decide closure
    vs refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
New improvement program epic created for context_compass. Active execution is
routed to the first story (abstract system mapping). The second story (rubric
and opportunity investigation) is pre-scoped and ready once story 1 outcomes
are documented.







