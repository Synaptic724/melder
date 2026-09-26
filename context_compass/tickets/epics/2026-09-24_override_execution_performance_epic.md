# Epic: Plan override-supplied dependencies before object creation

## Metadata
- Epic ID: EPIC-2026-09-24-override-execution-performance
- Status: in_progress
- Owner: user
- Agent Name: updater_0, updater_1, melder_0, melder_1
- Lead Agent: updater_0
- Priority: p1
- Created: 2026-09-24T09:27:42Z
- Updated: 2026-09-25T20:53:31Z
- Target Window: Investigation first; implementation after owner review.
- Related Program/Initiative: Melder runtime performance.

## Problem / Opportunity
The main defect under investigation is structural: the runtime constructs dependencies that a caller
already supplied, then substitutes the supplied values at the consumer's argument sockets. Overriding
three of five dependencies should let execution construct only the two still needed plus the consumer,
subject to other reachable uses. Faster execution of the original full graph does not satisfy that goal.

The preserved emission-only prototype proves avoidable instruction overhead, with 1.64x-4.68x gains
against old override execution. Against normal creation it reaches 41.8% shallow, 53.3% wide, 41.6%
diamond and 95.3% deep throughput. It retains every constructor and is evidence, not the selected fix.
The owner now directs joint discovery of override-aware effective-graph planning and orchestration.

Structural discovery now separates logical override paths from physical constructor sites. Bounded
diagnostics show the expected 6-to-3 and 511-to-1 reductions, preserve shared fan-in and reproduce
native alias failures independently. Lead review exposes a static-prototype defect where runtime reuse
skips a parent but its descendant override still influences another active path. The separate conditional
prototype now handles this under the proposed inactive-path policy, with twenty peer cases and two
independent lead reviews. Native locking, readiness, hydration and timing remain implementation work.

## MRP Alignment (Most Reasonable Product)
Improve the common constructor-input path while preserving dependency selection, scoped creation,
override isolation, hooks, cleanup and concurrency. Optimize demonstrated costs without creating
parallel inconsistent resolution semantics or slowing ordinary creation.

## Ticket Contract
- ENTRY_GATE: Certified updater_0/updater_1; separate discovery tasks routed on the attention board.
- EXECUTION_BOUNDARY: Benchmark experiments and source investigation are authorized now. Production
  API changes, compiler changes and release/build generation follow a reviewed implementation decision.
- DEPENDENCIES: Existing shallow/override benchmark workloads and current Melder runtime contracts.
- EXIT_GATE: Measured diagnosis, agreed design, accepted implementation and regression/performance evidence.
- FAILURE_ESCALATION: Record incomparable workloads, unstable measurements or unresolved semantics explicitly.

## Goals (Outcomes)
- Measure normal creation and override execution with one Melder-only experiment and shared timing rules.
- Separate top-level constructor input cost from nested override targeting and mixed override work.
- Identify which costs arise in public argument normalization, targeting, planning and execution.
- Resolve supplied sockets before selecting construction work; separate value replacement from argument modification.
- Preserve shared dependencies required by other live edges and existing lifetime/storage authority.
- Reuse existing shape caching for effective execution plans without a new traversal on every meld.
- Implement the selected design only after investigation and owner review of concrete evidence.

## Non-Goals (Explicit Exclusions)
- Benchmark competitor libraries, redesign unrelated subsystems, or change production code in discovery.
- Assume the reported throughput ratio or promise a speedup before measurements exist.
- Treat the spelling init={} as an approved public API.

## Scope Boundaries
- In scope: Supplied benchmark models, Melder-only experimentation, override hot paths and relevant tests.
- Out of scope now: Production implementation, packaged assets, existing-object redesign and unrelated Bind work.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner explicitly requested an epic and a first unified performance experiment.

## Success Metrics
- Reproducible command, Python/GIL/version/source provenance and repeated timing samples.
- Per-case median latency, throughput, spread and override throughput relative to normal creation.
- Constructor and disposal counts explicitly match the remaining requested work after substitutions.
- For isolated examples: five dependencies with three supplied builds two dependencies plus the consumer;
  both supplied deep root branches build only that root when no other reachable edge needs those branches.
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
- Other agents may change source concurrently; record fresh fingerprints for each new experiment.
- Caller-supplied input semantics and nested overrides must remain distinguishable in comparisons.

## Dependencies / External References
- benchmarks/testing_other_di/test_shallow_all.py
- benchmarks/testing_other_di/test_overrides_all.py
- tests/experimentation/

## Milestones (Track Progress)
- [x] Establish comparable Melder-only baseline measurements.
- [x] Trace measured overhead and evaluate design alternatives, including separate top-level inputs.
- [x] Measure an artifact-only same-constructor prototype and independently qualify selected regressions.
- [x] Investigate occurrence-aware pruning, validation/admission ordering and shared lifecycle semantics.
- [ ] Agree the runtime/API design and patch contracts with the owner.
- [ ] Implement and qualify the chosen optimization.

## Stories (Required to Complete)
- Investigation determines implementation story boundaries; none is activated before baseline evidence.
- STORY-2026-09-25-verify-override-writer-and-contract (melder_0 lead, melder_1; done 2026-09-26):
  tickets/stories/completed/2026-09-25_verify_override_writer_and_contract_story.md
- STORY-2026-09-26-unresolved-input-sockets (melder_0):
  tickets/stories/2026-09-26_unresolved_input_sockets_story.md

## Tasks (Cross-Cutting or Epic-Level)
- [ ] TASK-2026-09-24-discover-override-execution-semantics:
  tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md
- [ ] TASK-2026-09-24-discover-override-occurrence-slicing:
  tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md
- [ ] TASK-2026-09-24-experiment-static-many-override-execution:
  tickets/tasks/2026-09-24_experiment_static_many_override_execution_task.md
- [ ] TASK-2026-09-24-coordinate-override-execution-investigation:
  tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md
- [ ] TASK-2026-09-24-investigate-override-compiler-planning:
  tickets/tasks/2026-09-24_investigate_override_compiler_planning_task.md
- [ ] TASK-2026-09-24-measure-melder-creation-and-overrides:
  tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md

## Acceptance Criteria (Epic Done)
- The reported gap is reproduced or corrected with explicit workload/runtime evidence.
- A root-cause account separates top-level constructor arguments from general graph override behavior.
- The selected change preserves contracts and has reproducible performance/regression evidence.
- Supplied whole dependencies suppress unnecessary construction; retained shared users still resolve correctly.
- Changes to unreachable-branch errors, hooks and disposal are explicit and covered by semantic regressions.
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
- Select the proposed inactive-path and shared-input conflict behavior for supplied and runtime-reused parents.
- Define native lock/admission ordering for reuse-dependent alias activation and retained-socket readiness.
- Separate call-specific readiness from baseline SpellValidity; supplied success cannot validate an unresolved baseline.
- Preserve root pre-hook ordering relative to selector errors, or explicitly approve a changed boundary.
- Extend family manifests with alias/site/readiness facts and specificity-aware input layout under existing invalidation.

## Current Structural Design
The lead's discovery task now links joint_alpha_proposal.md, the compact structure report and native
runtime boundary. Compact physical sites plus selector progress avoid expanded path inventories;
prepared demand drives a generated native claim prelude and direct constructor/publication code.
Native experiments expose an existing store/unique-Spell lock inversion. A coherent writer protocol
must cover ordinary creation, override creation and purge while preserving Creations as the live
registry. The direct variant also removes full-catalog wrapper rebuilding from pruned warm calls.
Existing Existence, scope routing and context/cache invalidation retain their responsibilities.
No production override code, release version or build assets have changed during discovery.

## Decision Log
- 2026-09-24: Owner authorized epic creation and a unified Melder-only experiment before runtime changes.
- 2026-09-24: Owner assigns updater_0 lead; OEP-001 acknowledged the split. updater_1 owns many-only
  compiler diagnosis; updater_0 owns runtime/lifecycle constraints and synthesis. Use the mailbox with
  numbered OEP messages and bounded 30-second PowerShell waits. Task notes retain findings before delivery.
- 2026-09-24: Owner selects structural override planning over an isolated emitter patch. Preserve all
  prior evidence and continue joint discovery; do not treat eager construction as the desired invariant.
- 2026-09-25: Owner opens a melder-pair verification story alongside updater_0/updater_1: melder_0
  verifies the store/unique-Spell inversion; melder_1 verifies joint alpha contract items 1-8.
- 2026-09-25: Meld store/Spell lock-order deadlock fixed by per-slot build guards (store locks are leaves;
  cache generation 10). Override emitters now hold slot guards; joint-alpha work builds on that.
- 2026-09-26: Owner approves melder_0's UNRESOLVED_INPUT socket (typed parameter with no provider is
  supplied at meld; UnresolvedInputError otherwise) as design step S1; resolvable=False stays separate.

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
- DATETIME: 2026-09-24T10:08:38Z
  TYPE: DECISION
  CLAIM: Owner appoints updater_0 as lead and directs joint work with updater_1 through the mailbox.
    Use bounded PowerShell Start-Sleep -Seconds 30 waits between coordination checks. Lead owns
    work splitting and synthesis; each contributor records findings in their own task before messaging.
  EVIDENCE:
  - Owner's current lead assignment and PowerShell/mailbox coordination instruction.
  IMPACT: Coordinate the compiler investigation without competing edits or harness subagents.
  NEXT: updater_1 sends the baseline and proposed many-only investigation scope to updater_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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

- DATETIME: 2026-09-24T10:54:45Z
  TYPE: MEASURE
  CLAIM: Joint investigation now has a measured candidate: seven-repeat original-override public
    improvements are 1.64x shallow, 2.26x wide, 1.91x diamond and 4.68x deep with unchanged constructor
    order/count. Normal controls remain within 1%. Lead independently passes ten current many-only
    regressions against the measured candidate and proves executor restoration; 36 baseline checks
    and ten lifecycle observations support the preserved behavior boundary.
  EVIDENCE:
  - artifacts/override_execution_lead_20260924/joint_proposal.md
  - artifacts/override_emission_prototype_20260924/results.json
  - artifacts/override_execution_lead_20260924/prototype_review.json
  IMPACT: Recommend the bounded many-only emission change, retaining current API and eager lifecycle.
    The prototype does not qualify generalized/scoped/disposal/collection/contract/positional/concurrent
    production behavior. Pruning remains a separate behavior choice; no production code changed.
  NEXT: Owner reviews the concrete production scope recorded in the joint proposal and compiler map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:16:08Z
  TYPE: DECISION
  CLAIM: Owner directs the deeper structural fix and joint investigation. The emission-only prototype
    remains frozen and documented. The primary question is which constructors should execute after
    supplied dependencies satisfy their sockets, rather than how cheaply to execute every original step.
    updater_0 leads validation/lifecycle semantics; updater_1 traces occurrence graphs, plans and caches.
  EVIDENCE:
  - Owner's current structural-fix request and preceding five-dependency example.
  - artifacts/override_execution_lead_20260924/joint_proposal.md
  IMPACT: The former emission-only recommendation is superseded as the immediate production direction.
    Its optimization can support the structural design later. Runtime edits still follow investigation.
  NEXT: Complete the two new structural discovery tasks and synthesize an implementation boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-24T21:28:47Z
  TYPE: FACT
  CLAIM: Joint structural investigation now includes eleven base row scenes, nine static alias
    cases, three independent native alias failures and six lead review observations. Simple cuts
    show 6-to-3 and 511-to-1 construction work; many parent sites remain distinct. Native Meld/purge
    proves a parent can stay live with its declared shared child absent. The static alias prototype
    still lets skipped-parent rules conflict or win elsewhere; peer is qualifying conditional alias
    activation in separate artifacts while preserving the first prototype.
  EVIDENCE:
  - tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md
  - tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md
  - artifacts/override_structural_discovery_20260924/structural_plan.md
  IMPACT: The selected change spans alias/site representation, value-free shape caching, retained-work
    readiness and generated reuse branches. No native structural speed result or production fix is
    claimed. Existing Existence/Creations and context invalidation retain ownership.
  NEXT: Review the conditional-alias proof, then present the implementation contract and open policy boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-24T21:35:26Z
  TYPE: DECISION
  CLAIM: The structural discovery tranche is ready for owner review. The first alias model's
    reuse defects are preserved; a separate conditional model now has twenty peer cases and two
    independent lead reviews. Cached programs must retain guarded ranked inputs and fallback edges,
    rather than one winner chosen from a transient reuse state. The implementation boundary is
    native admission/readiness, store locks, family hydration and generated execution qualification.
  EVIDENCE:
  - tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md
  - artifacts/override_structural_discovery_20260924/structural_plan.md
  IMPACT: Investigation is no longer blocked on the two demonstrated alias counterexamples. This
    accepts a bounded proof, not a production optimization or speed claim. The epic stays open.
  NEXT: Owner reviews the documented semantics before production patch contracts are activated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-24T22:43:55Z
  TYPE: DECISION
  CLAIM: Owner-directed joint continuation produced a concrete alpha replacement proposal, not just
    more analysis of the old emitter. Compact physical graphs and selector progress now drive direct
    generated calls; the demand prelude joins to real native stores through experimental claims.
    Native tests expose an existing ordinary/override creation-versus-purge lock inversion. The direct
    integration variant also removes per-call whole-catalog wrapper rebuilding, retaining earlier
    artifacts and passing eight cases including a 511-site graph reduced to one constructor.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md
  - artifacts/override_structural_discovery_20260924/native_runtime_boundary.md
  - artifacts/override_structural_discovery_20260924/native_compact_direct_results.json
  - artifacts/override_occurrence_discovery_20260924/compact_structure_proposal.md
  IMPACT: Proposed production work must coordinate normal creation, overrides and purge under one
    writer protocol and replace the upstream path inventory, while preserving scope authority and
    existing cache ownership. No native throughput promise follows yet, and production remains unchanged.
  NEXT: Review the concrete semantic and implementation contract in joint_alpha_proposal.md.
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
Read the lead task's joint_alpha_proposal.md, compact_structure_proposal.md from the peer, and the
native_runtime_boundary.md report. The owner-directed continuation now includes compact generated/
hydrated proofs, demanded native claims and actual Creations publication, concurrency, purge and
admission controls. A direct variant demonstrates 511 -> 1 construction without catalog traversal.
The recommendation must change shared writer coordination across all paths, not just overrides.
Production adoption, complete API semantics and timing remain. Earlier prototypes and measurements
are preserved; no production patch, version bump or asset generation occurred. The epic stays open.
