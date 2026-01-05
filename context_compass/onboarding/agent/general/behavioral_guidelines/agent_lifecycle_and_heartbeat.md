# agent_lifecycle

Purpose
- Define the lifecycle of an agent record and how explicit checkin/checkout works.

Story steps
1) Create or reuse an agent id
   - Generate with `context_compass/system/ai_restricted/agent_management/agent_id.py` if needed.
   - Create files via `context_compass/system/ai_restricted/agent_management/agent_manage.py create`.

2) Check in and mark active
   - `context_compass/system/ai_restricted/agent_management/agent_checkin.py` marks the agent profile active.
   - Optional metadata recorded: agent_kind, model_name, runtime.
   - Optional role label recorded: agent_role.
   - Tool invocations do not update the profile automatically.

3) Work session updates
   - Per-agent work queue lives in SQLite user.db table `agent_work_queue` with items in `agent_work_items`.
   - Move work out of per-agent queues when needed:
     - `context_compass/system/ai_restricted/work_management/work_item_agent_to_branch.py` (assign to branch work).
     - `context_compass/system/ai_restricted/work_management/work_item_agent_to_global.py` (publish to shared history).
4) Check out when done
   - `context_compass/system/ai_restricted/agent_management/agent_checkout.py` marks the agent inactive.

5) Archive or delete
   - Use `context_compass/system/ai_restricted/agent_management/agent_manage.py archive` for audit retention.
   - Use `context_compass/system/ai_restricted/agent_management/agent_manage.py delete` only after archiving.

Artifacts touched
- SQLite user.db table: `agent_profile` (with certification and last command child tables).
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.

Tools
- `context_compass/system/ai_restricted/agent_management/agent_id.py`
- `context_compass/system/ai_restricted/agent_management/agent_manage.py`
- `context_compass/system/ai_restricted/agent_management/agent_checkin.py`
- `context_compass/system/ai_restricted/agent_management/agent_checkout.py`

References
- `context_compass/onboarding/agent/general/skills/agent_lifecycle.md`
