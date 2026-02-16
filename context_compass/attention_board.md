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
| task: creationcontext low-risk CC-L2 iteration | blocked | codex | pending keep/revert decision | CC-L2 is implemented and validated; user decision required on mixed but non-overrides-favorable averaged deltas before continuing to CC-L3 | `context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md` | 2026-02-16 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Clean 10k rerun after external benchmark contention shows CC-L2 fast-cycle deltas all improved versus baseline and `overrides/solo` flipped from prior regression to improvement; override lane remains mixed in very small absolute-time slices.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_rerun_clean_2026-02-16_snapshot_summary_2026-02-16_12-32-46.txt:42-52, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt:42-52
  IMPACT: Decision gate should use the clean rerun as primary evidence rather than the contested run.
  NEXT: User selects keep or revert for CC-L2 based on the clean rerun deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - CC-L2 post-test is green and improves non-overrides aggregate means on 10k snapshots, but includes small mixed regressions (fast `wide`, overrides `solo`), so keep/revert direction is required.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:225-234, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt:42-52
  IMPACT: Execution is paused at the decision gate before taking further low-risk candidates.
  NEXT: User selects keep or revert for CC-L2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active routing switched from snapshot-process implementation to CreationContext low-risk iteration `CC-L2` (compile helper dedupe) using the new averaged snapshot gate for pre/post decision quality.
  EVIDENCE: context_compass/tasks/2026-02-16_codegen_snapshot_average_process_task.md:111-117, context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:39-46
  IMPACT: We can immediately apply the new benchmark process to a compact non-overrides-friendly CreationContext change.
  NEXT: Capture averaged prebaseline snapshot for current CC-L2 code shape, patch CC-L2, then run averaged post-test snapshot and compare.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The new non-cProfile snapshot runner is implemented and validated across both normal fast lanes and override lanes, including successful 1000-iteration and 10000-iteration artifact runs.
  EVIDENCE: context_compass/tasks/2026-02-16_codegen_snapshot_average_process_task.md:84-110, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_summary_2026-02-16_12-16-23.txt:1-33, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_10k_2026-02-16_snapshot_summary_2026-02-16_12-16-31.txt:1-33
  IMPACT: Future keep/revert decisions can now use stable averaged snapshots instead of single-run cProfile timings.
  NEXT: Announce the new snapshot command contract in the active ticket and use it for the next pre/post candidate cycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active routing moved from the reverted CC-L1 lane to a dedicated benchmark-process task that builds a non-cProfile averaged snapshot workflow (1000 default, 10000 optional).
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:192-192, context_compass/tasks/2026-02-16_codegen_snapshot_average_process_task.md:1-102
  IMPACT: Benchmark decisions can now use high-repeat averages without profiler overhead while preserving the same fast/overrides lane coverage.
  NEXT: Implement `benchmarks/testing_other_di/run_snapshot_timings.py` and produce smoke artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Benchmark discipline is standardized across all deep codegen stories: pre-test baseline, post-test comparison, `DECISION_REQUEST` escalation on failing/non-winning deltas, plus explicit `RESULT` announcement notes.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:122-140, context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:63-84
  IMPACT: Non-overrides and overrides follow-on optimization tasks now share one enforceable benchmark decision contract with user-directed keep/revert outcomes.
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
  NEXT: Start medium-risk overrides with candidate `OV-M1` under the benchmark decision gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Completed one additional overrides medium-risk discovery iteration and expanded that queue from five to eight candidates.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:38-55, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:264-271
  IMPACT: We can run several more benchmark-gated attempts without further discovery setup.
  NEXT: Run `OV-M1`; if user directs revert, continue with `OV-M6`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active execution switched to high-risk-first per user direction; OV-H1 slice task opened and routed as active work item.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:273-280, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:1-112
  IMPACT: Current iteration now targets the high-risk backlog before medium/low lanes.
  NEXT: Complete OV-H1 pre/post benchmark cycle and publish `RESULT`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - OV-H1 slice 1 failed post-test unit gate and was reverted; active execution moved to OV-H1 slice 2 (narrowed owner-target helper segmentation).
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:121-137, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:1-106
  IMPACT: High-risk-first iteration continues with restored baseline runtime state and a tighter follow-on slice.
  NEXT: Run slice-2 pre-test baseline cadence before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Slice-2 prebaseline cadence completed successfully and is captured for checkpoint comparison.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:108-115, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice2_prebaseline_2026-02-16.txt:1-1954
  IMPACT: Active task is ready for implementation and post-test decision-request evaluation.
  NEXT: Apply narrowed owner-target helper segmentation patch in `phase12_overrides_executor.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active routing switched to CreationContext low-risk candidate `CC-L1` per user direction for one compact iteration.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:38-46, context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:121-128
  IMPACT: Immediate execution focus is now the CreationContext codegen selector dispatch optimization lane.
  NEXT: Capture pre-test baseline cadence for CreationContext unit + fast/overrides benchmarks, then patch `CC-L1`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - CC-L1 post-test cadence is green but non-winning versus retained checkpoint (fast lanes regressed, including `fast_timings_wide` +6.602 ms / +5.98%).
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:156-174, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_summary_2026-02-16.txt:24-32
  IMPACT: Active execution is paused for explicit keep/revert direction per epic benchmark gate policy.
  NEXT: User chooses keep or revert for CC-L1, then execution resumes on that branch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - User selected revert for CC-L1; selector-dispatch map changes were removed and one-pass post-revert validation succeeded.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:195-283, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_postrevert_summary_2026-02-16.txt:1-26
  IMPACT: Runtime is restored to pre-CC-L1 code shape and the low-risk lane can proceed to process improvements.
  NEXT: Build a separate snapshot benchmark process with high-repeat averaging (1000 default, 10000 optional).
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
