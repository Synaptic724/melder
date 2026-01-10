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
- Initialize branch state: ToolCommandAPI command `branch_init`.
- Switch active branch: ToolCommandAPI command `branch_switch`.
- Clone a branch (context + work): ToolCommandAPI command `branch_clone`.
- Copy context only: ToolCommandAPI command `branch_copy_context`.
- Copy work queues only: ToolCommandAPI command `branch_copy_work`.
- Clear branch work queues: ToolCommandAPI command `branch_delete_work`.
- Delete context records: ToolCommandAPI command `branch_delete_context`.
- Hard-delete a branch: ToolCommandAPI command `branch_delete`.

Notes
- Branch state lives in SQLite user.db tables (repo_state, contexts, scans, errors).
- Branch queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- Global queues live in SQLite user.db tables `work_queues` and `work_queue_items` (scope=global, branch_name null) and are not modified by branch deletion.
