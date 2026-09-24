# Epic: Improve override execution performance without weakening creation contracts

## Metadata
- Epic ID: EPIC-2026-09-24-override-execution-performance
- Status: in_progress
- Owner: user
- Agent Name: updater_1
- Priority: p1
- Created: 2026-09-24T09:27:42Z
- Updated: 2026-09-24T09:48:20Z
- Target Window: Investigation first; implementation after owner review.
- Related Program/Initiative: Melder runtime performance.

## Problem / Opportunity
The owner reports override creation at roughly 20% of normal creation throughput and asks for a
controlled comparison based on the existing shallow and override benchmark suites. This ratio is
an observation to reproduce, not an established measurement for the current checkout.

Passing explicit constructor inputs is common in Python. A top-level initialization path such as
init={} may deserve different treatment from general dependency-graph overrides. Its API and
implementation remain open questions; first establish comparable workloads and measure the gap.

## MRP Alignment (Most Reasonable Product)
Improve the common constructor-input path while preserving dependency selection, scoped creation,
override isolation, hooks, cleanup and concurrency. Optimize demonstrated costs without creating
parallel inconsistent resolution semantics or slowing ordinary creation.

## Ticket Contract
- ENTRY_GATE: Certified updater_1; discovery task routed on the attention board.
- EXECUTION_BOUNDARY: Benchmark experiments and source investigation are authorized now. Production
  API changes, compiler changes and release/build generation follow a reviewed implementation decision.
- DEPENDENCIES: Existing shallow/override benchmark workloads and current Melder runtime contracts.
- EXIT_GATE: Measured diagnosis, agreed design, accepted implementation and regression/performance evidence.
- FAILURE_ESCALATION: Record incomparable workloads, unstable measurements or unresolved semantics explicitly.

## Goals (Outcomes)
- Measure normal creation and override execution with one Melder-only experiment and shared timing rules.
- Separate top-level constructor input cost from nested override targeting and mixed override work.
- Identify which costs arise in public argument normalization, targeting, planning and execution.
- Compare improvements to existing overrides against a distinct top-level init={} API.
- Implement the selected design only after investigation and owner review of concrete evidence.

## Non-Goals (Explicit Exclusions)
- Benchmark competitor libraries, redesign unrelated subsystems, or change production code in discovery.
- Assume the reported throughput ratio or promise a speedup before measurements exist.
- Treat the spelling init={} as an approved public API.

## Scope Boundaries
- In scope: Supplied benchmark models, Melder-only experimentation, override hot paths and relevant tests.
- Out of scope now: Production implementation, packaged assets and unrelated concurrent cache work.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner explicitly requested an epic and a first unified performance experiment.

## Success Metrics
- Reproducible command, Python/GIL/version/source provenance and repeated timing samples.
- Per-case median latency, throughput, spread and override throughput relative to normal creation.
- Equal creation/lifetime contracts and explicit accounting when supplied inputs replace work.
- No numerical performance claim without local run evidence.
- Later implementation: preserved behavior and measured gains with ordinary-creation regression checks.

## Requirements (Functional + Non-Functional)
- Use the two supplied benchmark files as the starting workloads, limiting execution to Melder.
- Keep setup, correctness assertions and teardown outside steady-state timing.
- Measure warm execution separately from initial preparation; control repeat order and garbage collection.
- Preserve raw results so another session can reproduce and investigate the measured differences.
- Make the experiment opt-in and configurable; no flaky wall-time pass/fail threshold in normal tests.

## Constraints / Assumptions
- Initial automatic measurements reproduce 20-25% throughput on the supplied graph override shapes.
- Source may change concurrently in another agent's cache-release lane; record source fingerprints.
- Caller-supplied input semantics and nested overrides must remain distinguishable in comparisons.

## Dependencies / External References
- benchmarks/testing_other_di/test_shallow_all.py
- benchmarks/testing_other_di/test_overrides_all.py
- tests/experimentation/

## Milestones (Track Progress)
- [x] Establish comparable Melder-only baseline measurements.
- [ ] Trace measured overhead and evaluate design alternatives, including separate top-level inputs.
- [ ] Agree the runtime/API design and patch contracts with the owner.
- [ ] Implement and qualify the chosen optimization.

## Stories (Required to Complete)
- Investigation determines implementation story boundaries; none is activated before baseline evidence.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] TASK-2026-09-24-measure-melder-creation-and-overrides:
  tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md

## Acceptance Criteria (Epic Done)
- The reported gap is reproduced or corrected with explicit workload/runtime evidence.
- A root-cause account separates top-level constructor arguments from general graph override behavior.
- The selected change preserves contracts and has reproducible performance/regression evidence.
- Owner accepts the resulting behavior and documentation before epic closure.

## Risks / Mitigations
- Unequal work can produce misleading ratios: report constructed/supplied object semantics per case.
- Microbenchmark noise: warm up, repeat, rotate case order, retain spread and environment details.
- API fragmentation: prefer shared invariants and explain any separate execution path with evidence.

## Applicable Anti-Patterns
- [ ] No speed claim from unlike workloads or a single timing sample.
- [ ] No runtime implementation before the evidence/design decision.
- [ ] No competing harness tracking or automatic delegation.

## Validation / Test Approach
The first task verifies experiment outcomes before timing, then runs repeated Melder measurements.
Later changes require behavioral regressions and matched performance comparisons; coverage is not inferred.

## Rollout / Adoption Plan
Baseline -> bounded profiling/source investigation -> owner design review -> implementation -> qualification.

## Open Questions
- Which override shapes explain the largest measured cost?
- How much comes from normalization/target selection versus generated execution?
- Can current overrides specialize root arguments, or should a distinct init={} surface express that intent?
- What are the conflict, optional-argument, hook and caching rules if both input mechanisms coexist?

## Decision Log
- 2026-09-24: Owner authorized epic creation and a unified Melder-only experiment before runtime changes.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: Measurement artifacts belong to the discovery task.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner-directed disposition at epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Override throughput, top-level constructor input and execution specialization.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-24T09:27:42Z
  TYPE: DECISION
  CLAIM: Begin with the owner's supplied shallow/override benchmarks and one unified Melder-only
    experiment. A possible init={} API remains a design hypothesis, not an implementation instruction.
  EVIDENCE:
  - Owner's current epic-first experimentation request and supplied benchmark paths.
  IMPACT: Establish comparable measurements before attributing cost or changing runtime behavior.
  NEXT: Execute the linked measurement task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user.
- [ ] Acceptance criteria confirmed by user.
- [ ] Board and artifact state synchronized.

## Noting Behavior
Record program direction and design decisions here; detailed measurements and source findings stay in tasks.

- DATETIME: 2026-09-24T09:48:20Z
  TYPE: MEASURE
  CLAIM: The first experiment reproduces 20-25% normal throughput for automatic graph overrides.
    Reusing payloads does little; even all supplied deep root dependencies still trigger all 511
    constructor calls. Dynamic measurements and positional/DI rejection observations are also retained.
  EVIDENCE:
  - tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md
  - artifacts/override_execution_performance_20260924/findings.md
  IMPACT: Investigate the generated override execution path and eager descendants before choosing
    whether root inputs should specialize existing overrides or use a distinct init={} contract.
  NEXT: Trace the many-only override executor's root-input work and observable pruning constraints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Epic created first; the unified Melder-only experiment and automatic/dynamic baseline are delivered
for review under the linked task. Read its findings artifact. Next investigate generated override
execution and unnecessary descendant construction. No production optimization or init={} API yet.
