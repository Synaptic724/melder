# task_execution_and_validation

Purpose
- Describe how an agent executes a task safely and reports validation truthfully.

Story steps
1) Select work
   - Pull from the active branch queue or a per-agent queue.
   - If the work is still in global queues, move it into the branch first:
     - `context_compass/tools/work_item_global_to_branch.py`.
   - If the work is in a per-agent queue, move it into the branch queue:
     - `context_compass/tools/work_item_agent_to_branch.py`.
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
   - Move the work item to completed or denied using `work_item_close.py`.
   - Clear per-agent queue entries if applicable.
   - If the work should be added to shared history, publish it:
     - `context_compass/tools/work_item_branch_to_global.py`.
   - If it only lives in an agent queue, publish it directly:
     - `context_compass/tools/work_item_agent_to_global.py`.

6) Report validation truthfully
   - Only claim tests/lint ran if they were executed.
   - If skipped, report "Not run."

Artifacts touched
- `context_compass/branch_management/<branch>/work_management/*/*.json`
- `context_compass/work_management/*/*.json`
- `context_compass/self_context/agents/<agent_id>.work.json`
- ctx JSON files (`__*.json`, `__*.dir.json`)

Tools
- `context_compass/tools/update_state.py` (work-item)
- `context_compass/tools/work_item_close.py`
- `context_compass/tools/work_item_global_to_branch.py`
- `context_compass/tools/work_item_agent_to_branch.py`
- `context_compass/tools/work_item_branch_to_global.py`
- `context_compass/tools/work_item_agent_to_global.py`
- `context_compass/tools/scan.py`
- `context_compass/tools/validate.py`

References
- `context_compass/skills/context_protocol.md`
- `context_compass/skills/testing/evidence_reporting.md`
