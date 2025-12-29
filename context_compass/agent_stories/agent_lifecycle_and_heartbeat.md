# agent_lifecycle_and_heartbeat

Purpose
- Define the lifecycle of an agent record and how heartbeat tracking works.

Story steps
1) Create or reuse an agent id
   - Generate with `context_compass/tools/agent_id.py` if needed.
   - Create files via `context_compass/tools/agent_manage.py create`.

2) Check in and start heartbeat
   - `context_compass/tools/agent_checkin.py` writes active registry + profile.
   - Every tool call updates heartbeat automatically.

3) Work session updates
   - Tool invocations refresh `active_agents.json` and the profile.
   - Per-agent work queue stays at `context_compass/self_context/agents/<agent_id>.work.json`.
   - Move work out of per-agent queues when needed:
     - `context_compass/tools/work_item_agent_to_branch.py` (assign to branch work).
     - `context_compass/tools/work_item_agent_to_global.py` (publish to shared history).

4) Cleanup on each tool run
   - Cleanup scripts run before heartbeat updates.
   - Stale agents are marked and removed from the active registry.

5) Check out when done
   - `context_compass/tools/agent_checkout.py` marks the agent inactive.

6) Archive or delete
   - Use `context_compass/tools/agent_manage.py archive` for audit retention.
   - Use `context_compass/tools/agent_manage.py delete` only after archiving.

Staleness handling
- `agent_heartbeat_stale_seconds` marks agents stale and removes them from active.
- `agent_archive_after_seconds` moves stale agent files into `context_compass/archive/`.
- Cleanup requeues active work items owned by stale agents back to backlog.

Artifacts touched
- `context_compass/self_context/active_agents.json`
- `context_compass/self_context/agents/<agent_id>.profile.json`
- `context_compass/self_context/agents/<agent_id>.work.json`
- `context_compass/archive/`

Tools
- `context_compass/tools/agent_id.py`
- `context_compass/tools/agent_manage.py`
- `context_compass/tools/agent_checkin.py`
- `context_compass/tools/agent_checkout.py`
- `context_compass/tools/agent_cleanup.py`

References
- `context_compass/skills/agent_lifecycle.md`
