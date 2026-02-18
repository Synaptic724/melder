# Task: Holistic Discovery For Phase 8-12 and Creation Context Codegen

## Metadata
- Task ID: TASK-2026-02-18-phase8-12-holistic-codegen-discovery
- Story: STORY-2026-02-18-phase12-creation-context-speedup
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## Objective
Build one holistic discovery map that covers phase8-12 and creation_context
hotspots, then produce an implementation order without executing code changes.

## Ticket Contract
- ENTRY_GATE: attention board routes active work to this task.
- EXECUTION_BOUNDARY: discovery only, no implementation edits.
- DEPENDENCIES: benchmark runner, p-core affinity helper, phase8-12 sources.
- EXIT_GATE: evidence-backed hotspot ranking + execution task plan produced.
- FAILURE_ESCALATION: raise BLOCKER if requested source docs are inaccessible.

## Scope Boundaries
- In scope:
  - benchmark policy and route-scoring surfaces
  - phase8-12 compile/execution surfaces
  - creation_context codegen execution surfaces
  - stories/tasks planning for execution tranches
- Out of scope:
  - code implementation and behavior changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested immediate holistic discovery pass.

## Steps / Checklist
- [x] Create epic + phase stories + task tree for execution lane.
- [x] Read architecture and components docs (`src_architecture.md` and `src_components.md`).
- [x] Trace phase8-12 call surfaces and cache/invalidation boundaries.
- [x] Trace creation_context execute paths used by fast/override routes.
- [x] Build hotspot ranking and phase execution order.
- [x] Convert findings into implementation-ready phase tasks.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One discovery summary with ranked hotspots for phase8-12 and creation_context.
- Story/task execution sequence with boundaries and validation gates.
- Explicit weighted validation policy for future execution tasks.

## Files / Paths Impacted
- `context_compass/tickets/epics/2026-02-18_codegen_phase8_12_creation_context_speedup_epic.md`
- `context_compass/tickets/stories/2026-02-18_phase8_occurrence_plan_speedup_story.md`
- `context_compass/tickets/stories/2026-02-18_phase9_injection_plan_speedup_story.md`
- `context_compass/tickets/stories/2026-02-18_phase10_patch_map_speedup_story.md`
- `context_compass/tickets/stories/2026-02-18_phase11_execution_plan_speedup_story.md`
- `context_compass/tickets/stories/2026-02-18_phase12_creation_context_speedup_story.md`
- `context_compass/tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md`
- `context_compass/tickets/tasks/2026-02-18_phase9_injection_plan_optimization_task.md`
- `context_compass/tickets/tasks/2026-02-18_phase10_patch_map_optimization_task.md`
- `context_compass/tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md`
- `context_compass/tickets/tasks/2026-02-18_phase12_creation_context_optimization_task.md`
- `context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands (execution tranche):
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --output-path <baseline_json>`
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path <baseline_json> --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path <after_json>`

## Risks / Rollback Notes
- Risk: discovery may miss architecture coupling without required docs.
- Mitigation: read and cite architecture/components docs before final ranking.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T18:54:05Z
  TYPE: FACT
  CLAIM: Benchmark runner includes route matrix collection for warm root,
    override root args, and targeted override lanes plus weighted regression scoring.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:810-840
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:357-359
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1100-1229
  IMPACT: Discovery and execution tasks can use existing route schema and
    weighted scoring contract.
  NEXT: complete code-path discovery for phase8-12 and creation_context.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T18:54:05Z
  TYPE: UNKNOWN
  CLAIM: Current report schema includes medians but may not persist mean metrics
    required for fast/override success tracking.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:989-1012
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1088-1091
  IMPACT: Execution tasks may need schema extension to publish means.
  NEXT: verify schema fields during discovery and define implementation scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:20:28Z
  TYPE: FACT
  CLAIM: Architecture/components docs confirm phase8-11 are explicit post-foundational plan phases and phase12 executes through `creation_context` compiled no-overrides/overrides lanes; tests architecture docs remain placeholder UNKNOWNs and are not usable for hotspot claims.
  EVIDENCE:
  - system_docs/src_architecture.md:306-306
  - system_docs/src_architecture.md:508-522
  - system_docs/src_components.md:744-744
  - system_docs/src_components.md:1546-1554
  - system_docs/tests_architecture.md:79-94
  IMPACT: Discovery can now focus directly on phase8-12 and `creation_context` runtime paths in `src/` and benchmark routing without relying on incomplete tests architecture docs.
  NEXT: trace phase8-12 call surfaces and cache/invalidation boundaries in `spell_crafter.py`, then map `creation_context` execute paths used by fast and override routes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:22:31Z
  TYPE: FACT
  CLAIM: Hotspot ranking for the active lane is now explicit: (1) phase11 execution-plan build/reuse plus phase12 no-overrides compile handoff, (2) phase8-11 IR export + dirty-flag recapture path, (3) `creation_context` override executor cache/compile path, and (4) benchmark weighted route scoring/reporting gates for override routes.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:2319-2502
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4058-4463
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:565-706
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1064-1176
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:810-840
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:971-1229
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1280-1346
  IMPACT: We can execute implementation in a low-risk order that first cuts repeated plan/compile churn, then reduces override specialization miss cost, while validating gains on the existing route matrix and weighted baseline gates.
  NEXT: convert this ranking into concrete per-phase execution sub-steps under existing phase8-12 tasks with explicit validation gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T19:23:09Z
  TYPE: FACT
  CLAIM: Phase8/9/10/11/12 optimization tasks exist and are all `ready` but remain discovery-blocked with generic checklists; they need ranked execution order and concrete target-function gates inserted before implementation starts.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md:1-123
  - tickets/tasks/2026-02-18_phase9_injection_plan_optimization_task.md:1-120
  - tickets/tasks/2026-02-18_phase10_patch_map_optimization_task.md:1-122
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:1-120
  - tickets/tasks/2026-02-18_phase12_creation_context_optimization_task.md:1-137
  IMPACT: Without task-level sequencing and explicit target function boundaries, execution can drift into cross-phase scope creep despite having hotspot evidence.
  NEXT: update phase tasks with ranked tranche order and explicit target symbols, then unblock them from discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:24:31Z
  TYPE: FACT
  CLAIM: Discovery outputs are now converted into implementation-ready tranche tasks: phase11 is tranche #1, phase8/9/10 are tranche #2 with dirty/export boundaries, and phase12+creation_context is tranche #3 with explicit route/weighted validation gates.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:107-120
  - tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md:107-121
  - tickets/tasks/2026-02-18_phase9_injection_plan_optimization_task.md:105-119
  - tickets/tasks/2026-02-18_phase10_patch_map_optimization_task.md:106-120
  - tickets/tasks/2026-02-18_phase12_creation_context_optimization_task.md:121-137
  IMPACT: The epic can now switch from discovery into controlled implementation without re-discovering scope boundaries per phase.
  NEXT: route attention board to tranche #1 (`phase11_execution_plan_optimization_task`) and begin implementation tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery lane has produced hotspot ranking and converted it into phase-level
execution tranches. Next step is to route to tranche #1 task
(`phase11_execution_plan_optimization_task`) and start scoped implementation.
