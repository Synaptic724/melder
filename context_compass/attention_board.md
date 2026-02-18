

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
| epic: skill-gate-first compaction measurement loop | review | handoff | codex | none | share implemented policy/generator/board changes and request acceptance confirmation | score-grounded compaction loop with skill-gate-first onboarding, targeted relearn, and single-cycle reset/shrink is implemented | user confirms acceptance criteria so epic/story/tasks can move to completed folders | `tickets/epics/2026-02-18_skill_gate_first_compaction_measurement_loop_epic.md` | 2026-02-18T17:07:51Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Discovery and implementation lanes are complete; compaction policy now
    enforces skill-gate-first minimum reads, score-grounded completion, targeted
    relearn, and single-active-cycle reset/shrink behavior.
  EVIDENCE:
  - AGENTS.MD:59-61
  - agent_onboarding/default/general/skills/compaction_requirements.md:61-185
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:54-107
  - skill_check/skill_check_policy.md:21-26
  - compacting_differential_board.md:107-109
  - skill_check/generate_bootstrap_suite.py:270-329
  IMPACT: Active work is now closure-ready pending user acceptance.
  NEXT: run walkthrough and confirm acceptance criteria before moving tickets.
  SWITCH_TRIGGER: user confirms acceptance criteria.
  RESUME_HIERARCHY: epic.
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
