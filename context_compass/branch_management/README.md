# branch_management

Purpose
- Keep branch-scoped state and work queues isolated from global queues.
- Allow agents to initialize and switch branch runtime state safely.

Structure
- current_branch.json: active branch pointer (machine-owned, minified JSON).
- <branch_name>/state/: branch-specific scans, locks, errors, repo_state, context_profiles.
- <branch_name>/work_management/: branch-specific active/backlog/completed/denied queues.

Workflow
1) Create a branch runtime with `context_compass/tools/branch_init.py --branch-name <name>`.
2) Switch the active branch with `context_compass/tools/branch_switch.py --branch-name <name>`.
3) Run scans and work tools; they read/write under the active branch directory.

Notes
- `self_context` remains global and is not branch-scoped.
- Global queues in `context_compass/work_management/` remain the canonical shared list.
- Branch queues are for in-branch execution and can be promoted to global manually.
