
# compacting_differential_board

Purpose
- Measure compaction retention quality per compaction cycle.
- Improve compaction-cache retention empirically (from measured misses, not intuition).
- Preserve **1:1 operational truth** for P0/P1 claims across compactions.

Core rule (non-negotiable)
- Each row is one **atomic retention claim**.
- Do NOT store paragraph blobs.
- Do NOT merge multiple dependencies into one claim.
- If a claim is complex, split it.

Important constraint
- Repository artifacts remain the durable source of truth.
- The compaction summary is a volatile cache that can carry P0/P1 claims across a reset.
- The cache is **not authoritative** until verified via Diff-Onboarding.

Security and privacy (non-negotiable)
- Never store secrets, credentials, tokens, private keys, or sensitive identifiers.
- If a claim depends on a secret value, record only a redacted placeholder and point to the secure source.

Board data model (one row = one claim)
Each row is one atomic retention item.

| cycle_id | claim_id | priority | source_doc_path | source_doc_title | evidence_path | pre_read_recall | ground_truth | diff_type | distortion_class | impact | next_compaction_hint | status | streak_retained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Field meanings
- `cycle_id`: Unique id for one compaction/re-entry cycle (ISO-8601 timestamp recommended).
- `claim_id`: Stable id; never reused. Format: `C-P0-001`, `C-P1-042`, ...
- `priority`: `P0` | `P1` | `P2`.
  - `P0`: execution-blocking if wrong.
  - `P1`: materially impacts correctness/quality; not always blocking.
  - `P2`: useful context; lowest priority for cache retention.
- `source_doc_path`: Canonical repo-relative source-of-truth path.
- `source_doc_title`: Human title of the source doc (stable label).
- `evidence_path`: Evidence pointer(s) supporting `ground_truth` (`path:start-end`).
- `pre_read_recall`: What the agent believes **before** rereading `source_doc_path`.
- `ground_truth`: Short doc-backed truth (paraphrase; keep it checkable).
- `diff_type`: `retained_exact` | `retained_paraphrase` | `distorted` | `dropped`.
- `distortion_class`: `value` | `scope` | `dependency` | `sequence` | `policy`.
- `impact`: Why this miss matters (what breaks or what wrong action happens).
- `next_compaction_hint`: How to write the next compaction summary to retain this correctly.
- `status`: `open` | `improving` | `stable`.
- `streak_retained`: Consecutive cycles with `diff_type` in `{retained_exact, retained_paraphrase}`.

Active claims board
Only `open`/`improving` rows live here. Keep this section small.

| cycle_id | claim_id | priority | source_doc_path | source_doc_title | evidence_path | pre_read_recall | ground_truth | diff_type | distortion_class | impact | next_compaction_hint | status | streak_retained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Cycle metrics log
For each compaction/re-entry cycle, record the metrics block below.

Cycle metrics (required)
- `P0_retention_rate = retained(P0) / total(P0)`
- `P0_critical_loss_count = distorted_or_dropped(P0)`
- `P1_retention_rate = retained(P1) / total(P1)`
- `distortion_rate_total = distorted_or_dropped(all) / total(all)`
- `resume_correctness`: were the first next-actions still correct? (`true`|`false`)

Gates (default pass conditions)
The loop is considered healthy only when all are true:

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

- `P0_retention_rate >= 0.98`
- `P0_critical_loss_count == 0`
- achieved for `2` consecutive cycles

Adaptation rules (mandatory)
- If `dropped`: raise to `P0` next cycle and simplify claim wording.
- If `distorted`: split into smaller atomic claims (one dependency per claim).
- If retained for `streak_retained >= 3`: may demote `P0` -> `P1` (never demote policy-gate claims).
- If a source doc changes materially (hash/LOC/ticket evidence moves): reset affected claims to `open`
  and `streak_retained = 0`.

References
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
