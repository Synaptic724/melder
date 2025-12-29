# branching

Purpose
- Describe how context_compass state and queues behave across git branches.

Branch model
- Global queues live in context_compass/work_management/ and are shared history.
- Branch queues live in context_compass/branch_management/<branch>/work_management/.
- Branch state (scans, errors, locks, repo_state, context_profiles) lives in context_compass/branch_management/<branch>/state/.
- self_context remains global in context_compass/self_context/.

Workflow
1) Run `context_compass/tools/branch_init.py --branch-name <name> --agent-id <id> --work-id <work_id>`.
2) Run `context_compass/tools/branch_switch.py --branch-name <name> --agent-id <id> --work-id <work_id>`.
3) Run scans and work tooling; they operate on branch state and queues.
4) Promote work items to global queues when you want shared history
   (use context_compass/tools/work_item_branch_to_global.py).
5) Pull global items into the branch when execution should begin
   (use context_compass/tools/work_item_global_to_branch.py).

Notes
- Branch directories mirror the work_management structure.
- Branch state is isolated to reduce merge conflicts and branch churn.
