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
- During ticket closure, run deterministic board sync (remove/replace active rows, prune stale details, add compact closed anchor, cap anchors).

Attention detail notation (required for non-empty entries)
- `DATETIME`: ISO-8601 UTC timestamp for the detail entry.
- `TYPE`: one allowed type from the list above.
- `CLAIM`: concise routing-relevant claim.
- `EVIDENCE`: one or more `path:start_line-end_line` pointers.
- `IMPACT`: what this changes for active execution.
- `NEXT`: the immediate next action.
- `SWITCH_TRIGGER`: explicit condition to rotate active routing.
- `RESUME_HIERARCHY`: compact resume chain (`task -> story -> epic`).
- `REREAD`: `REQUIRED` or `HELPFUL`.

## Active Items
| work_item | status | mode | owner | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|---|---|---|
| phase12 codegen second implementation tranche | in_progress | implementation | codex | none | optimize targeted override path (`patch_maps` + overrides executor dispatch) | reduce targeted/mixed non-spellspace means after tranche 1 mixed results | pinned rerun shows targeted and mixed mean improvements vs baseline | tickets/stories/2026-02-18_codegen_baseline_and_hotspot_map_story.md | 2026-02-18T10:28:35Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T10:28:35Z
  TYPE: PLAN
  CLAIM: Tranche 1 patch landed and measured; routing advances to tranche 2 because targeted/mixed outcomes still need improvement.
  EVIDENCE:
  - tickets/tasks/2026-02-18_creation_context_override_dispatch_micro_optimization_task.md:107-126
  - tickets/stories/2026-02-18_codegen_baseline_and_hotspot_map_story.md:135-144
  IMPACT: Implementation continues with focus on `patch_maps` and overrides executor path rather than additional front-door tweaks.
  NEXT: Implement targeted override path optimizations and rerun pinned benchmarks.
  SWITCH_TRIGGER: tranche 2 patch + pinned rerun evidence show targeted and mixed mean gains.
  RESUME_HIERARCHY: task -> story -> epic
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| board cleanup: bulk closure set | done | codex | none | none | `attention_board.md` | 2026-02-17T00:00:00Z | REQUIRED |
