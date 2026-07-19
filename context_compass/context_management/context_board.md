# Context Board

Purpose
- Canonical index of active context-management associations.
- Track reusable reread packs linked to tickets.
- Keep `attention_board.md` ticket-only and free of context-artifact paths.

Scope rules
- `attention_board.md` routes tickets only; do not add context artifact paths
  there.
- Tickets remain canonical execution memory; this board is an association
  index for derived context packs.
- Add rows only when a ticket sets `CONTEXT_MANAGEMENT_REQUIRED: true`.
- Every context row must include:
  - `context_id`
  - `ticket`
  - `context_artifact_path`
  - `agent_name`

## Active Context Links
| context_id | ticket | context_artifact_path | context_type | owner | agent_name | status | next | updated_at | reread |
|---|---|---|---|---|---|---|---|---|---|

## Active Context Notes
- DATETIME: 2026-06-03T12:23:49Z
  TYPE: FACT
  CLAIM: This board starts empty by design. Context management is optional and
    should only be populated when a ticket explicitly opts into it.
  NEXT: add rows only when a ticket sets `CONTEXT_MANAGEMENT_REQUIRED: true`,
    points at one or more `CONTEXT_ID` values, and links one or more context
    artifacts through those ids.
  REREAD: REQUIRED

## Recently Cleared Context Links
| context_id | ticket | context_artifact_path | reason | cleared_at |
|---|---|---|---|---|
| CTX-2026-06-07-phase10-solo-and-many-only-discovery | tickets/stories/archive/2026-06-06_phase10_solo_and_many_only_discovery_story.md | context_management/artifacts/2026-06-07_phase10_solo_and_many_only_discovery_context.md | owner clean-slate 2026-07-18: owning story archived; context artifact retained on disk | 2026-07-18T21:25:00Z |
