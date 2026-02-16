# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Keep this board compact and operational.
- Durable history belongs in ticket `## Notes`, not here.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`, `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`, `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`, `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- During ticket closure, run deterministic board sync (remove/replace active rows, prune stale details, add compact closed anchor, cap anchors).

## Active Items
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| story: deep phase12 overrides codegen strategy discovery | in_progress | codex | none | medium-risk discovery iteration 2 completed; queue expanded to 8 candidates, execute `OV-M1` first then `OV-M6` on revert | `context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md` | 2026-02-16 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Benchmark discipline is standardized across all deep codegen stories: pre-test baseline, post-test comparison, immediate revert on failing/non-winning deltas, plus explicit `RESULT` announcement notes.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:122-140, context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:63-84
  IMPACT: Non-overrides and overrides follow-on optimization tasks now share one enforceable benchmark keep/revert contract and outcome-reporting format.
  NEXT: Copy this gate verbatim into each newly opened implementation task from deep story lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: First compact implementation slice completed with a non-winning result and was reverted; story-level routing resumes for next-candidate selection.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_cold_path_helper_extraction_task.md:101-135, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:214-229
  IMPACT: We keep benchmark discipline and avoid retaining regressions while preserving momentum for the next compact iteration.
  NEXT: Select next compact candidate (narrower rank-1 variant or rank-2 metadata snapshot caching) and open a new gated task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Added low/medium/high risk-lane discovery queues to all deep codegen stories with dedicated tasks and a mandatory queue-first iteration rule.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:85-96, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:85-96, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:89-100, context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:1-78, context_compass/tasks/2026-02-16_phase12_no_overrides_low_risk_discovery_task.md:1-78, context_compass/tasks/2026-02-16_phase12_overrides_low_risk_discovery_task.md:1-77
  IMPACT: Iteration entry points are now explicit across all three deep stories, reducing hunt-and-seek overhead.
  NEXT: Execute queued discovery tasks by risk lane, beginning with overrides medium-risk lane unless reprioritized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Each risk-lane task now includes multi-candidate backlog ordering and reusable ops-reference steps, turning the tasks into persistent execution playbooks.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:38-86, context_compass/tasks/2026-02-16_phase12_no_overrides_medium_risk_discovery_task.md:35-85, context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:35-85
  IMPACT: Future iterations can run directly from ticket ops without re-planning overhead.
  NEXT: Start medium-risk overrides with candidate `OV-M1` under the existing benchmark keep/revert gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Completed one additional overrides medium-risk discovery iteration and expanded that queue from five to eight candidates.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:38-55, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:264-271
  IMPACT: We can run several more benchmark-gated attempts without further discovery setup.
  NEXT: Run `OV-M1`; if reverted, continue with `OV-M6`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| story: creationcontext/phase12 discovery refresh | done | codex | none | none | `context_compass/stories/completed/2026-02-15_creationcontext_phase12_codegen_discovery_refresh_story.md` | 2026-02-16 | REQUIRED |
| story: phase12 runtime tightening | done | codex | none | none | `context_compass/stories/completed/2026-02-15_phase12_codegen_runtime_tightening_story.md` | 2026-02-16 | REQUIRED |
| task: phase12/creationcontext codegen optimize wave1 | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md` | 2026-02-16 | REQUIRED |
| task: profile melder overrides graph callchain | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_profile_melder_overrides_graph_callchain_task.md` | 2026-02-16 | REQUIRED |
| task: profile meld hotpath with test shallow all | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md` | 2026-02-16 | REQUIRED |
| epic: jit/aot phase split configuration | done | codex | none | none | `context_compass/epics/completed/2026-02-14_jit_aot_phase_split_configuration_epic.md` | 2026-02-15 | REQUIRED |
| story: jit/aot runtime phase resolution path | done | codex | none | none | `context_compass/stories/completed/2026-02-14_jit_aot_runtime_phase_resolution_path_story.md` | 2026-02-15 | REQUIRED |
