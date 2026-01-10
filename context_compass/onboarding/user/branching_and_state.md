# Branching and State

Purpose
- Explain how branch-scoped state works and what remains global.

Branch-scoped
- SQLite user.db table `repo_state` (branch_name key) and table `context_profiles`.
- SQLite user.db tables `architecture_context` and `component_contexts` (branch_name + kind).
- SQLite user.db tables `scan_registry` and `scan_error_records` (branch_name + scan_id/error_id).
- SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set).
- `current_branch` table (record_id: current) points to the active branch.

State examples
- `repo_state`: lifecycle assessment and tooling gating (keyed by branch_name).
- `context_profiles`: context profile bundles and freshness (per-branch row keyed by branch_name).
- `context_profile_items`: per-profile entries for context_profiles.
- `context_profile_item_paths`: profile path lists.
- `context_profile_item_staleness_reasons`: profile staleness reason lists.

Global (not branch-scoped)
- SQLite user.db tables: `agent_profile`, `self_context`, `agent_work_queue` (with child tables for lists/maps).
- Self-context locks are recorded in SQLite system.db lease_locks.
- SQLite system.db config tables (feature flags, policies, roots).
- `context_compass/system/memory/` (user/system memory stores).
- `context_compass/commands/` (command registries).

Branch initialization
- Use ToolCommandAPI command `branch_init` (see `context_compass/onboarding/user/commands.md` for payloads).

Branch switching
- Use ToolCommandAPI command `branch_switch`.

Branch cloning and copying
- Clone a branch with state + queues:
  Use ToolCommandAPI command `branch_clone`.
- Copy context files only:
  Use ToolCommandAPI command `branch_copy_context`.
- Copy work queues only:
  Use ToolCommandAPI command `branch_copy_work`.

Branch deletion
- Clear branch work queues:
  Use ToolCommandAPI command `branch_delete_work`.
- Delete context state records:
  Use ToolCommandAPI command `branch_delete_context`.
- Hard-delete a branch (deletes branch rows from shared tables):
  Use ToolCommandAPI command `branch_delete`.

Why branch state exists
- Keeps task queues and scan results isolated per branch.
- Avoids accidental cross-branch task contamination.

Do not modify branch state manually
- Use commands that acquire locks and write SQLite records atomically.
