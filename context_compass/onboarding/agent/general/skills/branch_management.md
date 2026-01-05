# branch_management

Purpose
- Define how branch-scoped state and queues are created, cloned, copied, and cleaned up.
- Keep branch operations deterministic and isolated from global queues.

Rules
- Use branch tools; never copy branch state manually.
- Do not delete the active branch; switch branches first.
- Copy context and work separately unless you explicitly need both.
- When copying work queues, reset leases and in_progress states unless you must preserve them.
- When copying repo_state, reset scan counters unless you intentionally want to inherit scan history.
- Always acquire lease locks in system.db before branch writes.

Commands
- Initialize branch state:
  `python context_compass/system/ai_restricted/system_management/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Switch active branch:
  `python context_compass/system/ai_restricted/system_management/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Clone a branch (context + work):
  `python context_compass/system/ai_restricted/system_management/branch_clone.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Copy context only:
  `python context_compass/system/ai_restricted/system_management/branch_copy_context.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Copy work queues only:
  `python context_compass/system/ai_restricted/system_management/branch_copy_work.py --repo-root . --source-branch <branch> --dest-branch <branch> --agent-id <agent_id> --work-id <work_id>`
- Clear branch work queues:
  `python context_compass/system/ai_restricted/system_management/branch_delete_work.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Delete context records:
  `python context_compass/system/ai_restricted/system_management/branch_delete_context.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
- Hard-delete a branch:
  `python context_compass/system/ai_restricted/system_management/branch_delete.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

Notes
- Branch state lives in SQLite user.db tables (repo_state, contexts, scans, errors).
- Branch queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- Global queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=global, branch_name null) and are not modified by branch deletion.
