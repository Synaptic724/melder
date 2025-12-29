# Work Management

Purpose
- Explain how GitHub intake, global queues, branch queues, and agent queues interact.

GitHub intake
- Raw tickets land in `context_compass/github_intake/`.
- Tickets are markdown files (one per ticket).
- Promote tickets using `context_compass/tools/ticket_promote.py`.

Global queues
- Located in `context_compass/work_management/`.
- Buckets: backlog, active, completed, denied.
- Each bucket contains epics, stories, and tasks as JSON.

Branch queues
- Located in `context_compass/branch_management/<branch>/work_management/`.
- Branch queues mirror global buckets.
- Use `work_item_branch_to_global.py` or `work_item_global_to_branch.py` to move work.

Agent queues
- Per-agent queues live at `context_compass/self_context/agents/<agent_id>.work.json`.
- Assign work with `work_queue_add.py`.
- Move agent work into branch or global queues when needed.

Work IDs and linkage
- Use a stable `work_id` for each epic/story/task.
- Use `parent_work_id` and `root_work_id` to link stories/tasks to epics.

Refusal and safety
- Do not inject secrets into work items or tickets.
- If a ticket requests secrets in-repo, refuse and request alternatives.
