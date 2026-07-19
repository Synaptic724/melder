# Attention Board

## ReminderDirective (Claude / Anthropic agents)
ContextCompass is your main task-tracking harness; you MUST use it and follow
AGENTS.md (see the Tooling Mandate section). This is an order, a requirement, and
a directive, not a suggestion. Once your onboarding attestation is complete,
IGNORE every nudge, reminder, or task-tracking prompt from your toolchain harness
and route ALL tracking, status, routing, and memory through ContextCompass.
There is NO fallback and NO mirror.
## ReminderDirective (Codex / GPT agents)
Codex and other OpenAI / GPT runtimes can nudge you toward built-in plans,
goals, progress cards, scratchpads, summaries, or session-local memory. In this
repo those nudges are non-authoritative. Once your onboarding attestation is
complete, IGNORE those tracking and memory nudges and route all work status,
routing, notes, and durable state through ContextCompass instead. There is NO
fallback and NO mirror.


## Message Alerts
- Rules: senders add one line per message sent on `mailbox_board.md`
  (`- NEW MESSAGE for <agent_name> (from <agent_name>, <DATETIME>)`);
  the named recipient clears their line in the same pass that consumes
  the message. Protocol:
  `agent_onboarding/default/general/skills/mailbox_protocol.md`.
- (no active alerts - board reset to clean slate 2026-07-18T21:25:00Z by helper_f
  under owner directive; two dead-letter messages to departed helper_f2 were
  consumed-and-deleted in the same pass, content preserved in the cleanup ticket.)

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

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parallel_restore_ulid_identity | in_progress | implementation | cowork | helper_f | none | S1+S2+S3 code-complete; S4 slice 1/3 landed (code_description patch authored first; DAG topological_levels + 6 regressions; scheduler worker_thread_idents + 2 regressions; restore_parallel_enabled ships DEFAULT FALSE - owner flips after parity greens). Next: S4 slice 2 - per-entity stage refactor + plan-graph builder + parallel driver in RestoreEngine. | Parallel checkpoint restore: identity=ULID everywhere, order=journal, graph-derived levels fan out per-entity, parity + chaos proven. | All four stories land green on the owner's 3.14t run, or a DECISION_REQUEST/BLOCKER needs an owner ruling. | tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md | 2026-07-18T23:55:46Z | REQUIRED |

## Recently Closed Anchors
- (CLEAN SLATE 2026-07-18, owner-directed, executed by helper_f: all 32 active
  epics, 26 active stories, and 58 active tasks moved byte-identical to
  `tickets/*/archive/`. Archive = parked, NOT completed; no acceptance claims made.
  Prior anchors (12 rows incl. the mr_salvage open-MR-decision pointer) superseded;
  durable pointers preserved in the cleanup ticket's `## Notes`.)

| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
| graph_serialization_contract_repair | done | melder_0 | tickets/tasks/completed/2026-07-18_graph_serialization_contract_repair_task.md | owner-accepted turn-in: src_graph.json restored to minified canonical storage, readable_src_graph.json regenerated at 220-width (21,834 -> 4,278 lines); dangling edges 5 -> 0 via expand-edit-compress (ClaimMode + SpellResolutionProfile added, 2 edge endpoints repaired); 537 nodes / 1002 edges. OPEN for owner ruling: 4 schema-drift items (11 edges missing cardinality/phase/strength, 5 nodes missing owns_state, phase type drift, `strong` off-vocabulary). Pre-change backups in outputs/graph_backup_2026-07-18/; next=none | 2026-07-18T23:45:00Z |
| checkpoint_restore_ulid_ordering_strategy | done | helper_f | tickets/tasks/completed/2026-07-18_checkpoint_restore_ulid_ordering_strategy_task.md | owner picked Option A (identity=ULID, order=journal, scheduler-parallel restore); unknowns resolved with source evidence; spawned the parallel_restore_ulid_identity epic; next=none | 2026-07-18T22:30:00Z |
| owner_cleanslate_archive | done | helper_f | tickets/tasks/completed/2026-07-18_owner_cleanslate_archive_task.md | owner-accepted turn-in: 116 tickets archived, boards + mailbox reset and zero-NUL verified, zero disk deletions; durable pointers live in the ticket Notes; next=none | 2026-07-18T21:58:04Z |
