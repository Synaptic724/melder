# ai_restricted

This directory stores restricted command scripts and shared helpers for context_compass.

Rules
- Use minified JSON for any machine-owned artifact.
- Always lease locks before writing shared state or ctx targets.
- Publish JSON atomically using a tmp file and os.replace.
- Tools that mutate repo state must refuse to run unless the agent profile certification_state indicates CERTIFIED.
- Tools must honor the SQLite-backed config tables (`config_context_compass_*`) and refuse disabled features.
- Policy settings are loaded from SQLite config_policies_* tables (defaults are seeded when no overrides exist).
- If work_mode is hard, tools must require a work_id for execution.
- Only agent_checkin/agent_checkout/agent_manage update agent profiles.
- Invoke tools with --agent-id so certification checks can locate the profile.
- Exception: onboarding_bundle.py is allowed before certification and does not update agent state.
- Branch-aware tools read/write via SQLite; locks are stored in system.db (lease_locks).

Categories
- system_management: branch state, scanning, validation, registry generation, and environment preflight
- agent_management: agent identity, certification, checkin/checkout, and self context
- memory: memory store CRUD
- work_management: work queues, work items, and ticket intake
- context_management: context profiles, architecture/component contexts, and research lifecycle
- database_management: database tooling (reserved)
- hooks: manifest-driven hook registry (seeded into hook_registry_system/user)

Tools
System management
- ai_restricted/system_management/branch_delete.py: hard-delete a branch (drop SQLite tables and registry records).
- ai_restricted/system_management/branch_clone.py: clone branch state and work queues into a new branch.
- ai_restricted/system_management/branch_copy_context.py: copy context records between branches.
- ai_restricted/system_management/branch_copy_work.py: copy work queues between branches.
- ai_restricted/system_management/branch_delete_context.py: delete context records for a branch.
- ai_restricted/system_management/branch_delete_work.py: clear branch work queues.
- ai_restricted/system_management/branch_init.py: initialize branch-scoped state and work queues.
- ai_restricted/system_management/branch_switch.py: switch the active branch pointer.
- ai_restricted/system_management/command_registry_generate.py: generate machine-readable command registries.
- ai_restricted/system_management/environment_check.py: report OS/runtime/tool availability and persist environment_state in system.db.
- ai_restricted/system_management/lease.py: lock acquisition and lease refresh.
- ai_restricted/system_management/repo_state_assess.py: assess repo lifecycle stage and update repo_state records.
- ai_restricted/system_management/scan.py: repository scan, staleness detection, task emission.
- ai_restricted/system_management/update_state.py: safe state transitions for tasks and repo_state.
- ai_restricted/system_management/validate.py: schema and staleness validation for CI.

Agent management
- ai_restricted/agent_management/agent_checkin.py: check in an agent and mark the profile active.
- ai_restricted/agent_management/agent_checkout.py: check out an agent and mark the profile inactive.
- ai_restricted/agent_management/agent_id.py: generate a session-scoped agent id (ULID).
- ai_restricted/agent_management/agent_manage.py: create, archive, or delete agent worklists and self context.
- ai_restricted/agent_management/onboarding_bundle.py: generate a consolidated onboarding bundle of context_compass docs (allowed pre-certification).
- ai_restricted/agent_management/python_certified.py:
- ai_restricted/agent_management/self_context.py: manage agent self context records.
- ai_restricted/agent_management/skill_receipt.py: write deterministic skill read receipts.

Memory
- ai_restricted/memory/memory_add.py: add a memory entry to user/system memory stores.
- ai_restricted/memory/memory_read.py: read memory entries from user/system memory stores.
- ai_restricted/memory/memory_remove.py: remove a memory entry from user/system memory stores.
- ai_restricted/memory/memory_update.py: update a memory entry in user/system memory stores.

Work management
- ai_restricted/work_management/work_item_add.py: add a work item to work_management epics/stories/tasks queues.
- ai_restricted/work_management/work_item_move.py: move a work item between work_management buckets.
- ai_restricted/work_management/work_item_bulk_move.py: move multiple work items between work_management buckets.
- ai_restricted/work_management/work_item_close.py: close a work item and remove it from per-agent queues.
- ai_restricted/work_management/work_item_global_to_branch.py: move a work item from global queues into the active branch queues.
- ai_restricted/work_management/work_item_branch_to_global.py: move a work item from branch queues into the global queues.
- ai_restricted/work_management/work_item_agent_to_branch.py: move a work item from an agent queue into branch queues.
- ai_restricted/work_management/work_item_agent_to_global.py: move a work item from an agent queue into global queues.
- ai_restricted/work_management/work_queue_add.py: add a work item to a per-agent work queue.
- ai_restricted/work_management/ticket_promote.py: promote a GitHub ticket markdown into work_management queues.

Context management
- ai_restricted/context_management/context_architecture_survey.py: build architecture_context records from directory ctx.
- ai_restricted/context_management/context_component_survey.py: build component_contexts records from directory ctx.
- ai_restricted/context_management/context_architecture_check.py: report architecture_context freshness from the matrix.
- ai_restricted/context_management/context_component_check.py: report component_contexts freshness from the matrix.
- ai_restricted/context_management/context_architecture_resurvey.py: process resurvey_architecture_context tasks.
- ai_restricted/context_management/context_component_resurvey.py: process resurvey_component_contexts tasks.
- ai_restricted/context_management/context_profiles_survey.py: build context profile bundles from ctx and work queues.
- ai_restricted/context_management/context_profiles_read.py: emit consolidated context for a named profile and update usage.
- ai_restricted/context_management/context_profiles_review.py: record profile grades/notes and emit optimize/prune tasks.
- ai_restricted/context_management/context_profiles_resurvey.py: process resurvey_context_profile tasks and rebuild profiles.
- ai_restricted/context_management/research_move.py: move research artifacts between lifecycle buckets.
- ai_restricted/context_management/research_delete.py: delete research artifacts from a lifecycle bucket.

Shared helpers
- ai_restricted/_shared contains canonical JSON IO, hashing, schema validation, ignore rules, paths, and agent presence helpers.

Preflight scripts
- ai_restricted/system_management/environment_check.ps1 and ai_restricted/system_management/environment_check.sh provide OS + python availability checks when python is missing.
