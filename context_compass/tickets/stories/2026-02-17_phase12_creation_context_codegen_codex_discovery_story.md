# Story: Codex Discovery On Phase12 And CreationContext Codegen

## Metadata
- Story ID: STORY-2026-02-17-phase12-creation-context-codegen-codex-discovery
- Epic: EPIC-2026-02-17-phase12-creation-context-codegen-performance
- Mission: codex_discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T19:18:11Z
- Updated: 2026-02-17T20:53:52Z

## User Narrative
As a performance-focused maintainer, I want a fresh Codex-only discovery lane on
Phase 12 and `CreationContext` codegen, so that concurrent agent activity does
not contaminate findings or routing.

## Value / MRP Alignment
This story creates a clean, bounded, evidence-first discovery lane before any
new optimization implementation. It preserves system correctness while we
identify high-leverage call-path and specialization-shape risks.

## Ticket Contract
- ENTRY_GATE: `attention_board.md` active row routes to this story and no
  implementation/validation runs under unrelated tickets.
- EXECUTION_BOUNDARY: read/discovery in
  `src/melder/aether/conduit/meld/creation_context/creation_context.py`,
  `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`,
  and
  `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`.
- DEPENDENCIES: EPIC-2026-02-17-phase12-creation-context-codegen-performance.
- EXIT_GATE: story notes contain evidence-backed hotspot findings, risk-ranked
  options, and explicit next-step task recommendations.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if proposed optimization alters
  override semantics, root reuse contracts, or lock/gate behavior.

## Requirements (Functional)
- Capture concrete code hotspots in Phase 12 no-overrides, Phase 12 overrides,
  and `CreationContext`.
- Document risks/opportunities with `path:start-end` evidence.
- Keep findings scoped to codegen runtime and override specialization flow.

## Requirements (Non-Functional)
- No assumptions: UNKNOWN-first discipline for unevidenced claims.
- Maintain compact, replay-safe notes for compaction/handoff.
- Avoid touching implementation code during this discovery-only mission.

## Scope Boundaries
- In scope:
  - Source review of codegen compile/runtime specialization paths.
  - Cache behavior, shape-key behavior, and override payload routing analysis.
- Out of scope:
  - Code edits to runtime behavior.
  - Benchmark reruns or performance claims without execution evidence.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested a brand-new Codex discovery lane tied to
  the existing Phase 12 epic while avoiding the currently active task lane.

## Dependencies / Related Work
- `tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md`
- `tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md`

## Tasks (Implementation Checklist)
- [x] Convert findings into one scoped task per approved optimization tranche.
- [x] Task: TASK-2026-02-17-phase12-codex-attempts-implementation - implement
      empty override normalization while keeping override cache unbounded.
- [ ] Require explicit user approval before any runtime code edits.
- [ ] Keep all discovery findings in story notes with line-range evidence.
- [ ] Enforce Ticket Microcycle while discovery continues.

## Acceptance Criteria
- Story routes as active lane in `attention_board.md`.
- At least three evidence-backed discovery findings are logged.
- Findings include at least one correctness-risk and one perf-opportunity item.
- Next-step task candidates are proposed with clear scope boundaries.

## Validation / Test Plan
- Not run.
- Discovery-only mission; no runtime behavior changes performed.

## UX / API / Data Notes
- No public API changes permitted in this story.
- Root override semantics and existing-instance behavior must stay explicit in
  follow-up tasks.

## Risks / Mitigations
- Risk: concurrent work causes routing drift.
  Mitigation: board row pinned to this story and story-specific notes.
- Risk: discovery drifts into implementation.
  Mitigation: explicit discovery-only boundary with escalation gate.

## Applicable Anti-Patterns
- [ ] No claims promoted from UNKNOWN to FACT without file evidence.
- [ ] No implementation/edit activity under this discovery-only story.
- [ ] No scope expansion outside the three target source files without approval.

## Open Questions
- Should empty dict `spell_override` (`{}`) be normalized to `None` so root
  reuse stays on no-overrides semantics?
- Is override-specialization cache cardinality bounded enough for long-lived
  dynamic sessions with many unique override shapes?

## Decision Log
- Created separate Codex-only discovery lane tied to the existing Phase 12 epic
  due to concurrent agent activity.
- User approved empty-override normalization but explicitly rejected bounded
  override-specialization cache policy for this tranche.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-17T19:18:11Z
  TYPE: FACT
  CLAIM: Empty dict override payloads remain non-null through Meld normalization
    and are treated as `any_overrides_present=True` in specialization compile
    selection, which activates root existing-instance override guards.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:290-294
  - src/melder/aether/conduit/meld/meld.py:954-960
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:674-683
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2610-2634
  IMPACT: Root reuse semantics for `{}` may diverge from no-overrides calls and
    can inject avoidable override-lane cost/failure behavior.
  NEXT: confirm intended contract for empty override payloads and decide whether
    front-door normalization should coerce `{}` to `None`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T19:18:11Z
  TYPE: FACT
  CLAIM: `CreationContext` maintains multiple override specialization caches
    keyed by shape/signature with no runtime eviction; they are only cleared on
    context cleanup.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:259-279
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:358-373
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1064-1107
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1219-1233
  IMPACT: Long-lived contexts with high override-shape cardinality can accrue
    memory and compile churn even when behavior is functionally correct.
  NEXT: measure real shape-cardinality under benchmark routes before proposing
    cache-bound or eviction strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T19:18:11Z
  TYPE: FACT
  CLAIM: Phase 12 overrides already includes compile-time prefilter caching of
    step targets and path metadata keyed by specialization shape.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:679-689
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2547-2566
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2589-2606
  IMPACT: Any proposal to "add caching for step-target prefilter" is already
    redundant; optimization focus should move to cache-cardinality and call-path
    overhead instead.
  NEXT: target discovery on specialization-key cardinality and root override
    branching semantics, not prefilter recomputation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T19:18:11Z
  TYPE: FACT
  CLAIM: Phase 12 no-overrides has two emitted-codegen lanes: transient-unrolled
    (optionally native-dispatched via env gate) and step-plan fallback.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:58-92
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:285-351
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:552-579
  IMPACT: Discovery and benchmark comparisons must isolate env-gated native
    dispatch effects from Python-source emission effects.
  NEXT: keep follow-up measurement matrix explicit for native-dispatch on/off
    before attributing gains to Python-side code changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-02-17T19:25:58Z
  TYPE: DECISION
  CLAIM: Discovery findings are transitioned into a new implementation task
    lane under this story to execute scoped attempts with benchmark-first gate.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_codex_attempts_implementation_task.md:1-145
  - context_compass/attention_board.md:23-39
  IMPACT: Story now separates discovery and implementation execution while
    preserving epic benchmark-before-edit policy.
  NEXT: run mandatory pre-change benchmark and begin task-scoped code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T20:20:28Z
  TYPE: MEASURE
  CLAIM: Implementation tranche completed with empty-dict override normalization
    plus targeted tests, but post-change benchmark did not show net weighted
    improvement; targeted override lane regressed versus pre-change baseline.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_codex_attempts_implementation_task.md:56-62
  - tickets/tasks/2026-02-17_phase12_codex_attempts_implementation_task.md:182-210
  - benchmarks/testing_other_di/results/codegen_benchmark_after_codex_attempts.json:176-194
  - benchmarks/testing_other_di/results/codegen_benchmark_after_codex_attempts.json:812-841
  IMPACT: Discovery question about empty dict semantics is now resolved in code,
    and cache-cardinality remains explicitly unbounded per user direction; next
    optimization tranche should target a different hotspot.
  NEXT: keep this story open for next codex_discovery-backed optimization task
    selection under the same epic benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T20:53:52Z
  TYPE: MEASURE
  CLAIM: Higher-confidence pinned-core rerun (`sample_count=21`,
    `profile_iteration_count=25`) passed weighted scoring and showed targeted
    override median improvement versus baseline.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_codex_attempts_implementation_task.md:304-320
  - benchmarks/testing_other_di/results/codegen_benchmark_after_codex_attempts_high_samples.json:170-193
  - benchmarks/testing_other_di/results/codegen_benchmark_after_codex_attempts_high_samples.json:904-936
  IMPACT: This implementation tranche is now in acceptance-review state rather
    than immediate next-candidate selection.
  NEXT: request user acceptance decision and close task if approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-file synthesis on codegen execution contracts and cache
  behavior.
- Add notes when risk classification changes or a follow-up task boundary is
  finalized.
- Keep notes append-only and maintain UNKNOWN-first discipline.

## Context / Handoff Summary
Codex-only discovery lane remains active under the phase-12 epic with source
evidence across `CreationContext` and Phase 12 executors. The first codex
implementation tranche now has a high-confidence weighted pass after expanded
sampling/profile iterations, so the immediate next action is user acceptance
review for task closure.
