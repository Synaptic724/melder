# work_management

Purpose
- Track Epics, Stories, and Tasks across backlog, active, completed, and denied states.
- Provide a machine-owned global queue that can be promoted from branch queues.

Directory layout
- context_compass/work_management/backlog/
- context_compass/work_management/active/
- context_compass/work_management/completed/
- context_compass/work_management/denied/
- Branch queues live under context_compass/branch_management/<branch>/work_management/.

Files in each state (minified JSON, machine-owned)
- epics.json
- stories.json
- tasks.json

Work item requirements
- work_id is the uniform identifier for epics/stories/tasks.
- kind is required (epic/story/task or a more specific type).
- parent_work_id and root_work_id must be set (use null for top-level).

Workflow
- Triage tickets into the active branch backlog.
- Work within branch queues during feature work.
- Promote finished work into the global queues when you want shared history.

Tooling
- context_compass/tools/work_item_add.py can add epics/stories/tasks to any bucket.
- Use --ticket-path to link back to the intake markdown.
- context_compass/tools/work_item_move.py moves work items between backlog/active/completed/denied.
- context_compass/tools/ticket_promote.py promotes a ticket into a root work item (optional child plan).
- context_compass/tools/work_item_close.py closes work items and clears per-agent queues.
- context_compass/tools/work_item_global_to_branch.py moves items from global queues to branch queues.
- context_compass/tools/work_item_branch_to_global.py moves items from branch queues to global queues.
- context_compass/tools/work_item_agent_to_branch.py moves items from agent queues to branch queues.
- context_compass/tools/work_item_agent_to_global.py moves items from agent queues to global queues.

Lineage rules
- story items must include parent_work_id.
- tasks may be root or child; set parent_work_id/root_work_id when derived from an epic/story.

Notes
- JSON must be minified (canonical writer) and written atomically with locks.
- Global queue locks live under context_compass/work_management/locks.
