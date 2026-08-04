# Epic: Redesign Phase Scheduler Queue-Ordered Execution

## Metadata
- Epic ID: EPIC-2026-06-03-redesign-phase-scheduler-queue-ordered-execution
- Status: ready
- Owner: codex
- Agent Name: compiler_0
- Priority: p1
- Created: 2026-06-03T11:43:53Z
- Updated: 2026-06-03T11:43:53Z
- Target Window: 2026-Q3
- Related Program/Initiative: compiler throughput and runtime coordination simplification

## Problem / Opportunity
This epic captures a user-directed redesign lane for the phase scheduler.

The current hypothesis is:
- barrier synchronization is too heavy
- ordered queue-driven work dispatch with event-style tickets would be simpler
  and faster
- fail-fast behavior should stop accepting or processing further queued work as
  soon as one phase error occurs
- threads should park on queue or event work instead of converging repeatedly
  at a barrier

This epic is intentionally being created without reading the implementation
first. It is a planning lane and problem statement, not a source-backed
diagnosis yet.

## MRP Alignment (Most Reasonable Product)
The MRP is not "rewrite threading because barriers feel bad."

The MRP is:
- prove the current scheduler responsibilities clearly
- replace barrier-heavy phase synchronization with a queue-ordered execution
  model if the evidence supports it
- preserve deterministic phase ordering and failure semantics
- make cancellation, stop-the-world failure handling, and thread parking
  simpler and cheaper

The core idea is that ordering should come from the queue and event tickets
rather than repeated barrier rendezvous.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a side epic for a future phase
  scheduler redesign and explicitly said not to read code for the epic-creation
  step.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/synchronization/`
  - scheduler callers in compiler/runtime orchestration paths
  - `codex/context_compass/tickets/epics/backlog/`
- DEPENDENCIES:
  - future source investigation of the current scheduler
  - current compiler exploration program
  - scheduler-related tests and benchmark surfaces once investigation begins
- EXIT_GATE:
  - current scheduler responsibilities are source-backed
  - queue-ordered replacement architecture is explicit
  - failure, cancellation, parking, and ordering semantics are explicit
  - rollout and validation strategy are explicit
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the future investigation
  shows the barrier is not the real dominant cost or if queue-ordering would
  break required semantics.

## Goals (Outcomes)
- Define a simpler phase scheduler architecture.
- Move coordination from barrier-heavy synchronization toward queue-ordered
  work and parked thread events if evidence supports it.
- Preserve deterministic phase order while reducing unnecessary synchronization
  overhead.
- Make fail-fast shutdown behavior explicit and robust.

## Non-Goals (Explicit Exclusions)
- No implementation in this ticket.
- No claim yet that the barrier is definitely the bottleneck.
- No scheduler rewrite before investigation and acceptance of the design.
- No compiler redesign bundled into the scheduler lane by default.

## Scope Boundaries
- In scope:
  - scheduler architecture
  - queue vs barrier coordination model
  - failure and cancellation semantics
  - thread parking and wakeup model
  - deterministic phase ordering
- Out of scope:
  - unrelated compiler strategy work
  - unrelated runtime storage or meld work
  - unbounded concurrency redesign outside scheduler responsibilities

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the user explicitly requested a side epic to capture the
  scheduler redesign idea before investigation begins.

## Success Metrics
- One explicit source-backed design explains why the current scheduler should
  or should not move away from barriers.
- One explicit replacement model covers queue ordering, wakeups, fail-fast
  stopping, and thread lifecycle.
- Future validation can compare coordination overhead before and after the
  redesign.

## Requirements (Functional + Non-Functional)
- Preserve deterministic phase sequencing.
- Preserve explicit fail-fast semantics when one error invalidates the phase
  run.
- Support clean queue shutdown and blocked-thread release on error.
- Support cheap parked waiting instead of repeated barrier convergence if that
  redesign is adopted.
- Keep cancellation and stop semantics comprehensible and auditable.
- Keep the design benchmarkable.

## Constraints / Assumptions
- This epic is hypothesis-first and intentionally not yet source-backed.
- The future redesign must still respect no-GIL threaded reality and
  thread-safety requirements.
- Scheduler semantics matter more than local micro-optimizations.

## Dependencies / External References
- Current compiler exploration lane for larger performance context.
- Future tests and benchmarks for scheduler comparison.

## Milestones (Track Progress)
- [ ] Milestone 1: Current scheduler responsibilities and costs are
  source-backed.
- [ ] Milestone 2: Queue-ordered scheduler design is explicit.
- [ ] Milestone 3: Failure and cancellation semantics are explicit.
- [ ] Milestone 4: Validation and rollout strategy are explicit.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-03-phase-scheduler-current-state
  Read and document the current scheduler and its callers.
- [ ] Story: STORY-2026-06-03-phase-scheduler-queue-design
  Design the queue-ordered replacement model.
- [ ] Story: STORY-2026-06-03-phase-scheduler-failure-semantics
  Define fail-fast queue stop, wakeup, and cancellation behavior.
- [ ] Story: STORY-2026-06-03-phase-scheduler-validation-plan
  Define benchmarks, tests, and rollout strategy.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Keep this lane separate from active compiler strategy work until
  the future scheduler investigation starts.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The current scheduler is understood from source.
- The redesign decision is evidence-backed.
- If adopted, the queue-ordered scheduler design is concrete enough to
  implement without guessing.
- Validation criteria clearly compare ordering, failure, cancellation, and
  coordination overhead.

## Risks / Mitigations
- Risk: barrier overhead is blamed for costs caused elsewhere.
  - Mitigation: future investigation must separate scheduler overhead from
    compiler work cost.
- Risk: queue-ordering simplifies throughput but weakens correctness.
  - Mitigation: deterministic ordering and fail-fast semantics stay
    non-negotiable.
- Risk: redesign broadens into generic threading churn.
  - Mitigation: keep the lane explicitly scheduler-scoped.

## Applicable Anti-Patterns
- [ ] No scheduler rewrite from intuition alone.
- [ ] No performance claims without comparison measurements.
- [ ] No weakening of failure semantics in the name of speed.

## Validation / Test Approach
- Not run.
- This epic is design capture only.
- Future validation should compare:
  - scheduling overhead
  - deterministic order preservation
  - failure-stop behavior
  - thread parking behavior
  - cancellation responsiveness

## Rollout / Adoption Plan
- Investigate current scheduler first.
- Decide whether queue-ordering is truly the right convergence target.
- If yes, design the replacement fully.
- Then implement in bounded slices with benchmarks and tests.

## Open Questions
- Is the barrier actually the dominant coordination cost?
- Which current semantics depend on barrier-wide synchronization?
- Can queue tickets encode enough phase-order information cleanly?
- How should fail-fast draining interact with already-running work?

## Decision Log
- This epic exists to capture the scheduler redesign idea early without
  pretending it is already source-backed.
- Future work should treat queue-ordering as a serious candidate, not a fixed
  conclusion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-06-03T11:43:53Z
  TYPE: HYPOTHESIS
  CLAIM: Replacing barrier-centric phase coordination with queue-ordered work
    and parked thread events may lower overhead and produce simpler fail-fast
    behavior, but this is not source-backed yet and must be investigated before
    design is locked.
  IMPACT: This creates a future lane for scheduler convergence without mixing
    it into the active compiler exploration lane prematurely.
  NEXT: Leave this epic in backlog until a dedicated scheduler investigation
    starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: scheduler architecture, synchronization semantics, and rollout
  tradeoffs.
- Add notes only after source investigation begins.
- Keep unsupported performance claims marked as hypothesis or unknown until
  measured.

## Context / Handoff Summary
This is a side epic parked in backlog. It captures the user-requested idea of
replacing barrier-heavy phase scheduling with a queue-ordered, fail-fast,
thread-parking model, but it intentionally does not pretend that idea is
source-backed yet.
