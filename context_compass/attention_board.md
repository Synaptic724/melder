

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
| task: skill check bootstrap test suite generation | in_progress | implementation | codex | none | generate manifest and cycle test/answer files for required docs | compaction-ready skill-check suite exists with quality metrics | generated suite satisfies bootstrap policy requirements | `tickets/tasks/2026-02-18_skill_check_bootstrap_test_suite_task.md` | 2026-02-18T16:01:46Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T16:01:46Z
  TYPE: PLAN
  CLAIM: User requested immediate skill-check suite build for compaction setup;
    active routing now targets bootstrap manifest and cycle artifact generation.
  EVIDENCE:
  - tickets/tasks/2026-02-18_skill_check_bootstrap_test_suite_task.md:1-74
  - skill_check/skill_check_policy.md:63-65
  IMPACT: Workstream shifts from prior wording-cleanup closure to compaction
    readiness artifact generation.
  NEXT: generate manifest entries and required cycle test/answer files.
  SWITCH_TRIGGER: bootstrap artifacts exist and quality gate summary is
    available.
  RESUME_HIERARCHY: task.
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| epic: onboarding policy drift hardening | done | codex | none | none | `tickets/epics/completed/2026-02-17_onboarding_policy_drift_hardening_epic_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| story: certification token-only policy | done | codex | none | none | `tickets/stories/completed/2026-02-18_certification_token_only_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| task: onboarding policy skills/certify/reonboard sweep | done | codex | none | none | `tickets/tasks/completed/2026-02-17_onboarding_policy_skills_certify_reonboard_sweep_task_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | REQUIRED |
| task: split root AGENTS into bootstrap and profile-owned policies | done | codex | none | none | `tickets/tasks/completed/2026-02-17_agents_bootstrap_split_and_profile_distribution_task_completed.md` | 2026-02-17T15:53:33Z | HELPFUL |
