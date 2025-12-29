# tools

This directory documents the context_compass tool contracts and implementations.

Rules
- Use minified JSON for any machine-owned artifact.
- Always lease locks before writing shared state or ctx targets.
- Publish JSON atomically using a tmp file and os.replace.
- Tools that mutate repo state must refuse to run unless certification_state.json indicates CERTIFIED.
- Tools must honor context_compass/config/context_compass_configuration.json and refuse disabled features.
- If work_mode is hard, tools must require a work_id for execution.
- All tool invocations must update agent heartbeat state (active_agents + agent profile).
- Invoke tools with --agent-id so heartbeat state can be recorded.
- Cleanup scripts are executed before heartbeat updates to evict stale agents.
- Exception: onboarding_bundle.py is allowed before certification and does not update heartbeat or state.
- Branch-aware tools read/write under context_compass/branch_management/<branch>/ after branch_init/branch_switch.

Tools
- scan.py: repository scan, staleness detection, task emission.
- lease.py: lock acquisition and lease refresh.
- validate.py: schema and staleness validation for CI.
- update_state.py: safe state transitions for tasks and repo_state.
- self_context.py: manage active_agents and agent self context records.
- skill_receipt.py: write deterministic skill read receipts.
- agent_manage.py: create, archive, or delete agent worklists and self context.
- agent_checkin.py: check in an agent and start heartbeat tracking.
- agent_checkout.py: check out an agent and mark it inactive.
- agent_id.py: generate a session-scoped agent id (ULID).
- agent_cleanup.py: run cleanup scripts under tools/cleanup_agents.
- branch_init.py: initialize branch-scoped state and work queues.
- branch_switch.py: switch the active branch pointer.
- branch_clone.py: clone branch state and work queues into a new branch.
- branch_copy_context.py: copy context state between branches.
- branch_copy_work.py: copy work queues between branches.
- branch_delete_context.py: delete context state files in a branch.
- branch_delete_work.py: clear branch work queues.
- branch_cleanup.py: archive or delete a branch directory.
- context_profiles_survey.py: build context profile bundles from ctx and work queues.
- context_profiles_read.py: emit consolidated context for a named profile and update usage.
- context_profiles_review.py: record profile grades/notes and emit optimize/prune tasks.
- context_profiles_resurvey.py: process resurvey_context_profile tasks and rebuild profiles.
- context_architecture_survey.py: build architecture_context.json from directory ctx.
- context_component_survey.py: build component_contexts.json from directory ctx.
- context_architecture_check.py: report architecture_context freshness from the matrix.
- context_component_check.py: report component_contexts freshness from the matrix.
- context_architecture_resurvey.py: process resurvey_architecture_context tasks.
- context_component_resurvey.py: process resurvey_component_contexts tasks.
- environment_check.py: report OS/runtime/tool availability and optionally write environment state.
- repo_state_assess.py: assess repo lifecycle stage and update repo_state.json.
- onboarding_bundle.py: generate a consolidated onboarding bundle of context_compass docs (allowed pre-certification).
- command_registry_generate.py: generate machine-readable command registries.
- memory_add.py: add a memory entry to user/system memory stores.
- memory_update.py: update a memory entry in user/system memory stores.
- memory_remove.py: remove a memory entry from user/system memory stores.
- memory_read.py: read memory entries from user/system memory stores.
- work_queue_add.py: add a work item to a per-agent work queue.
- work_item_add.py: add a work item to work_management epics/stories/tasks queues.
- work_item_move.py: move a work item between work_management buckets.
- work_item_close.py: close a work item and remove it from per-agent queues.
- work_item_global_to_branch.py: move a work item from global queues into the active branch queues.
- work_item_branch_to_global.py: move a work item from branch queues into the global queues.
- work_item_agent_to_branch.py: move a work item from an agent queue into branch queues.
- work_item_agent_to_global.py: move a work item from an agent queue into global queues.
- ticket_promote.py: promote a GitHub ticket markdown into work_management queues.

Shared helpers
- tools/_shared contains canonical JSON IO, hashing, schema validation, ignore rules, paths, and agent presence helpers.

Cleanup scripts
- tools/cleanup_agents contains cleanup modules that accept an agent_id and implement cleanup(repo_root, agent_id, now=...).
- Each cleanup module should also expose a CLI with --repo-root and --agent-id for direct invocation.

Preflight scripts
- environment_check.ps1 and environment_check.sh provide OS + python availability checks when python is missing.
