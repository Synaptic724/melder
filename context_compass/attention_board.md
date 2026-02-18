

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
| task: phase8 occurrence-plan tranche | in_progress | implementation | codex | none | implement phase8 compile/reuse optimization within `run_phase_occurrence_plan` + input-signature boundary | phase8 optimization patch is ready with phase11 behavior preserved | phase8 task records implementation + validation notes and clears weighted gate | `tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md` | 2026-02-18T19:32:27Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T19:32:27Z
  TYPE: DECISION
  CLAIM: Phase11 tranche is unblocked after weighted pass rerun; active routing has advanced to tranche #2 phase8 implementation.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:53-63
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:146-154
  - tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md:1-122
  IMPACT: Epic execution continues without blocker; next risk is phase8 churn reduction without invalidating downstream signatures.
  NEXT: implement phase8 tranche and log the first meaningful code-level finding in task notes.
  SWITCH_TRIGGER: phase8 tranche reaches validation-ready state or reveals a cross-phase conflict requiring reroute.
  RESUME_HIERARCHY: task -> story -> epic.
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| story: knowledge-test-only gate | done | codex | none | none | `tickets/stories/completed/2026-02-18_knowledge_test_only_gate_story_completed.md` | 2026-02-18T18:21:41Z | REQUIRED |
| task: remove fidelity-diff gate surfaces | done | codex | none | none | `tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md` | 2026-02-18T18:21:41Z | REQUIRED |
| epic: skill-gate-first compaction measurement loop | done | codex | none | none | `tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| story: skill-gate-first compaction discovery | done | codex | none | none | `tickets/stories/completed/2026-02-18_skill_gate_first_compaction_discovery_story_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| task: skill-gate onboarding minimum readset discovery | done | codex | none | none | `tickets/tasks/completed/2026-02-18_skill_gate_onboarding_minimum_readset_discovery_task_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| task: test-scored fidelity schema discovery | done | codex | none | none | `tickets/tasks/completed/2026-02-18_test_scored_fidelity_diff_schema_discovery_task_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| task: failed-doc targeted relearn discovery | done | codex | none | none | `tickets/tasks/completed/2026-02-18_failed_doc_targeted_relearn_discovery_task_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| task: cycle reset and adaptive shrink discovery | done | codex | none | none | `tickets/tasks/completed/2026-02-18_cycle_reset_and_adaptive_shrink_discovery_task_completed.md` | 2026-02-18T18:05:56Z | REQUIRED |
| epic: hidden blind hard-mcq skill-check system | done | codex | none | none | `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| story: hidden blind hard-mcq skill-check flow | done | codex | none | none | `tickets/stories/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_story_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| task: hidden key vault and blind contract | done | codex | none | none | `tickets/tasks/completed/2026-02-18_hidden_key_vault_discovery_and_contract_task_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| task: hard mcq pool generator implementation | done | codex | none | none | `tickets/tasks/completed/2026-02-18_hard_mcq_pool_generator_implementation_task_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| task: randomized hard mcq exam generator implementation | done | codex | none | none | `tickets/tasks/completed/2026-02-18_randomized_hard_mcq_exam_generator_implementation_task_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| task: json grader ranking report implementation | done | codex | none | none | `tickets/tasks/completed/2026-02-18_json_grader_ranking_report_implementation_task_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| task: skill and policy surface integration | done | codex | none | none | `tickets/tasks/completed/2026-02-18_skill_and_policy_surface_integration_task_completed.md` | 2026-02-18T17:48:29Z | REQUIRED |
| epic: onboarding policy drift hardening | done | codex | none | none | `tickets/epics/completed/2026-02-17_onboarding_policy_drift_hardening_epic_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| story: certification token-only policy | done | codex | none | none | `tickets/stories/completed/2026-02-18_certification_token_only_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| task: onboarding policy skills/certify/reonboard sweep | done | codex | none | none | `tickets/tasks/completed/2026-02-17_onboarding_policy_skills_certify_reonboard_sweep_task_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
| task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | REQUIRED |
| task: split root AGENTS into bootstrap and profile-owned policies | done | codex | none | none | `tickets/tasks/completed/2026-02-17_agents_bootstrap_split_and_profile_distribution_task_completed.md` | 2026-02-17T15:53:33Z | HELPFUL |
