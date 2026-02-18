

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
| task: historical language hard-cut purge | in_progress | implementation | codex | none | summarize completion and request closure confirmation | forward-only wording is consistent across full context_compass docs | user confirms task closure | `tickets/tasks/2026-02-18_historical_language_hard_cut_purge_task.md` | 2026-02-18T00:38:29Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T00:35:09Z
  TYPE: PLAN
  CLAIM: User requested continuation after closure; a follow-up hard-cut purge
    task is active to remove remaining historical wording across
    `context_compass`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_historical_language_hard_cut_purge_task.md:1-62
  - artifacts/README.md:34-34
  - agent_onboarding/default/new/README.md:29-29
  - agent_onboarding/user_defined/synaptic_python_developer/README.md:24-24
  IMPACT: Completes forward-only language enforcement across active and
    historical documentation surfaces.
  NEXT: patch matched files and re-run verification.
  SWITCH_TRIGGER: verification search returns zero targeted matches.
  RESUME_HIERARCHY: task.
  REREAD: REQUIRED

- DATETIME: 2026-02-18T00:38:29Z
  TYPE: MEASURE
  CLAIM: Wording normalization pass completed and verification scan returned no
    matches for the targeted terminology set.
  EVIDENCE:
  - tickets/tasks/2026-02-18_historical_language_hard_cut_purge_task.md:41-74
  - artifacts/README.md:34-34
  - agent_onboarding/default/new/README.md:29-29
  - agent_onboarding/user_defined/synaptic_python_developer/README.md:24-24
  - examples/example_epics/2026-02-16_system_representation_documentation_improvement_epic_completed.md:143-143
  IMPACT: Active work can move to closure confirmation without additional patch
    rounds.
  NEXT: present completion summary and request user closure decision.
  SWITCH_TRIGGER: user confirms task closure.
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



