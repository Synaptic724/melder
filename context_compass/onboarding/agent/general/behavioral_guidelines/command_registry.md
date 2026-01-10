# command_registry

Purpose
- Describe how an agent generates and uses command registries.

Story steps
1) Check configuration
   - Ensure command_registry feature is enabled.

2) Generate registries
   - `python context_compass/workspace/tools/general/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id> [--manifest-path <path>]`
   - This updates both user and system registry tables.
   - Default manifest: `context_compass/system/ai_restricted/system_management/command_manifest.json`
   - Add `--export-json` to emit optional JSON exports.

3) Use registries to respond
   - User asks for commands: query `command_registry_user` and summarize by category.
   - Agent needs full list: query `command_registry_system`.

Notes
- Registries are machine-owned; never edit by hand.
- Commands remain subject to feature flags and repo_state gating.
- Commands run with hooks through ToolCommandAPI via `tool_execute.py`.
- Preferred CLI entrypoint: `python context_compass/workspace/tools/general/tool_execute.py --command-name <name> --payload-json '{}' --repo-root . --agent-id <agent_id> [--work-id <work_id>]`
- Direct tool execution is a last resort and bypasses hooks.
- Full registry details: `python context_compass/workspace/tools/general/tool_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope both`
- SQL registry discovery:
  `python context_compass/workspace/tools/sql/crud/sql_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
  `python context_compass/workspace/tools/sql/query/sql_query_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
