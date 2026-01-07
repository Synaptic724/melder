# command_api_rebuild

Goal
- Rebuild execution flow around a CommandAPI that constructs a runner per invocation,
  loads hooks, builds a DAG, and runs pre/post hooks around the target command.

Decisions
- No backward compatibility; direct script entrypoints are removed or become thin wrappers only.
- tool_command_api is the top-level executor and owns hook orchestration.
- Non-SQL tools remain leaf scripts; they must never call ToolCommandAPI to avoid recursion.
- Direct tool CLI execution is allowed as a last resort but bypasses hooks.
- SQL CRUD/query/sql_tools are out of scope for CommandAPI (separate DB API).
- Reuse the existing hook registry for now; keep DAG build inside tool_command_api.
- Payload schemas live in the manifest (no separate schema files yet).

Design sketch (tool_command_api)
- Inputs: command_name, payload, repo_root, agent_id, work_id (plus any required top-level flags).
- CommandAPI builds the ExecutionContext internally; callers never construct it.
- Resolve command metadata via registry/manifest (script_path, cli_args, requirements).
- Enforce requirements (certification + feature flags) before execution; work_id is advisory.
- Load hooks for the command (pre/post), build ordered execution plan (DAG if needed).
- Execute pre-hooks -> command -> post-hooks with shared ExecutionContext.
- Capture errors and return CommandResult with structured status and timing.
- Add recursion/loop guard for hook chains and nested command calls.

Initial tasks
- Define CommandAPI.execute contract and payload schema format.
- Implement requirement enforcement (certification + feature flags; work_id advisory).
- Implement tool_execute dispatcher that executes by command name.
- Update registry/manifest to reference payload schemas.
- Convert existing scripts to thin wrappers that call CommandAPI.
- Add tests for hook ordering and command execution.

TODO inventory (non-SQL tool refactor targets)
Note: sql_queries/sql_tools are a separate SQL API; update them to remove hook execution only.

system_management
- `context_compass/system/ai_restricted/system_management/branch_clone.py`
- `context_compass/system/ai_restricted/system_management/branch_copy_context.py`
- `context_compass/system/ai_restricted/system_management/branch_copy_work.py`
- `context_compass/system/ai_restricted/system_management/branch_delete.py`
- `context_compass/system/ai_restricted/system_management/branch_delete_context.py`
- `context_compass/system/ai_restricted/system_management/branch_delete_work.py`
- `context_compass/system/ai_restricted/system_management/branch_init.py`
- `context_compass/system/ai_restricted/system_management/branch_switch.py`
- `context_compass/system/ai_restricted/system_management/command_registry_describe.py`
- `context_compass/system/ai_restricted/system_management/command_registry_generate.py`
- `context_compass/system/ai_restricted/system_management/command_registry_path.py`
- `context_compass/system/ai_restricted/system_management/command_registry_validator.py`
- `context_compass/system/ai_restricted/system_management/environment_check.py`
- `context_compass/system/ai_restricted/system_management/lease.py`
- `context_compass/system/ai_restricted/system_management/lock_acquire.py`
- `context_compass/system/ai_restricted/system_management/lock_release.py`
- `context_compass/system/ai_restricted/system_management/lock_status.py`
- `context_compass/system/ai_restricted/system_management/repo_state_assess.py`
- `context_compass/system/ai_restricted/system_management/scan.py`
- `context_compass/system/ai_restricted/system_management/update_state.py`
- `context_compass/system/ai_restricted/system_management/validate.py`

agent_management
- `context_compass/system/ai_restricted/agent_management/agent_checkin.py`
- `context_compass/system/ai_restricted/agent_management/agent_checkout.py`
- `context_compass/system/ai_restricted/agent_management/agent_id.py`
- `context_compass/system/ai_restricted/agent_management/agent_manage.py`
- `context_compass/system/ai_restricted/agent_management/agent_onboarding_start.py`
- `context_compass/system/ai_restricted/agent_management/agent_status.py`
- `context_compass/system/ai_restricted/agent_management/onboarding_bundle.py`
- `context_compass/system/ai_restricted/agent_management/onboarding_bundle_restore.py`
- `context_compass/system/ai_restricted/agent_management/python_certified.py`
- `context_compass/system/ai_restricted/agent_management/self_context.py`
- `context_compass/system/ai_restricted/agent_management/skill_receipt.py`

work_management
- `context_compass/system/ai_restricted/work_management/ticket_promote.py`
- `context_compass/system/ai_restricted/work_management/work_item_add.py`
- `context_compass/system/ai_restricted/work_management/work_item_agent_to_branch.py`
- `context_compass/system/ai_restricted/work_management/work_item_agent_to_global.py`
- `context_compass/system/ai_restricted/work_management/work_item_branch_to_global.py`
- `context_compass/system/ai_restricted/work_management/work_item_bulk_move.py`
- `context_compass/system/ai_restricted/work_management/work_item_claim.py`
- `context_compass/system/ai_restricted/work_management/work_item_close.py`
- `context_compass/system/ai_restricted/work_management/work_item_complete.py`
- `context_compass/system/ai_restricted/work_management/work_item_global_to_branch.py`
- `context_compass/system/ai_restricted/work_management/work_item_move.py`
- `context_compass/system/ai_restricted/work_management/work_queue_add.py`
- `context_compass/system/ai_restricted/work_management/work_queue_list.py`

context_management
- `context_compass/system/ai_restricted/context_management/context_architecture_check.py`
- `context_compass/system/ai_restricted/context_management/context_architecture_resurvey.py`
- `context_compass/system/ai_restricted/context_management/context_architecture_survey.py`
- `context_compass/system/ai_restricted/context_management/context_component_check.py`
- `context_compass/system/ai_restricted/context_management/context_component_resurvey.py`
- `context_compass/system/ai_restricted/context_management/context_component_survey.py`
- `context_compass/system/ai_restricted/context_management/context_profiles_read.py`
- `context_compass/system/ai_restricted/context_management/context_profiles_resurvey.py`
- `context_compass/system/ai_restricted/context_management/context_profiles_review.py`
- `context_compass/system/ai_restricted/context_management/context_profiles_survey.py`
- `context_compass/system/ai_restricted/context_management/research_delete.py`
- `context_compass/system/ai_restricted/context_management/research_move.py`

memory
- `context_compass/system/ai_restricted/memory/memory_add.py`
- `context_compass/system/ai_restricted/memory/memory_read.py`
- `context_compass/system/ai_restricted/memory/memory_remove.py`
- `context_compass/system/ai_restricted/memory/memory_update.py`

database_management
- `context_compass/system/ai_restricted/database_management/sqlite_crud.py`
- `context_compass/system/ai_restricted/database_management/sqlite_crud_command.py`
- `context_compass/system/ai_restricted/database_management/sqlite_query.py`
- `context_compass/system/ai_restricted/database_management/sqlite_query_command.py`

sql_queries
- `context_compass/system/ai_restricted/sql_queries/system/describe_table.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_agent_records.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_architecture_context.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_branch_work_queues.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_component_contexts.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_context_profiles.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_dir_ctx_by_branch.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_file_ctx_by_branch.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_repo_state.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_scan_error_records_by_branch.py`
- `context_compass/system/ai_restricted/sql_queries/user/delete_scan_records_by_branch.py`
- `context_compass/system/ai_restricted/sql_queries/user/describe_table.py`
- `context_compass/system/ai_restricted/sql_queries/user/list_active_ctx_paths.py`
- `context_compass/system/ai_restricted/sql_queries/user/list_dir_ctx_payloads.py`
- `context_compass/system/ai_restricted/sql_queries/user/list_file_ctx_payloads.py`
- `context_compass/system/ai_restricted/sql_queries/user/move_agent_work_item_to_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/move_work_queue_item.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_agent_profile.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_agent_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_architecture_context.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_branch_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_component_contexts.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_context_profiles.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_dir_ctx_by_ctx_path.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_dir_ctx_by_dir_path.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_file_ctx_by_ctx_path.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_file_ctx_by_file_path.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_global_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/read_self_context.py`
- `context_compass/system/ai_restricted/sql_queries/user/upsert_work_queue_tasks.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_agent_profile.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_agent_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_architecture_context.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_branch_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_component_contexts.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_context_profiles.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_dir_ctx.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_file_ctx.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_global_work_queue.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_onboarding_bundle.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_repo_state.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_scan_record.py`
- `context_compass/system/ai_restricted/sql_queries/user/write_self_context.py`

sql_tools
- `context_compass/system/ai_restricted/sql_tools/agent_profile/read/list_agent_ids.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_item_lease/delete/by_work_id.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_item_reasons/create/insert_reasons.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_item_reasons/delete/by_work_id.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_items/create/insert_item.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_items/delete/by_work_id.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_items/read/by_work_id.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_queue/create/ensure_queue.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_queue/read/list_agent_ids.py`
- `context_compass/system/ai_restricted/sql_tools/agent_work_queue/update/touch_queue.py`
- `context_compass/system/ai_restricted/sql_tools/branch_registry/create/register_branch.py`
- `context_compass/system/ai_restricted/sql_tools/branch_registry/delete/by_branch_name.py`
- `context_compass/system/ai_restricted/sql_tools/branch_registry/read/by_branch_name.py`
- `context_compass/system/ai_restricted/sql_tools/branch_registry/update/by_branch_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_system/create/register_command.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_system/delete/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_system/read/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_system/read/list_commands.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_system/update/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_user/create/register_command.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_user/delete/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_user/read/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_user/read/list_commands.py`
- `context_compass/system/ai_restricted/sql_tools/command_registry_user/update/by_command_name.py`
- `context_compass/system/ai_restricted/sql_tools/config_context_compass_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_context_compass_flags/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_context_compass_skill_rules/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_ctx_artifact_output_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_ignore_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_ignore_rules/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_languages_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_languages_directory_hints/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_languages_extensions/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_policies_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_source_roots_core/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/config_source_roots_entries/read/by_config_id.py`
- `context_compass/system/ai_restricted/sql_tools/current_branch/read/by_record_id.py`
- `context_compass/system/ai_restricted/sql_tools/current_branch/update/set_current_branch.py`
- `context_compass/system/ai_restricted/sql_tools/environment_state/update/set_environment_state.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_system/create/register_hook.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_system/delete/unregister_hook.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_system/read/list_hooks.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_system/update/modify_hook.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_user/create/register_hook.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_user/delete/unregister_hook.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_user/read/list_hooks.py`
- `context_compass/system/ai_restricted/sql_tools/hook_registry_user/update/modify_hook.py`
- `context_compass/system/ai_restricted/sql_tools/lease_locks/create/acquire_lock.py`
- `context_compass/system/ai_restricted/sql_tools/lease_locks/delete/release_lock.py`
- `context_compass/system/ai_restricted/sql_tools/onboarding_bundle/read/by_bundle_id.py`
- `context_compass/system/ai_restricted/sql_tools/onboarding_bundle_errors/read/by_bundle_id_and_paths.py`
- `context_compass/system/ai_restricted/sql_tools/onboarding_bundle_files/read/by_bundle_id_and_paths.py`
- `context_compass/system/ai_restricted/sql_tools/onboarding_bundle_missing/read/by_bundle_id_and_paths.py`
- `context_compass/system/ai_restricted/sql_tools/repo_state/read/by_branch_name.py`
- `context_compass/system/ai_restricted/sql_tools/scan_error_records/create/write_error_record.py`
- `context_compass/system/ai_restricted/sql_tools/self_context/read/list_agent_ids.py`
- `context_compass/system/ai_restricted/sql_tools/work_queue_item_reasons/create/insert_reasons.py`
- `context_compass/system/ai_restricted/sql_tools/work_queue_items/create/insert_item.py`
- `context_compass/system/ai_restricted/sql_tools/work_queue_items/read/list_by_queue_id.py`
- `context_compass/system/ai_restricted/sql_tools/work_queue_items/update/update_item_state.py`
- `context_compass/system/ai_restricted/sql_tools/work_queues/create/ensure_queue.py`
- `context_compass/system/ai_restricted/sql_tools/work_queues/update/touch_queue.py`

_shared
- `context_compass/system/ai_restricted/_shared/command_results.py`
