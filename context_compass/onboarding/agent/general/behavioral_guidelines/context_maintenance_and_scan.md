# context_maintenance_and_scan

Purpose
- Keep directory and file ctx JSON fresh so agents prefer ctx over code.
 - All commands below are ToolCommandAPI commands (execute via `context_compass/workspace/tools/general/tool_execute.py`).

Story steps
1) Scan for staleness
   - Confirm repo_state allows scan (SQLite user.db table `repo_state` keyed by branch_name); if tooling_policy is restricted, stop and request enablement.
   - Run ToolCommandAPI command `scan` or read the latest scan output.
   - Scanner computes code/subtree hashes and updates ctx computed fields.
   - Missing/stale/needs_review/blocked ctx items become tasks.
   - Architecture/component contexts are checked against their citation matrix and can emit resurvey tasks.

2) Resolve ctx tasks first
   - Generated tasks land in the ready branch queue.
   - Move ready items into active before executing them.
   - Refresh or regenerate ctx before feature work.
   - Refresh file ctx before regenerating dir ctx; dir ctx is derived from file ctx, not code.

3) Perform feature work
   - Use ctx JSON as primary truth.
   - Use directory ctx as the sole source of structural understanding.
   - If directory ctx is insufficient, stop and refresh dir ctx before proceeding.
   - Open code only when ctx is missing or insufficient.

4) Restore freshness after edits
   - Do not manually edit ctx JSON after code changes.
   - Run scan to emit refresh tasks, then resolve them.
   - Re-scan or validate so freshness_state returns to fresh.

5) Validate (optional CI)
   - ToolCommandAPI command `validate` checks schema + staleness.

Artifacts touched
- `__<stem>__.json` and `__<dir>__.dir.json`
- SQLite user.db tables `scan_registry` + scan_* (keys: branch_name + scan_id).
- SQLite user.db table `repo_state` (branch_name key).
- SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set, bucket=ready, work_kind=task).

Tools
- ToolCommandAPI commands: `scan`, `validate`, `update_state` (scan metadata).

References
- `context_compass/onboarding/agent/general/skills/context_protocol.md`
- `context_compass/onboarding/agent/general/skills/staleness_protocol.md`
