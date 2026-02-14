# active_pointerboard

Purpose
- Keep a single, compact routing view of active work.
- Make post-compaction re-entry fast without replacing ticket detail.
- Prevent "what am I working on?" ambiguity.

Canonical board path
- `context_compass/attention_board.md`

Scope
- Pointer data only.
- No deep analysis, no full history replay, no speculative claims.
- Detailed context remains in ticket files.

Required columns
- `work_item`: short active event label.
- `status`: `ready` | `in_progress` | `blocked` | `review`.
- `owner`: current executor (for now usually `codex`).
- `blocker`: concrete blocker or `none`.
- `next`: one concrete next action.
- `ticket`: canonical ticket path.
- `updated`: `YYYY-MM-DD`.
- `reread`: `REQUIRED` | `HELPFUL`.

Update triggers (mandatory)
1) When a work item changes status.
2) When blocker state changes.
3) Before compaction/handoff.
4) Immediately after re-onboarding if board is stale.

Operating rules
- Pointer board never overrides ticket truth.
- Every row must map to exactly one canonical ticket path.
- Keep row text short and operational.
- If a claim is uncertain, mark it in the ticket `Unknowns`, not on this board.

Re-entry protocol
1) Open `context_compass/attention_board.md`.
2) Read rows with `reread=REQUIRED`.
3) Open linked ticket(s) and resume from `next`.

Anti-patterns
- Using board as a second ticket system.
- Copying long narrative into rows.
- Leaving stale `in_progress` rows after handoff.

References
- `context_compass/WORKFLOW.md`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/agent/general/skills/memory_management.md`
- `context_compass/agent_onboarding/agent/general/skills/reactive_documentation.md`
- `context_compass/agent_onboarding/agent/general/skills/active_documentation.md`
