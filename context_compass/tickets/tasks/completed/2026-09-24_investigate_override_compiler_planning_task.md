# Task: Trace override plan divergence through compiler phases 7-11

- Completed: 2026-09-26T13:45:56Z
- Summary: Default-plan reuse diagnosis verified by the measured prototype. Turned in by the owner in the 2026-09-26 board cleanup (row agent updater_1);
  no further work; artifacts retained as reference.

## Metadata
- Task ID: TASK-2026-09-24-investigate-override-compiler-planning
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: done
- Owner: codex
- Agent Name: updater_1
- Priority: p1
- Created: 2026-09-24T10:04:57Z
- Updated: 2026-09-26T13:45:56Z

## Objective
Explain why the override path departs from normal-plan performance and constructs overridden
descendants. Trace phases 7-11, emphasizing phase-10 planning and phase-11 executor generation.
Evaluate the owner's default-plan-plus-adjustments model before selecting an API or implementation.

## Ticket Contract
- ENTRY_GATE: Baseline evidence exists; this task is routed from the attention board under the epic.
- EXECUTION_BOUNDARY: Source/test inspection, diagnostic experiments and ContextCompass artifacts.
  Production compiler/runtime changes and an init={} API remain outside this investigation.
- DEPENDENCIES: Completed measurement work; live phase/planner/codegen sources and relevant regression contracts.
- EXIT_GATE: Source-backed phase map, precise cause of wasted work, proposed change boundaries and risks.
- FAILURE_ESCALATION: Record unresolved lifetime, hook, shared-node or override-precedence semantics explicitly.

## Scope Boundaries
- In scope: Phases 7-11; plan/model/occurrence inputs; many-only and generalized no-override/override
  strategies; target resolution, shape caches, generated execution and affected test contracts.
- Out of scope: Production edits, release generation, unrelated optimizations and another public API now.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Compiler diagnosis, exact source capture and bounded next-tranche seams delivered to lead.
- from_state: review
- to_state: done
- transition_reason: Owner turned in this dormant row in the 2026-09-26 shared-board cleanup (all 13 dormant rows,
  2026-09-26T13:45:56Z); closed by fable_0 with board and artifact sync.

## Questions To Resolve
- Where do the normal and override plans diverge, and what is already shared?
- Which decisions are compile-time, first-use specialization, or repeated per call?
- Why do supplied root dependencies still cause all descendants to be constructed?
- Can unchanged subgraphs retain normal generated execution while changed sockets substitute values?
- How should shared occurrences, hooks, disposal, positional inputs and invalidation constrain pruning?

## Steps / Checklist
- [x] Read phase ownership and route the measured all-many graphs to their real planner/codegen family.
- [x] Trace the default plan and override delta through generation, caching and execution.
- [x] Verify wasted-work causes against generated executors and relevant tests.
- [x] Compare concrete implementation approaches and record recommended boundaries.

## Deliverables
- Source-backed compiler trace and a concrete proposal for default-plan-biased overrides.
- Focused diagnostic evidence where source alone does not settle a behavior question.

## Files / Paths Impacted
- This task, parent epic and shared routing/check-in/artifact boards.
- Optional investigation artifacts associated with this task.

## Validation
Exact source capture and eight warmed identity/constructor-count cases passed with stable runtime
source fingerprints. The diagnostic script passes Ruff. No new speed measurement or production edit.

## Risks / Mitigations
- Shared descendants may remain required elsewhere: reason over occurrences/edges, not only types.
- Removing eager constructors can affect side effects and lifecycle: identify current contracts first.
- New source revision: another agent completed cache-release work after baseline; do not imply source identity.

## Applicable Anti-Patterns
- [ ] No full recompilation per override value as an unmeasured default.
- [ ] No pruning based solely on type names or graph appearance.
- [ ] No production implementation before the agreed compiler contract.

## Done Checklist
- [x] Actual phase owners and code paths identified.
- [x] Per-call overhead and eager construction explained with evidence.
- [x] Design tradeoffs and regression matrix delivered.
- [ ] Owner accepts investigation outcome.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/override_compiler_investigation_20260924/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Preserve investigation evidence for the implementation decision.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Default plans, override deltas and phase-10/11 code generation.
- IF_UNKNOWN: none

## Noting Behavior
Record each complete source/call-path tranche with evidence, impact and one NEXT step.

## Notes
- DATETIME: 2026-09-24T10:04:57Z
  TYPE: DECISION
  CLAIM: Owner directs structural investigation: overrides should favor the default plan and
    adjust only required parts. Prioritize phase 10-11 within the phase 7-11 compiler sequence.
  EVIDENCE:
  - Owner's current default-plan and phase-10/11 direction.
  - artifacts/override_execution_performance_20260924/findings.md:7-74
  IMPACT: Investigate common planning and execution rather than committing to a separate init={} API.
  NEXT: Read phase dispatch, planner family selection and phase-11 generation for the measured all-many graphs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:07:35Z
  TYPE: FACT
  CLAIM: Phase 7 wires change-control revalidation. Phase 8 publishes occurrence analysis, phase 9
    the codegen model, phase 10 the codegen plan, and phase 11 the creation handoff. The many-only
    planning strategy invokes the same builder twice with NO_OVERRIDES and OVERRIDES variants.
    The warmed measurements concern execution produced by these phases, not evidence that all
    phases rerun for every override call.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:52-265
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:76-123
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:62-91
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:74-112
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:79-127
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_many_only_codegen_plan_strategy.py:39-77
  IMPACT: Determine where the shared model loses fast execution structure in the override variant,
    then inspect phase-11 shape specialization and actual generated instructions.
  NEXT: Read the many-only plan builder and both phase-11 compiler paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:08:38Z
  TYPE: DECISION
  CLAIM: Owner assigns updater_0 as lead. updater_1 will coordinate through the repository mailbox
    using bounded 30-second PowerShell waits. Proposed contribution is the many-only phase-10/11
    default/override plan and generated-executor trace, pending the lead's split or redirection.
  EVIDENCE:
  - Owner's current lead assignment and mailbox coordination instruction.
  - tickets/epics/2026-09-24_override_execution_performance_epic.md
  IMPACT: Continue source-only evidence gathering within the current scope; send findings before
    implementation planning. No production edits or new agents are authorized by this coordination.
  NEXT: Send the current findings and proposed scope to updater_0, then check for a reply after 30 seconds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:10:42Z
  TYPE: FACT
  CLAIM: The many-only builder creates the same complete dependency-first occurrence sequence
    for both variants. Only the normal variant precomputes callable/arity/dependency-slot arrays;
    the overrides variant returns all steps with targeting prefixes and no equivalent flat arrays.
    Phase 11 packages an empty-target override baseline separately from the normal executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:977-1362
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_overrides_codegen_creation_step.py:116-183
  IMPACT: The structural divergence exists before runtime targeting: retaining normal call structure
    in an override-delta plan is a concrete design seam. Full execution cause still requires reading the emitter.
  NEXT: Read the finalizer shape-cache path and generated override emitter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T10:11:55Z
  TYPE: FACT
  CLAIM: The phase-11 many-only finalizer already caches specialization by plan signature, socket
    shape and positional arity, with an atomic last-shape tuple. Values are supplied per call.
    Warm calls still split payloads and apply targeting before entering a cached executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:243-469
  IMPACT: Do not diagnose this as recompilation for every value. The critical next comparison is
    emitted override instructions versus the normal plan's prebound call sequence.
  NEXT: Read the shape emitter and ordinary unrolled emitter, then provide lead a precise change seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T10:19:10Z
  TYPE: DECISION
  CLAIM: Re-onboarding is complete after owner compaction. Received OEP-001 from updater_0, confirming
    updater_1 owns many-only phase-10/11 diagnosis and the existing experiment. updater_0 leads synthesis
    and independently traces targeting, shared/scoped occurrences and hook/disposal constraints.
    Coordinate timed runs and use bounded 30-second PowerShell waits when awaiting replies.
  EVIDENCE:
  - tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md:73-88
  - Owner's current compaction message reconfirming updater_0 as lead.
  IMPACT: Retain the current investigation boundary and peer-owned files; production edits remain excluded.
  NEXT: Acknowledge OEP-001 and capture actual shallow normal/override generated executors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:21:28Z
  TYPE: FACT
  CLAIM: Normal transient emission hoists constructor targets and emits direct fixed-arity calls
    using local vN results. Override shape emission retains every step and a dictionary keyed by
    instance identity. Even untouched steps read plan_step.spell.spell, select the creations store,
    assemble keyword dictionaries for dependencies and store their result. Store selection remains
    emitted when static disposal is False, although no registration will consume it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:1203-1429
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:756-859
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1329-1977
  IMPACT: Two separable changes exist: cheaper equivalent emission for the same ordered constructors,
    then occurrence-aware pruning with observable lifecycle consequences. No speedup is measured yet.
  NEXT: Capture generated shallow executors and per-case constructor counts without timing or runtime edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:24:42Z
  TYPE: MEASURE
  CLAIM: Exact emitted sources confirm normal shallow construction is t0(), t1(), t2(v0, v1).
    A warmed root override still constructs both leaves, selects unused creation stores, performs
    dictionary writes and compares socket parameter names before calling the root through **kwargs.
    Captured shallow cases execute 3 fixture constructors; diamond cases execute 5, including full
    root replacement and broadcast leaf override. Runtime source fingerprints are unchanged.
    This diagnostic reports counts and source, not latency or a speedup.
  EVIDENCE:
  - artifacts/override_compiler_investigation_20260924/000_shallow_setup.py:1-35
  - artifacts/override_compiler_investigation_20260924/002_shallow_root_one_reused.py:1-110
  - artifacts/override_compiler_investigation_20260924/003_shallow_root_all_reused.py:1-119
  - artifacts/override_compiler_investigation_20260924/capture.json
  IMPACT: Baseline cost is paid even by unaffected leaves. Reuse normal-style static call operands
    in shape specialization before making the distinct semantic decision to skip constructors.
  NEXT: Send this evidence and proposed seams to updater_0, then inspect the specialization key granularity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:24:42Z
  TYPE: FACT
  CLAIM: Received OEP-002/003. Lead reports generalized manifest raw-key caching and 36 passing
    selector/reuse/eager-branch checks. Existing non-resolvable-override tests characterize supplied
    whole branches as still executing their registered constructors, including missing-input failures.
    These are lead-verified results; updater_1 has not rerun those tests.
  EVIDENCE:
  - tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md
  IMPACT: Proposal separates same-constructor-order emitter improvements from observable pruning.
  NEXT: Align the recommendation with the lead's lifecycle findings through OEP-004.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T10:25:50Z
  TYPE: FACT
  CLAIM: The many-only specialization key already includes exact socket shape (node, path, parameter,
    kind) and positional arity. But the shape emitter receives only targeted spell IDs and per-step
    target counts. Exact parameter identity is discarded before source emission, requiring runtime
    socket.param_name comparisons and kwargs assembly inside a supposedly specialized executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:572-828
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:231-335
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:615-754
  IMPACT: Keep the existing shape-cache lifetime but carry exact per-occurrence socket operands into
    lowering. This can select default dependency locals versus supplied values once per shape.
    API differentiation is not necessary merely to represent this information.
  NEXT: Share this lost-information seam and propose a bounded emission-only experiment to the lead.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:32:26Z
  TYPE: DECISION
  CLAIM: OEP-005/006 received and retained. Lead confirms lifecycle effects and requests final seams.
    He also found generalized source/factory keys use counts rather than exact operand placement.
    Many-only hydration instead reuses the finalizer with its exact socket-shape key. The final
    compiler_findings.md recommends an emission-only experiment first, using the same constructors
    and normal call layout plus socket substitutions. Preserve a-only/b-only equal-count alternation.
  EVIDENCE:
  - artifacts/override_compiler_investigation_20260924/compiler_findings.md
  - artifacts/override_execution_lead_20260924/runtime_constraints.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:208-349
  IMPACT: Source diagnosis is reviewable; no new API or production implementation is needed to test it.
    Initial eligibility is disposal-free many-only named inputs; broader semantics remain explicit follow-ons.
  NEXT: Send OEP-007 with the final artifact and await lead synthesis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T10:35:21Z
  TYPE: FACT
  CLAIM: Final source cross-check finds another occurrence granularity loss: static targeted presence
    is set from Spell ID while target counts are per occurrence. An untouched occurrence of a targeted
    Spell can enter override assembly with count zero and emit empty-map membership tests instead of
    the unchanged-step path. This reinforces selecting emission from exact per-occurrence operands.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:615-754
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:976-1328
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1790-1933
  IMPACT: Add repeated-Spell nested-selector cases alongside equal-count a/b shape alternation.
    No separate implementation is proposed; the operand-based design already covers this.
  NEXT: Send the OEP-007 addendum and await lead receipt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Compiler investigation delivered to updater_0. Read compiler_findings.md in the linked artifact folder.
It contains exact generated sources, validated 3/5-constructor counts, the lost socket-identity seam,
proposed files/symbols and an emission-only first experiment. Lead owns combined design and next routing.
No production edits, new public API or optimized speedup claim. Task is in review, not closed.
