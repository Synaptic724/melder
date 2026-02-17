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
| story: phase12 and creation context optimization discovery | in_progress | discovery | codex | none | execute per-location discovery tasks and finalize risk-ranked options | benchmark-ready discovery package with medium/high-risk options | user approves implementation wave based on discovery outputs | `tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md` | 2026-02-17T15:53:33Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-17T15:53:33Z
  TYPE: PLAN
  CLAIM: Discovery lane is established with one epic, one story, and four tasks
    covering `creation_context`, Phase12 no-overrides, Phase12 overrides, and
    pinned-core benchmark/scoring protocol.
  EVIDENCE:
  - tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md:1-170
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:1-140
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:1-126
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:1-126
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:1-129
  - tickets/tasks/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task.md:1-129
  IMPACT: Work can proceed deterministically with explicit location ownership
    and benchmark success rules.
  NEXT: Start with benchmark protocol task, then run location discovery tasks.
  SWITCH_TRIGGER: benchmark protocol and discovery findings are approved for
    implementation wave.
  RESUME_HIERARCHY: story -> benchmark task -> location discovery tasks -> epic.
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| task: split root AGENTS into bootstrap and profile-owned policies | done | codex | none | none | `tickets/tasks/completed/2026-02-17_agents_bootstrap_split_and_profile_distribution_task_completed.md` | 2026-02-17T15:53:33Z | HELPFUL |
