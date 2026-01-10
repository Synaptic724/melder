# agent_lifecycle

Purpose
- Define how to create, check in, check out, archive, and delete agent records and worklists.

Rules
- Use ToolCommandAPI command `agent_manage` for lifecycle changes.
- Use ToolCommandAPI command `agent_checkin` at session start.
- Use ToolCommandAPI command `agent_checkout` at session end or when handing off work.
- Use a user-defined agent_id supplied by the user; if the id is missing or uncertain (e.g., after context compaction), stop and ask before running tools.
- Only generate an agent id when the user explicitly requests it.
- Do not edit self_context or worklist records manually.
- Archive before deletion when you need a record of past work.
- Keep per-agent queues separate from the global queue.
- Only agent_checkin/agent_checkout/agent_manage update agent profiles.

Commands
- Generate a session agent id (only if the user explicitly requests it): ToolCommandAPI command `agent_id`.
- Create agent records: ToolCommandAPI command `agent_manage` (action=create).
- Archive agent records: ToolCommandAPI command `agent_manage` (action=archive).
- Delete agent records: ToolCommandAPI command `agent_manage` (action=delete).
- When acting on another agent, set payload field owner_id to record the actor.
- Check in (mark active): ToolCommandAPI command `agent_checkin`.
- Check out (mark inactive): ToolCommandAPI command `agent_checkout`.
- Add a work item to a per-agent queue: ToolCommandAPI command `work_queue_add`.
- Move an agent work item into branch queues: ToolCommandAPI command `work_item_agent_to_branch`.
- Move an agent work item into global queues: ToolCommandAPI command `work_item_agent_to_global`.

Worklists
- Per-agent queue lives in SQLite user.db table `agent_work_queue` with items in `agent_work_items`.
- Agent profile lives in SQLite user.db table: `agent_profile` (with certification and last command child tables).
- Agent metadata (agent_kind, model_name, runtime, agent_role) is stored in the profile.
- Certification state lives in profile.certification_state.
- Branch task queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- Agents may have permissions to act on per-agent tasks only; confirm before pulling from global queues.

Example
- SQLite user.db table `agent_work_queue`
- SQLite user.db table `agent_profile`
