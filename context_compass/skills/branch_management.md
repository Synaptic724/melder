# branch_management

Purpose
- Define how branch-scoped state and queues are created, cloned, copied, and cleaned up.
- Keep branch operations deterministic and isolated from global queues.

Rules
- Use branch tools; never copy branch state manually.
- Do not clean up the active branch; switch branches first.
- Copy context and work separately unless you explicitly need both.
- When copying work queues, reset leases and in_progress states unless you must preserve them.
- When copying repo_state, reset scan counters unless you intentionally want to inherit scan history.
- Always acquire locks and write JSON atomically.

Commands
- Initialize branch state:
  `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Switch active branch:
  `python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Clone a branch (context + work):
  `python context_compass/tools/branch_clone.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Copy context only:
  `python context_compass/tools/branch_copy_context.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Copy work queues only:
  `python context_compass/tools/branch_copy_work.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Clear branch work queues:
  `python context_compass/tools/branch_delete_work.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Delete context state files:
  `python context_compass/tools/branch_delete_context.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Archive or delete a branch directory:
  `python context_compass/tools/branch_cleanup.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

Notes
- Branch state lives under `context_compass/branch_management/<branch>/state/`.
- Branch queues live under `context_compass/branch_management/<branch>/work_management/`.
- Global queues remain under `context_compass/work_management/` and are not modified by branch cleanup.
