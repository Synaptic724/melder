# Work Management

Purpose
- Explain how GitHub intake, global queues, branch queues, and agent queues interact.

Quick start (bulk move)
- Use ToolCommandAPI command `work_item_bulk_move`.
- Use `tool_registry_describe` to confirm payload fields (source_bucket, dest_bucket, work_type, work_ids/quantity).

GitHub intake
- Raw tickets land in `context_compass/user/github_intake/`.
- Tickets are markdown files (one per ticket).
- Promote tickets using ToolCommandAPI command `ticket_promote`.

Global queues
- SQLite user.db tables `work_queues` and `work_queue_items` (plus reason/lease child tables).
- Global queues use scope=global with branch_name null.
- Buckets: ready, backlog, active, completed, denied.
- Each queue stores epics, stories, and tasks in SQLite rows.

Branch queues
- SQLite user.db tables `work_queues` and `work_queue_items` (plus reason/lease child tables).
- Branch queues use scope=branch with branch_name set.
- Branch queues mirror global buckets.
- Use ToolCommandAPI commands `work_item_branch_to_global` or `work_item_global_to_branch` to move work.

Agent queues
- Per-agent queues live in SQLite user.db table `agent_work_queue` with items in `agent_work_items` (plus reason/lease child tables).
- Assign work with ToolCommandAPI command `work_queue_add`.
- Move agent work into branch or global queues when needed.

Work item moves
- Move individual items with ToolCommandAPI command `work_item_move`.
- Bulk move with ToolCommandAPI command `work_item_bulk_move`.
- Bulk move runs against the current branch queues and defaults work_type to `task` unless overridden.
- Use payload fields work_type (epic/story/task) or kind to infer the queue type.
- Use payload field state to update the work item state as part of the move.
- Bulk move continues on per-item errors and reports moved vs failed ids.

Work IDs and linkage
- Work ids are generated automatically when omitted (8-char alphanumeric).
- Use `parent_work_id` and `root_work_id` to link stories/tasks to epics.

Troubleshooting
- "quantity is required when work_ids is not provided": add `--quantity` or pass explicit `--work-ids`.
- "Invalid work_type" or "Invalid work kind": use epic/story/task values.
- Hard work_mode requires `--work-id`; pick a stable id (often the first moved work id or the originating ticket id).

Refusal and safety
- Do not inject secrets into work items or tickets.
- If a ticket requests secrets in-repo, refuse and request alternatives.
