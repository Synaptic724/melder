# Epic: Investigate Spellspace Benchmark Measurement And Optimization
- Completed: 2026-05-16T16:41:00Z
- Summary: Closed at user direction after the benchmark split and focused
  Melder-only spellspace experiment established the measurement boundary and
  narrowed the follow-on optimization target.

## Metadata
- Epic ID: EPIC-2026-04-29-spellspace-benchmark-measurement-and-optimization
- Status: done
- Owner: codex
- Agent Name: codex_01
- Priority: p0
- Created: 2026-04-29T22:54:23Z
- Updated: 2026-05-16T16:41:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder performance hardening and benchmarking credibility

## Problem / Opportunity
The current DI benchmark lane shows Melder close to competing libraries on many
single-resolution shapes, but the `spellspace` path is still materially slower.
The user specifically suspects the benchmark is measuring work that competing
libraries keep outside the timed window, especially spellspace creation-cycle
costs, and wants an evidence-backed discovery pass before any optimization work
is proposed.

## MRP Alignment (Most Reasonable Product)
The MRP is not "win every microbenchmark at any cost." The MRP is to make
Melder's benchmark story honest, explainable, and performant enough that the
system's extra runtime semantics are not paying accidental measurement tax.

## Ticket Contract
- ENTRY_GATE: active benchmarking concern is explicitly routed from `attention_board.md`
  and the benchmark file plus spellspace runtime path are identified.
- EXECUTION_BOUNDARY: discovery only for benchmark methodology and spellspace
  runtime cost attribution across:
  - `benchmarks/testing_other_di/`
  - Melder spellspace/meld/conduit/runtime files directly involved in the path
- DEPENDENCIES:
  - `benchmarks/testing_other_di/test_shallow_all.py`
  - Melder spellspace, conduit, meld, and creation code paths
  - current benchmark expectations for dishka / dependency-injector comparisons
- EXIT_GATE: the measured spellspace path is restated concretely, the likely
  cost contributors are identified with evidence, and the next optimization or
  benchmark-isolation stories are explicit.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the benchmark semantics prove
  too mixed to separate "spellspace runtime cost" from "benchmark harness cost"
  without redesigning the benchmark lane.

## Goals (Outcomes)
- Determine exactly what `test_shallow_all.py` measures for Melder spellspace.
- Determine whether spellspace creation/enter/cleanup is inside the timed path.
- Compare that measurement window to the other DI libraries in the same bench.
- Identify the highest-confidence next slices for benchmark correction and
  spellspace optimization.

## Non-Goals (Explicit Exclusions)
- Immediate optimization patches.
- Rewriting the whole benchmark suite in this epic.
- Broader Melder performance work unrelated to the spellspace path.

## Scope Boundaries
- In scope:
  - benchmark discovery
  - runtime-path tracing
  - timing-window attribution
  - story/task staging for follow-on work
- Out of scope:
  - landing runtime optimizations blindly
  - broad DI-container comparison claims beyond the relevant measured path

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an epic and a discovery pass
  focused on whether spellspace creation-cycle work is unfairly inside Melder's
  measured benchmark window.

## Success Metrics
- The timed spellspace path is reconstructed from benchmark source and runtime code.
- At least one evidence-backed explanation exists for the current spellspace gap.
- The next follow-on slices are concrete enough to implement without guessing.

## Requirements (Functional + Non-Functional)
- Functional:
  - read the benchmark implementation
  - trace the Melder spellspace code path
  - compare measurement boundaries with competing libraries
  - capture findings in notes with exact evidence
- Non-functional:
  - no unverified benchmark claims
  - no optimization proposals without measurement-path evidence
  - preserve the distinction between benchmark semantics and runtime semantics

## Constraints / Assumptions
- The user already suspects creation-cycle work is inside Melder's timed path.
- Melder's extra semantics may still cost more even after measurement cleanup.
- This epic should prefer direct code evidence over benchmark folklore.

## Dependencies / External References
- `benchmarks/testing_other_di/test_shallow_all.py`
- Melder spellspace/conduit/meld/runtime files in the active trace

## Milestones (Track Progress)
- [ ] Milestone 1: reconstruct the benchmark timing window for Melder spellspace
- [ ] Milestone 2: identify cost contributors and next optimization/isolation slices

## Stories (Required to Complete)
- [ ] Story: benchmark timing-window attribution for Melder spellspace
- [ ] Story: spellspace runtime cost decomposition and follow-on optimization plan

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: read `test_shallow_all.py` and document the exact spellspace benchmark flow
- [ ] Task: trace spellspace creation/entry/cleanup/runtime code for the measured path
- [ ] Task: compare Melder's measured window with dishka and dependency-injector semantics
- [ ] Task: complete `TASK-2026-04-29-split-spellspace-benchmark-metrics`
- [ ] Task: complete `TASK-2026-04-29-experiment-melder-spellspace-cycle-metrics`
- [ ] Task: verify Ticket Microcycle enforcement across active notes during discovery

## Acceptance Criteria (Epic Done)
- The current spellspace measurement path is explained with source evidence.
- The likely benchmark/harness vs runtime cost split is explicit.
- Follow-on implementation/discovery slices are staged clearly.

## Risks / Mitigations
- Risk: the benchmark code mixes setup and timed execution too tightly.
  Mitigation: document the exact boundary first before prescribing changes.
- Risk: Melder's extra semantics are genuinely more expensive even after cleanup.
  Mitigation: keep the goal on honesty and bounded optimization, not on forced parity.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No benchmark-performance claims without direct timing-path evidence.

## Validation / Test Approach
- Discovery-first.
- Validation will come from code-path reconstruction and, if needed later,
  targeted benchmark reruns under a follow-on story/task.

## Rollout / Adoption Plan
- First clarify the measurement path.
- Then isolate benchmark-window issues versus real runtime costs.
- Then stage focused optimization work if the evidence justifies it.

## Open Questions
- Is `spellspace` paying for creation/entry/cleanup inside the timed window?
- Are competing libraries measuring an equivalent lifecycle surface at all?
- Which Melder sub-steps dominate the current `spellspace` microbench cost?

## Decision Log
- 2026-04-29T22:54:23Z: Opened the epic at the user's request to investigate
  whether Melder spellspace benchmark timing includes work that peer libraries
  exclude from measurement.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-29T22:54:23Z
  TYPE: FACT
  CLAIM: The user wants a dedicated spellspace benchmark discovery lane, not a
    drive-by answer. The central suspicion is that Melder's spellspace timing
    includes creation-cycle work that dishka and dependency-injector keep
    outside their measured path.
  EVIDENCE:
  - user_instruction: "Make an epic and run discovery on this because spellspace shouldn't have its creation cycle mapped into this"
  - user_instruction: "if you look at dishka and dependency-injector and all these other things their build cycle is out of the measuring time I think"
  IMPACT: The next move is a benchmark-window and runtime-path investigation,
    not immediate optimization advice.
  NEXT: read the benchmark file and trace the Melder spellspace code path that
    the benchmark exercises.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T22:58:25Z
  TYPE: FACT
  CLAIM: The current benchmark helper times the full scope-cycle helper for
    every library, not just the cached second resolve. Dependency-injector
    creates a fresh `contextvars.Context` and runs the scope body inside it;
    Dishka creates a fresh request container; Injector enters its custom scope;
    and Melder enters a real `SpellSpace`. So a pure "inside active scope"
    metric would require a split benchmark for all libraries, not a Melder-only
    adjustment.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all.py:824-835
  - benchmarks/testing_other_di/test_shallow_all.py:996-1004
  - benchmarks/testing_other_di/test_shallow_all.py:1054-1061
  - benchmarks/testing_other_di/test_shallow_all.py:1138-1145
  - benchmarks/testing_other_di/test_shallow_all.py:1623-1623
  IMPACT: The likely fairness issue is narrower than "only Melder includes
    scope creation." The benchmark currently includes analogous scope entry/exit
    work for all libraries, so the next question is which extra Melder mechanics
    inside `enter_spellspace()` and teardown make its cycle materially heavier.
  NEXT: trace Melder's spellspace object lifecycle and unique-per-spell-space
    create/lookup/cleanup path to isolate the extra per-cycle work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:07:12Z
  TYPE: FACT
  CLAIM: The first benchmark refactor slice is now landed. The benchmark can
    split spellspace timing into build, meld, cached, and total metrics by
    using per-lib spellspace enter/resolve/exit hooks, and the Melder path
    validated locally with the new output shape.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all.py:80-121
  - benchmarks/testing_other_di/test_shallow_all.py:787-789
  - benchmarks/testing_other_di/test_shallow_all.py:1270-1303
  - benchmarks/testing_other_di/test_shallow_all.py:1767-1781
  - validation_result: `$env:PYTHONPATH='src;.'; python -m pytest benchmarks/testing_other_di/test_shallow_all.py::test_single_resolve_timings -q -s` -> Melder single-run split spellspace metrics printed and 5 tests passed
  IMPACT: We now have a benchmark path that excludes spellspace build time from
    the primary spellspace meld metric instead of only reporting whole-cycle
    scope cost.
  NEXT: review the new metric shape, then rerun in the fuller benchmark
    environment where the comparison libraries are installed to capture the
    side-by-side split numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:50:40Z
  TYPE: MEASURE
  CLAIM: The focused Melder-only spellspace experiment reproduces the same
    shape as the benchmark lane: build is ~5us, cached meld is ~1us, cleanup is
    ~2-3.5us, and the real hot seam is the first spellspace meld (~7us solo,
    ~13.8us shallow, ~30.2us depth-3 deep). That means the benchmark harness
    was not inventing the spellspace profile; the heavy first-meld shape is
    native to the current Melder runtime path.
  EVIDENCE:
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-201
  - validation_result: `python tests/experimentation/melder_spellspace_cycle_testbench.py` -> `OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT`
  IMPACT: The next optimization work should focus directly on the first
    `unique_per_spell_space` create/register path and the surrounding spellspace
    lifecycle semantics rather than on more benchmark decomposition.
  NEXT: trace and optimize the first spellspace meld path, then rerun both the
    experiment and the comparison benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when benchmark semantics, timing boundaries, or priority slices change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns discovery on Melder spellspace benchmark semantics and likely
optimization direction. It exists to separate true spellspace runtime cost from
benchmark-harness measurement artifacts before any tuning work is proposed.
