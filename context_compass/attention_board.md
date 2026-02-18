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
| phase12 codegen measurement reset | in_progress | validation | codex | none | run higher-sample pinned measurement pass before next code edit | reduce false positives from low-sample regressions and pick next hotspot confidently | next candidate change is chosen from higher-confidence benchmark evidence | tickets/stories/2026-02-18_codegen_baseline_and_hotspot_map_story.md | 2026-02-18T10:42:12Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-18T10:42:12Z
  TYPE: PLAN
  CLAIM: Tranche 4 was also reverted; active routing shifts to higher-sample measurement before further edits.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase12_invoke_no_args_fastpath_task.md:106-125
  IMPACT: Next optimization decision should be driven by stronger signal than two 3-sample reruns.
  NEXT: Run pinned benchmark with higher sample count and refresh route ranking.
  SWITCH_TRIGGER: high-sample results identify a new top candidate with acceptable confidence.
  RESUME_HIERARCHY: task -> story -> epic
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| board cleanup: bulk closure set | done | codex | none | none | `attention_board.md` | 2026-02-17T00:00:00Z | REQUIRED |
