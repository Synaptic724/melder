# ticket_closure_attention_sync

Purpose
- Enforce deterministic synchronization between ticket closure and `attention_board.md`.
- Prevent stale routing rows and historical note buildup on the pointer board.

When to use
- Any time a ticket is moved to `tickets/epics/completed/`, `tickets/stories/completed/`, or `tickets/tasks/completed/`.
- Any time a ticket status changes to done/review/blocked and the board row should change.

Deterministic closure sync protocol (mandatory)
1) Identify the closed ticket path (`old_ticket`) and completion date.
2) Open `context_compass/attention_board.md`.
3) In `## Active Items`:
   - If a row points to `old_ticket` and no immediate successor ticket exists, remove the row.
   - If a successor ticket exists, replace the row `ticket`, `status`, `next`, and `updated` values.
4) In `## Active Attention Details`:
   - Remove entries whose `NEXT` or `EVIDENCE` are only about `old_ticket` and no longer route active work.
   - Keep the section focused on current active rows only.
5) In `## Recently Closed Anchors`:
   - Add one compact anchor row for `old_ticket` with status `done` and `next=none`.
   - Keep at most 12 anchor rows; remove oldest rows first when adding a new one.
6) Verify board invariants before saving.

Board invariants (must hold)
- `## Active Items` rows must only reference non-completed tickets.
- Every active row must map to one canonical ticket path.
- `next` text must be one concrete action.
- `## Active Attention Details` must only contain active-routing details.
- Board must remain compact; durable narrative belongs in ticket `## Notes`.

Verification commands
- `rg -n "context_compass/(epics|stories|tasks)/completed/" context_compass/attention_board.md`
- `rg -n "## Active Items|## Active Attention Details|## Recently Closed Anchors" context_compass/attention_board.md`

Anti-patterns
- Leaving closed ticket rows in `## Active Items`.
- Keeping deep historical narratives in board detail section.
- Using board detail section as a duplicate of ticket notes.

References
- `context_compass/WORKFLOW.md`
- `context_compass/agent_onboarding/agent/general/skills/ticketing.md`
- `context_compass/agent_onboarding/agent/general/skills/active_pointerboard.md`

