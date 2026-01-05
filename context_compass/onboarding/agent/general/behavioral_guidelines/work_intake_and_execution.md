# work_intake_and_execution

Purpose
- Describe how raw GitHub tickets become epics/stories/tasks and move through work queues.

Story steps
1) Intake
   - GitHub tickets land in `context_compass/user/github_intake/tickets/*.md`.

2) Triage to backlog
   - Use `context_compass/system/ai_restricted/work_management/work_item_add.py` or `context_compass/system/ai_restricted/work_management/ticket_promote.py`.
   - Store triaged work in the active branch backlog.

3) Pull shared work into the branch (optional)
   - If an item already exists in global queues, move it into the branch:
     - `context_compass/system/ai_restricted/work_management/work_item_global_to_branch.py`.

4) Decompose work
   - Epics -> Stories -> Tasks.
   - Stories must include `parent_work_id` and `root_work_id`.

5) Move to active
   - Use `context_compass/system/ai_restricted/work_management/work_item_move.py` to move items from ready to active queues.
   - Optionally add to a per-agent queue with `context_compass/system/ai_restricted/work_management/work_queue_add.py`.
   - If work is already in a per-agent queue, move it into branch queues:
     - `context_compass/system/ai_restricted/work_management/work_item_agent_to_branch.py`.

6) Execute and update state
   - Update state via `context_compass/system/ai_restricted/system_management/update_state.py work-item` when needed.
   - Close work with `context_compass/system/ai_restricted/work_management/work_item_close.py` (moves to completed/denied).

7) Publish to global history (optional)
   - When you want shared history, move branch items to global queues:
     - `context_compass/system/ai_restricted/work_management/work_item_branch_to_global.py`.
   - If an agent queue item should be published directly, use:
     - `context_compass/system/ai_restricted/work_management/work_item_agent_to_global.py`.

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
- `context_compass/system/ai_restricted/work_management/work_item_add.py`
- `context_compass/system/ai_restricted/work_management/ticket_promote.py`
- `context_compass/system/ai_restricted/work_management/work_item_move.py`
- `context_compass/system/ai_restricted/work_management/work_item_global_to_branch.py`
- `context_compass/system/ai_restricted/work_management/work_item_branch_to_global.py`
- `context_compass/system/ai_restricted/work_management/work_queue_add.py`
- `context_compass/system/ai_restricted/work_management/work_item_agent_to_branch.py`
- `context_compass/system/ai_restricted/work_management/work_item_agent_to_global.py`
- `context_compass/system/ai_restricted/system_management/update_state.py`
- `context_compass/system/ai_restricted/work_management/work_item_close.py`

References
- `context_compass/onboarding/agent/general/skills/work_management.md`
