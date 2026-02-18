# Epic: Skill-Gate-First Compaction Measurement Loop

## Metadata
- Epic ID: EPIC-2026-02-18-skill-gate-first-compaction-measurement-loop
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T17:07:51Z
- Target Window: 2026-Q1
- Related Program/Initiative: Compaction Fidelity Convergence

## Problem / Opportunity
Current compaction measurement behavior can report parity-style `fidelity_diff`
rows without requiring a full scored test cycle. This allows non-empirical
“knowledge retained” claims that do not prove performance against the generated
question set.

The opportunity is to make post-compaction success score-grounded:

1. Run a minimum skill-gate onboarding.
2. Submit blind answers.
3. Grade against answer keys.
4. Record real misses.
5. Relearn only failed docs.
6. Reduce cycle read/test volume over time through stability-based shrinking.

## MRP Alignment (Most Reasonable Product)
The durable core is a deterministic measurement-and-relearn loop that produces
real scores and progressively lowers reread volume while preserving safety
sentinels. This avoids fragile attestation-based “success” and improves
compaction reliability over repeated cycles.

## Ticket Contract
- ENTRY_GATE: user approved shift to score-grounded compaction success model and
  requested epic/story/task routing before further implementation.
- EXECUTION_BOUNDARY: `skill_check/`, compaction onboarding docs, differential
  board docs, generator/evaluator workflows, ticketing/board artifacts.
- DEPENDENCIES: `skill_check/skill_check_policy.md`,
  `compacting_differential_board.md`, `compaction_diff_onboarding.md`, current
  manifest/test artifacts.
- EXIT_GATE: discovery story accepted and implementation task set sequenced with
  explicit scoring, relearn, and shrink contracts.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` on schema incompatibilities that
  break historical rows or certification gating.

## Goals (Outcomes)
- Redefine post-compaction success as scored test performance.
- Add explicit `skill_gate_onboard` minimum-read stage before testing.
- Enforce blind-answer anti-cheat and graded evidence as mandatory.
- Implement targeted failed-doc relearn.
- Drive smaller cycles over time using stability streaks and P0 sentinels.

## Non-Goals (Explicit Exclusions)
- Runtime business-logic refactors under `src/`.
- Cosmetic changes unrelated to scoring/relearn/shrink loop behavior.

## Scope Boundaries
- In scope:
  - compaction measurement policy/docs and board schema
  - skill-check cycle orchestration and lifecycle rules
  - generator/evaluator behavior for reset + shrink + targeted relearn
- Out of scope:
  - non-compaction workflow redesign
  - unrelated benchmark or codegen optimization lanes

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user directed creation of epic/story/discovery-task lane
  before implementation due imminent compaction risk.

## Success Metrics
- 100% of cycle completion claims include graded `knowledge_test` evidence.
- 0 cycles marked successful with `knowledge_score: Not run`.
- Failed-doc reread sets are recorded and auditable each cycle.
- Question/read volume trends downward for stable docs without policy-gate loss.

## Requirements (Functional + Non-Functional)
- Functional:
  - define and enforce minimum readset skill-gate onboarding
  - capture blind submissions and post-submission grading only
  - persist scored rows and cycle-level metrics
  - regenerate fresh next cycle and prune stale artifacts
  - apply streak-based shrink with permanent P0 sentinels
- Non-Functional:
  - deterministic, auditable cycle state transitions
  - strict anti-cheat compliance
  - no performative score reporting

## Constraints / Assumptions
- Existing historical rows may need compatibility handling.
- Answer-key access sequencing remains strict.
- Policy changes must remain coherent with certification gates.

## Dependencies / External References
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/compacting_differential_board.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/artifacts/2026-02-18_skill_gate_first_compaction_success_model.md`

## Milestones (Track Progress)
- [x] Milestone 1: Capture requested success model in linked artifact.
- [x] Milestone 2: Discovery story completed with concrete change map and
      implementation sequence.
- [x] Milestone 3: Implementation tasks approved and routed.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-18-skill-gate-first-compaction-discovery -
      discovery and task decomposition for score-grounded cycle redesign.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-02-18-skill-gate-onboarding-minimum-readset-discovery
- [x] Task: TASK-2026-02-18-test-scored-fidelity-diff-schema-discovery
- [x] Task: TASK-2026-02-18-failed-doc-targeted-relearn-discovery
- [x] Task: TASK-2026-02-18-cycle-reset-and-adaptive-shrink-discovery
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Discovery story accepted by user with explicit approval to implement.
- Every required change area has a concrete implementation task with
  file-level boundaries.
- Artifact-linked model is reflected in ticket contracts and attention routing.

## Risks / Mitigations
- Risk: naming/schema changes invalidate older board analytics.
  Mitigation: discovery task defines compatibility approach before edits.
- Risk: strict blind-answer flow is bypassed operationally.
  Mitigation: enforce status blocks and explicit anti-cheat attestation fields.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery-phase validation only:
  - schema mapping checks
  - policy contract coherence checks
  - implementation sequencing and dependency review

## Rollout / Adoption Plan
1. Finish discovery tasks and confirm model.
2. Implement in bounded task order (policy -> board schema -> evaluator ->
   generator lifecycle).
3. Run first fully scored cycle and compare against baseline behavior.

## Open Questions
- Should scored row type reuse `fidelity_diff` or move to a clearer label?
- What shrink threshold should be defaulted for stable docs in this lane?

## Decision Log
- Pending discovery outcomes and user approval.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_skill_gate_first_compaction_success_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Notes
- DATETIME: 2026-02-18T16:53:27Z
  TYPE: FACT
  CLAIM: Current differential board semantics prioritize manual
    `fidelity_diff` parity rows while `knowledge_test` remains a separate row
    type, which enables non-scored cycle reporting.
  EVIDENCE:
  - compacting_differential_board.md:47-51
  - compacting_differential_board.md:55-91
  - compacting_differential_board.md:95-119
  IMPACT: Score-grounded success cannot be guaranteed without redesigning the
    cycle contract and row interpretation.
  NEXT: Route discovery story and tasks for each required change area.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Epic scope is implemented: re-entry now enforces skill-gate-first
    minimum reads, score-grounded completion semantics, targeted relearn, and
    single-cycle reset/shrink maintenance.
  EVIDENCE:
  - AGENTS.MD:59-61
  - agent_onboarding/default/general/skills/compaction_requirements.md:61-185
  - skill_check/skill_check_policy.md:21-26
  - compacting_differential_board.md:107-109
  - skill_check/generate_bootstrap_suite.py:270-329
  IMPACT: Epic is technically complete and awaiting user acceptance for closure.
  NEXT: request acceptance confirmation and close/move tickets when approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic implementation is complete and in review; closure is blocked only on user
acceptance confirmation per ticket policy.
