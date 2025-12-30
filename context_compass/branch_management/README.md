# branch_management

Purpose
- Keep branch-scoped state and work queues isolated from global queues.
- Describe how context_compass behaves across git branches.
- Allow agents to initialize and switch branch runtime state safely.

Structure
- current_branch.json: active branch pointer (machine-owned, minified JSON).
- <branch_name>/state/: branch-specific scans, locks, errors, repo_state, context_profiles.
- <branch_name>/state/: also includes architecture_context.json and component_contexts.json (plus test variants).
- <branch_name>/work_management/: branch-specific ready/active/backlog/completed/denied queues.
- archive/: archived branch directories created by branch_cleanup.py.

Branch model
- Global queues live in context_compass/work_management/ and are shared history.
- Branch queues live in context_compass/branch_management/<branch>/work_management/.
- Branch state (scans, errors, locks, repo_state, context_profiles) lives in context_compass/branch_management/<branch>/state/.
- self_context remains global in context_compass/self_context/.

Workflow
1) Create a branch runtime with `context_compass/tools/branch_init.py --branch-name <name> --agent-id <id> --work-id <work_id>`.
2) Switch the active branch with `context_compass/tools/branch_switch.py --branch-name <name> --agent-id <id> --work-id <work_id>`.
3) Run scans and work tools; they read/write under the active branch directory.
4) Promote work items to global queues when you want shared history
   (use context_compass/tools/work_item_branch_to_global.py).
5) Pull global items into the branch when execution should begin
   (use context_compass/tools/work_item_global_to_branch.py).
6) Clone branch state and queues when spinning a new branch
   (use context_compass/tools/branch_clone.py).
7) Copy context or work queues between branches without cloning
   (use context_compass/tools/branch_copy_context.py and branch_copy_work.py).
8) Clear branch queues or context without deleting the branch directory
   (use context_compass/tools/branch_delete_work.py and branch_delete_context.py).
9) Archive or delete branch directories when they are no longer needed
   (use context_compass/tools/branch_cleanup.py).

Notes
- Branch directories mirror the work_management structure.
- Branch state is isolated to reduce merge conflicts and branch churn.
- `self_context` remains global and is not branch-scoped.
- Global queues in context_compass/work_management remain the canonical shared list.
