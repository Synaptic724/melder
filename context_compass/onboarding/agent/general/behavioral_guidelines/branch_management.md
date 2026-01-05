# branch_management

Purpose
- Describe how agents create, clone, copy, and clean branch-scoped state.

Story
1) Initialize a branch runtime with `branch_init.py`.
2) Switch the active branch with `branch_switch.py`.
3) When you need a new branch that inherits context + queues, use `branch_clone.py`.
4) When you only need context or queues, use `branch_copy_context.py` or `branch_copy_work.py`.
5) If a branch needs a clean slate, run `branch_delete_work.py` or `branch_delete_context.py`.
6) When a branch is no longer needed, hard-delete it with `branch_delete.py`.

Rules
- Never delete the active branch; switch first.
- Use lease locks in system.db for branch copy/delete operations.
- Reset leases and in_progress states unless you must preserve them.

References
- `context_compass/onboarding/user/branching_and_state.md`
- `context_compass/onboarding/agent/general/skills/branch_management.md`
