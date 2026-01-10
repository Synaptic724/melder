# task_execution_and_validation

Purpose
- Describe how an agent executes a task safely and reports validation truthfully.
 - All commands below are ToolCommandAPI commands (execute via `context_compass/workspace/tools/general/tool_execute.py`).

Story steps
1) Select work
   - Pull from the ready branch queue or a per-agent queue.
   - Move ready work into active before you start execution.
   - If the work is still in global queues, move it into the branch first:
     - ToolCommandAPI command `work_item_global_to_branch`.
   - If the work is in a per-agent queue, move it into the branch queue:
     - ToolCommandAPI command `work_item_agent_to_branch`.
   - If required, update the work item state to in_progress.

2) Acquire locks before writes
   - Use lease locks for any ctx/state JSON writes.
   - Always re-read the latest state after acquiring a lock.

3) Perform changes
   - Prefer ctx JSON first, code last.
   - Keep edits narrow and reviewable.
   - Update ctx artifacts for any code changes.

4) Restore freshness
   - Run scan or validate to return freshness_state to fresh.

5) Close work
   - Move the work item to completed or denied using ToolCommandAPI command `work_item_close`.
   - Clear per-agent queue entries if applicable.
   - If the work should be added to shared history, publish it:
     - ToolCommandAPI command `work_item_branch_to_global`.
   - If it only lives in an agent queue, publish it directly:
     - ToolCommandAPI command `work_item_agent_to_global`.

6) Report validation truthfully
   - Only claim tests/lint ran if they were executed.
   - If skipped, report "Not run."

Artifacts touched
- SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- SQLite user.db tables `work_queues` and `work_queue_items` (scope=global, branch_name null).
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.
- ctx JSON files (`__*.json`, `__*.dir.json`)

Tools
- ToolCommandAPI commands: `update_state`, `work_item_close`, `work_item_global_to_branch`,
  `work_item_agent_to_branch`, `work_item_branch_to_global`, `work_item_agent_to_global`,
  `scan`, `validate`.

References
- `context_compass/onboarding/agent/general/skills/context_protocol.md`
- `context_compass/onboarding/agent/general/skills/testing/evidence_reporting.md`
