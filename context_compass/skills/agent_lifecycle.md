# agent_lifecycle

Purpose
- Define how to create, check in, check out, archive, and delete agent records and worklists.

Rules
- Use context_compass/tools/agent_manage.py for lifecycle changes.
- Use context_compass/tools/agent_checkin.py at session start.
- Use context_compass/tools/agent_checkout.py at session end or when handing off work.
- Do not edit self_context or worklist files manually.
- Archive before deletion when you need a record of past work.
- Keep per-agent queues separate from the global queue.
- Every context_compass tool invocation must update agent heartbeat state.
- Cleanup scripts run automatically on each tool invocation.

Commands
- Generate a session agent id (optional helper):
  python context_compass/tools/agent_id.py --prefix agent
- Create agent files:
  python context_compass/tools/agent_manage.py create --repo-root . --agent-id <agent_id>
- Archive agent files:
  python context_compass/tools/agent_manage.py archive --repo-root . --agent-id <agent_id>
- Delete agent files:
  python context_compass/tools/agent_manage.py delete --repo-root . --agent-id <agent_id>
- When acting on another agent, pass --owner-id to record the actor heartbeat.
- Check in (start heartbeat):
  python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-kind <kind> --model-name <model> --runtime <runtime>
- Check out (stop heartbeat):
  python context_compass/tools/agent_checkout.py --repo-root . --agent-id <agent_id>
- Run cleanup scripts directly (rare; normally automatic):
  python context_compass/tools/agent_cleanup.py --repo-root . --agent-id <agent_id>
- Sweep agent profiles and count active agents:
  python context_compass/tools/agent_sweep.py --repo-root . --agent-id <agent_id>
- Add a work item to a per-agent queue:
  python context_compass/tools/work_queue_add.py --repo-root . --agent-id <agent_id> --work-id <work_id> --kind <kind> --target-path <path> --ctx-path <path> --root-work-id <root> --parent-work-id <parent>
- Move an agent work item into branch queues:
  python context_compass/tools/work_item_agent_to_branch.py --repo-root . --agent-id <agent_id> --work-id <work_id> --dest-bucket <bucket>
- Move an agent work item into global queues:
  python context_compass/tools/work_item_agent_to_global.py --repo-root . --agent-id <agent_id> --work-id <work_id> --dest-bucket <bucket>

Worklists
- Per-agent queue lives at: context_compass/self_context/agents/<agent_id>.work.json
- Agent profile (heartbeat) lives at: context_compass/self_context/agents/<agent_id>.profile.json
- Agent metadata (agent_kind, model_name, runtime) is stored in the profile.
- Certification state lives in profile.certification_state.
- Branch task queues live under context_compass/branch_management/<branch>/work_management/ (epics/stories/tasks).
- Agents may have permissions to act on per-agent tasks only; confirm before pulling from global queues.

Staleness and archive policy
- agent_heartbeat_stale_seconds: mark stale in the profile.
- agent_archive_after_seconds: archive self/work/profile after threshold.
- Configure in context_compass/config/policies.json.
- Defaults: 4 hours stale (14400s), 24 hours archive (86400s).
- Cleanup requeues any active work items owned by stale agents back to backlog.

Cleanup script contract
- Location: context_compass/tools/cleanup_agents/.
- Each script must implement cleanup(repo_root, agent_id, now=None).
- Each script must accept --repo-root and --agent-id for direct CLI use.

Example
- context_compass/self_context/agents/example.work.json
- context_compass/self_context/agents/example.profile.json
