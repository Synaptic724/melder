# Work Management

Purpose
- Explain how GitHub intake, global queues, branch queues, and agent queues interact.

GitHub intake
- Raw tickets land in `context_compass/user/github_intake/`.
- Tickets are markdown files (one per ticket).
- Promote tickets using `context_compass/system/ai_restricted/work_management/ticket_promote.py`.
  - Example: `--child-items-json '[{"kind":"task","target_path":"src/pkg/foo.py","ctx_path":"src/pkg/foo.py"}]'`.

Global queues
- SQLite user.db tables `work_queues` and `work_queue_items` (plus reason/lease child tables).
- Global queues use scope=global with branch_name null.
- Buckets: ready, backlog, active, completed, denied.
- Each queue stores epics, stories, and tasks in SQLite rows.

Branch queues
- SQLite user.db tables `work_queues` and `work_queue_items` (plus reason/lease child tables).
- Branch queues use scope=branch with branch_name set.
- Branch queues mirror global buckets.
- Use `work_item_branch_to_global.py` or `work_item_global_to_branch.py` to move work.

Agent queues
- Per-agent queues live in SQLite user.db table `agent_work_queue` with items in `agent_work_items` (plus reason/lease child tables).
- Assign work with `work_queue_add.py`.
- Move agent work into branch or global queues when needed.

Work item moves
- Move individual items with `context_compass/system/ai_restricted/work_management/work_item_move.py`.
- Bulk move with `context_compass/system/ai_restricted/work_management/work_item_bulk_move.py` using `--work-ids` or `--quantity`.

Work IDs and linkage
- Work ids are generated automatically when omitted (8-char alphanumeric).
- Use `parent_work_id` and `root_work_id` to link stories/tasks to epics.

Refusal and safety
- Do not inject secrets into work items or tickets.
- If a ticket requests secrets in-repo, refuse and request alternatives.
