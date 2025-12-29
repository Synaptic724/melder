# work_management

Purpose
- Define the intake and execution flow for Epics, Stories, and Tasks.
- Keep GitHub intake separate from machine-owned work queues.

Locations
- context_compass/github_intake/tickets/: raw GitHub tickets as .md files.
- context_compass/work_management/: global canonical queues (shared history).
- context_compass/branch_management/<branch>/work_management/backlog/: branch backlog.
- context_compass/branch_management/<branch>/work_management/active/: branch in-flight work.
- context_compass/branch_management/<branch>/work_management/completed/: branch audit trail.
- context_compass/branch_management/<branch>/work_management/denied/: branch rejections.

Files and format
- Each state contains epics.json, stories.json, and tasks.json.
- JSON is machine-owned and must be minified (canonical writer).
- Use the same schema/shape as tasks.schema.json for all three types.
- Work items use work_id (uniform id for epics/stories/tasks) and must include kind.
- Recommended work_id prefixes: epic_, story_, task_.
- parent_work_id and root_work_id are required for all items (use null for top-level).

Workflow
1) Copilot drops new ticket into context_compass/github_intake/tickets/.
2) Human or agent triage moves ticket into branch backlog.
3) Break Epic -> Story -> Task inside backlog.
4) Move items to active/ when work begins.
5) Move items to completed/ or denied/ when finished.
6) Promote branch work items to global queues when you want shared history.

Tooling
- Use context_compass/tools/work_item_add.py to create epics/stories/tasks in any bucket.
- --ticket-path can be supplied to tie the work item back to the intake markdown.
- Use context_compass/tools/work_item_move.py to move items between backlog/active/completed/denied.
- Use context_compass/tools/ticket_promote.py to create a root epic/story/task from a ticket, with optional child plan.
- Use context_compass/tools/work_item_close.py to move items to completed/denied and clear per-agent queues.
- Use context_compass/tools/work_item_global_to_branch.py to pull global items into the active branch.
- Use context_compass/tools/work_item_branch_to_global.py to publish branch items to the global history.
- Use context_compass/tools/work_item_agent_to_branch.py to move agent-owned items into branch queues.
- Use context_compass/tools/work_item_agent_to_global.py to move agent-owned items into global queues.

Lineage rules
- story items must include parent_work_id (they cannot be root items).
- tasks may be root or child; when derived from an epic/story they must set parent_work_id and root_work_id.

Locking
- Any write to branch work_management JSON requires a lock on that file.
- Re-read latest state after acquiring a lock and before writing.
- Write JSON atomically (temp + replace).
- Global queue writes use locks under context_compass/work_management/locks.

Notes
- The scanner emits tasks into the active branch queue.
- Work queue tooling requires work_management feature enabled in context_compass/config/context_compass_configuration.json.
- If work_mode is hard, tools require a work_id for each work action.
