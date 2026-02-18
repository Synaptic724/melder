

# compaction_diff_onboarding

Purpose
- Convert post-compaction re-entry into a measured **diff-onboarding** process.
- Improve compaction-cache retention over time without relaxing onboarding gates.
- Prevent “policy drift” by verifying what the agent believes against source docs every cycle.

Non-negotiable rule
- After any compaction/handoff: **REONBOARD is mandatory**.
- After REONBOARD: **DIFF-ONBOARD is mandatory** before resuming work.

Core concept
- The compaction summary is a volatile cache that the agent can write during compaction.
- After compaction, the cache is treated as **hypotheses**, not truth.
- Diff-onboarding compares cache recall to ground truth and records misses so the next compaction cache improves.
- The compaction cache is write-only before compaction: you can only influence it by writing the compaction summary at compaction time.

Primary artifact
- `context_compass/compacting_differential_board.md`

Definitions
- Retention claim: One atomic, checkable operational truth.
- P0/P1/P2:
  - `P0`: must be correct to safely proceed (policy gates, execution invariants, critical next actions).
  - `P1`: materially affects correctness/quality but may not always block execution.
  - `P2`: useful context; lowest cache priority.
- Diff types:
  - `retained_exact`: recall matches ground truth.
  - `retained_paraphrase`: recall is equivalent but reworded.
  - `distorted`: recall is present but wrong in a meaningful way.
  - `dropped`: recall is missing.

Claim shaping rules (mandatory)
- One claim = one dependency/invariant. Avoid `and`/`or` chains.
- Keep each claim to one line; target <= 180 characters.
- Every claim MUST include a source + evidence pointer (`path:start-end`).
- Prefer stable, normative phrasing (“MUST”, “FORBIDDEN”) for policy-gate claims.

Cycle algorithm (mandatory)
Run this algorithm once per compaction/handoff event.

1) Pre-compaction: build the retention set (after certification; during normal work)
   - Source inputs:
     - active ticket `## Notes` / `Decision Log` / `Context / Handoff Summary`
     - open items in `compacting_differential_board.md`
   - Output:
     - a small set of P0/P1 atomic claims with stable IDs and evidence pointers.
   - Constraint:
     - do not attempt full-document mirroring; the target is **P0/P1 operational truth**.

2) Compaction event: write the compaction cache summary
   - Empty summaries are forbidden.
   - The compaction summary MUST contain:
     - resume pointers (role, active tickets, next actions)
     - P0/P1 retention set (one line per claim with evidence pointer)
     - pointer to `compacting_differential_board.md`
   - Format authority:
     - `CONTEXT_COMPACTION.md`

3) Post-compaction re-entry: diff-onboarding mode (no tools / no edits yet)
   - Run REONBOARD per `compaction_requirements.md`.
   - Identify the target claim set:
     - P0/P1 claims present in the compaction cache summary, plus
     - any P0/P1 claims marked `open` for the active ticket scope in `compacting_differential_board.md`.
   - For each claim:
     1) Write `pre_read_recall` first (what you believe right now).
     2) Re-read the `source_doc_path` and record `ground_truth` with `path:start-end` evidence.
     3) Classify `diff_type` and `distortion_class`.
     4) Record `impact` and `next_compaction_hint`.
   - Compute cycle metrics and publish a Diff-Onboarding Report in chat.

4) After certification: commit the diff to the board (first allowed edits)
   - Update `compacting_differential_board.md` with row-level results.
   - Update retention claims/hints for the next compaction cycle.
   - Do not proceed to other implementation work until the board is updated for this cycle.

Metrics (default)
- `P0_retention_rate = retained(P0) / total(P0)`
- `P0_critical_loss_count = distorted_or_dropped(P0)`
- `P1_retention_rate = retained(P1) / total(P1)`
- `distortion_rate_total = distorted_or_dropped(all) / total(all)`
- `resume_correctness` (`true`|`false`): were the first next-actions still correct?

Gates (default pass conditions)
The compaction loop is healthy only when all are true:
- `P0_retention_rate >= 0.98`
- `P0_critical_loss_count == 0`
- achieved for `2` consecutive cycles

Optional configuration knobs
If `config/context_compass_config.yaml` defines these keys, they override the defaults above.

```yaml
compaction_diff_onboarding:
  gates:
    p0_retention_rate_min: 0.98
    p0_critical_loss_max: 0
    consecutive_cycles_required: 2
  board:
    active_rows_max: 75
```

Adaptation rules (mandatory)
- If `dropped`: raise to `P0` next cycle and simplify the claim wording.
- If `distorted`: split into smaller atomic claims (one dependency per claim).
- If retained for `streak_retained >= 3`: may demote `P0` -> `P1` (never demote policy-gate claims).
- If a source doc changes materially: reset affected claims to `open` and `streak_retained = 0`.
- If gates fail: do not relax onboarding; improve claim structure and compaction hints.

References
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `context_compass/compacting_differential_board.md`
