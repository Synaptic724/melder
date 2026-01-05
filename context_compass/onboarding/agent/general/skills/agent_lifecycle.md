# agent_lifecycle

Purpose
- Define how to create, check in, check out, archive, and delete agent records and worklists.

Rules
- Use context_compass/system/ai_restricted/agent_management/agent_manage.py for lifecycle changes.
- Use context_compass/system/ai_restricted/agent_management/agent_checkin.py at session start.
- Use context_compass/system/ai_restricted/agent_management/agent_checkout.py at session end or when handing off work.
- Do not edit self_context or worklist records manually.
- Archive before deletion when you need a record of past work.
- Keep per-agent queues separate from the global queue.
- Only agent_checkin/agent_checkout/agent_manage update agent profiles.

Commands
- Generate a session agent id (optional helper):
  python context_compass/system/ai_restricted/agent_management/agent_id.py --prefix agent
- Create agent records:
  python context_compass/system/ai_restricted/agent_management/agent_manage.py create --repo-root . --agent-id <agent_id> --agent-role <role>
- Archive agent records:
  python context_compass/system/ai_restricted/agent_management/agent_manage.py archive --repo-root . --agent-id <agent_id> --agent-role <role>
- Delete agent records:
  python context_compass/system/ai_restricted/agent_management/agent_manage.py delete --repo-root . --agent-id <agent_id> --agent-role <role>
- When acting on another agent, pass --owner-id to record the actor.
- Check in (mark active):
  python context_compass/system/ai_restricted/agent_management/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-role <role> --agent-kind <kind> --model-name <model> --runtime <runtime>
- Check out (mark inactive):
  python context_compass/system/ai_restricted/agent_management/agent_checkout.py --repo-root . --agent-id <agent_id> --agent-role <role>
- Add a work item to a per-agent queue (work_id auto-generated if omitted):
  python context_compass/system/ai_restricted/work_management/work_queue_add.py --repo-root . --agent-id <agent_id> --kind <kind> --target-path <path> --ctx-path <path> --root-work-id <root> --parent-work-id <parent>
- Move an agent work item into branch queues:
  python context_compass/system/ai_restricted/work_management/work_item_agent_to_branch.py --repo-root . --agent-id <agent_id> --work-id <work_id> --dest-bucket <bucket>
- Move an agent work item into global queues:
  python context_compass/system/ai_restricted/work_management/work_item_agent_to_global.py --repo-root . --agent-id <agent_id> --work-id <work_id> --dest-bucket <bucket>

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
