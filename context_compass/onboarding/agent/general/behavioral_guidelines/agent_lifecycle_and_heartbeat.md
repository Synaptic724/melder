# agent_lifecycle

Purpose
- Define the lifecycle of an agent record and how explicit checkin/checkout works.
 - All commands below are ToolCommandAPI commands (execute via `context_compass/workspace/tools/general/tool_execute.py`).

Story steps
1) Create or reuse an agent id
   - Use a user-defined agent_id supplied by the user.
   - If the agent_id is missing or uncertain (e.g., after context compaction), stop and ask the user before running tools.
   - Only generate an agent id when the user explicitly requests ToolCommandAPI command `agent_id`.
   - Create files via ToolCommandAPI command `agent_manage`.

2) Check in and mark active
   - ToolCommandAPI command `agent_checkin` marks the agent profile active.
   - Optional metadata recorded: agent_kind, model_name, runtime.
   - Optional role label recorded: agent_role.
   - Tool invocations do not update the profile automatically.

3) Work session updates
   - Per-agent work queue lives in SQLite user.db table `agent_work_queue` with items in `agent_work_items`.
   - Move work out of per-agent queues when needed:
      - ToolCommandAPI command `work_item_agent_to_branch` (assign to branch work).
      - ToolCommandAPI command `work_item_agent_to_global` (publish to shared history).
4) Check out when done
   - ToolCommandAPI command `agent_checkout` marks the agent inactive.

5) Archive or delete
   - Use ToolCommandAPI command `agent_manage` with archive for audit retention.
   - Use ToolCommandAPI command `agent_manage` with delete only after archiving.

Artifacts touched
- SQLite user.db table: `agent_profile` (with certification and last command child tables).
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.

Tools
- ToolCommandAPI commands: `agent_id`, `agent_manage`, `agent_checkin`, `agent_checkout`.

References
- `context_compass/onboarding/agent/general/skills/agent_lifecycle.md`
