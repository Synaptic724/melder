# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Keep this board compact and operational.
- Durable history belongs in ticket `## Notes`, not here.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`,
  `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`,
  `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`,
  `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- Ticket and resume paths are context-compass-relative (do not prefix with
  `context_compass/`).
- Use `DATETIME` and `updated_at` values in ISO-8601 UTC
  (`YYYY-MM-DDTHH:MM:SSZ`).
- Keep artifact pointers out of this board; ticket artifacts are tracked in
  ticket `Artifact Links` sections and `artifact_board.md`.

## Active Items
| work_item | status | mode | owner | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|---|---|---|
| story: phase12 and creation context optimization discovery | in_progress | discovery | codex | none | collect user decision on wave-1 candidate IDs and risk class | implementation planning starts immediately with approved shortlist | user selects approved candidates and requests implementation kickoff | `tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md` | 2026-02-17T17:00:02Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-17T17:00:02Z
  TYPE: DECISION_REQUEST
  CLAIM: Consolidated shortlist is documented and execution is blocked only on
    candidate approval for implementation wave 1.
  EVIDENCE:
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:169-192
  - tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md:217-230
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:64-71
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:64-72
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:64-72
  IMPACT: Discovery phase is complete and implementation can begin with no
    additional analysis once the decision is made.
  NEXT: Request user approval for shortlisted medium/high candidates.
  SWITCH_TRIGGER: user confirms approved candidate IDs and risk level.
  RESUME_HIERARCHY: story decision -> epic wave plan -> implementation tasks.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:58:00Z
  TYPE: FACT
  CLAIM: All three discovery tasks now have documented hotspot summaries and
    risk-ranked candidate tables, so routing shifts from per-task discovery to
    story-level synthesis and decision preparation.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:53-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:53-155
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:55-155
  IMPACT: Epic discovery evidence is complete enough to rank options and request
    user approval for the first implementation wave.
  NEXT: Produce consolidated shortlist of medium/high candidates with rationale
    and expected impact for user decision.
  SWITCH_TRIGGER: user approves shortlist or requests deeper per-option analysis.
  RESUME_HIERARCHY: story synthesis -> epic wave selection -> implementation tasks.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:55:17Z
  TYPE: PLAN
  CLAIM: No-overrides lane moved to review with documented options, and active
    routing advanced to overrides discovery for the second location tranche.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:3-111
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:62-68
  IMPACT: Epic discovery remains single-threaded with one active task while
    preserving completed no-overrides findings for synthesis.
  NEXT: Complete overrides candidate table and then route to creation-context
    discovery.
  SWITCH_TRIGGER: overrides deliverables are documented with evidence.
  RESUME_HIERARCHY: overrides task -> creation-context task -> story -> epic.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:52:56Z
  TYPE: FACT
  CLAIM: No-overrides task now includes hotspot summary and six risk-ranked
    candidates with call-count impact direction, completing its discovery
    deliverables for this location.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:53-71
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:148-168
  - benchmarks/testing_other_di/results/codegen_benchmark_baseline.json:217-222
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:277-282
  IMPACT: First discovery lane has concrete option inventory and can be merged
    into story-level synthesis while routing shifts to overrides discovery.
  NEXT: Activate overrides task and capture equivalent hotspot/options evidence.
  SWITCH_TRIGGER: overrides task state is in_progress and board row can switch.
  RESUME_HIERARCHY: no-overrides task -> overrides task -> story -> epic.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:48:45Z
  TYPE: PLAN
  CLAIM: User approved active execution and requested epic catch-up, so routing
    moved to the first pending location task for no-overrides discovery.
  EVIDENCE:
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:62-68
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-36
  - tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md:92-97
  IMPACT: Discovery execution is now scoped to one active task with direct
    hotspot evidence capture and option synthesis.
  NEXT: Complete no-overrides hotspot findings and draft medium/high-risk
    options with expected cProfile impact.
  SWITCH_TRIGGER: no-overrides task deliverables are documented with evidence.
  RESUME_HIERARCHY: no-overrides task -> story -> epic.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:20:08Z
  TYPE: PLAN
  CLAIM: Benchmark protocol task is closed, so active routing returns to the
    story to execute remaining three location discovery tasks and synthesize
    medium/high-risk options.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md:1-215
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:1-144
  - tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md:1-175
  IMPACT: Benchmark scoring is locked and remaining work is discovery evidence
    and option design for optimization waves.
  NEXT: Begin the first location discovery task when user confirms execution
    order.
  SWITCH_TRIGGER: user requests immediate discovery start or selects first
    implementation candidate.
  RESUME_HIERARCHY: story -> location discovery tasks -> epic.
  REREAD: REQUIRED

- DATETIME: 2026-02-17T16:05:17Z
  TYPE: MEASURE
  CLAIM: Benchmark protocol implementation emits route-level cProfile fields
    and weighted 75/25 scoring, with pinned-core baseline and comparison
    reports generated.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md:1-215
  - benchmarks/testing_other_di/results/codegen_benchmark_baseline.json:3-745
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:807-853
  IMPACT: Optimization attempts can be assessed with deterministic before/after
    weighted ratios where cProfile call count regression has dominant weight.
  NEXT: use this baseline protocol for all optimization-wave success claims.
  SWITCH_TRIGGER: first discovery task starts.
  RESUME_HIERARCHY: story -> location discovery tasks -> epic.
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | REQUIRED |
| task: split root AGENTS into bootstrap and profile-owned policies | done | codex | none | none | `tickets/tasks/completed/2026-02-17_agents_bootstrap_split_and_profile_distribution_task_completed.md` | 2026-02-17T15:53:33Z | HELPFUL |
