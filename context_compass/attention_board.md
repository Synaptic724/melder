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
| epic: creationcontext/phase12 codegen optimization | in_progress | codex | none | deep discovery stories opened for all 3 codegen modules; continue option ranking and experiment planning per story | `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md` | 2026-02-16 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Opened three deep discovery stories, one per target codegen module (`creation_context_codegen.py`, `phase12_no_overrides_executor.py`, `phase12_overrides_executor.py`).
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-36, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-36, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-36
  IMPACT: Deep strategy discovery is now explicitly separated by module instead of a single broad ticket.
  NEXT: Continue discovery notes and option ranking in each story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Deep findings are now captured against unconsidered generator internals: CreationContext template matrix compile fan-out, no-overrides monolithic emitted step blocks/transient signature width, and overrides shape-metadata plus inline kwargs/invoke duplication.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:74-100, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:76-102, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:76-110
  IMPACT: Discovery focus has moved from micro runtime tweaks to generator architecture quality.
  NEXT: Convert top ranked strategy options into implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next step is to finish deep option ranking across the three stories and open one implementation task from the top strategy lane.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:88-101, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:188-201
  IMPACT: Keeps epic execution in deep-discovery-first mode before new optimization code edits.
  NEXT: Select the first generator-strategy experiment and create its task ticket.
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
