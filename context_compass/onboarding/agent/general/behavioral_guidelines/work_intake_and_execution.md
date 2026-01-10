# work_intake_and_execution

Purpose
- Describe how raw GitHub tickets become epics/stories/tasks and move through work queues.
 - All commands below are ToolCommandAPI commands (execute via `context_compass/workspace/tools/general/tool_execute.py`).

Story steps
1) Intake
   - GitHub tickets land in `context_compass/user/github_intake/tickets/*.md`.

2) Triage to backlog
   - Use ToolCommandAPI command `work_item_add` or `ticket_promote`.
   - Store triaged work in the active branch backlog.

3) Pull shared work into the branch (optional)
   - If an item already exists in global queues, move it into the branch:
     - ToolCommandAPI command `work_item_global_to_branch`.

4) Decompose work
   - Epics -> Stories -> Tasks.
   - Stories must include `parent_work_id` and `root_work_id`.

5) Move to active
   - Use ToolCommandAPI command `work_item_move` to move items from ready to active queues.
   - Optionally add to a per-agent queue with ToolCommandAPI command `work_queue_add`.
   - If work is already in a per-agent queue, move it into branch queues:
     - ToolCommandAPI command `work_item_agent_to_branch`.

6) Execute and update state
   - Update state via ToolCommandAPI command `update_state` (work-item) when needed.
   - Close work with ToolCommandAPI command `work_item_close` (moves to completed/denied).

7) Publish to global history (optional)
   - When you want shared history, move branch items to global queues:
     - ToolCommandAPI command `work_item_branch_to_global`.
   - If an agent queue item should be published directly, use:
     - ToolCommandAPI command `work_item_agent_to_global`.

Buckets and tables
- Branch queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- Global queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=global, branch_name null).
- Buckets: backlog, ready, active, completed, denied.
- Kinds: epic, story, task.

Artifacts touched
- `context_compass/user/github_intake/tickets/*.md`
- SQLite user.db tables for branch/global queues.
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.

Tools
- ToolCommandAPI commands: `work_item_add`, `ticket_promote`, `work_item_move`,
  `work_item_global_to_branch`, `work_item_branch_to_global`, `work_queue_add`,
  `work_item_agent_to_branch`, `work_item_agent_to_global`, `update_state`, `work_item_close`.

References
- `context_compass/onboarding/agent/general/skills/work_management.md`
