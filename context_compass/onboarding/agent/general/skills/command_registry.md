# command_registry

Purpose
- Define how to present and maintain the command registry.
- Provide a canonical list of tools a user or agent can run.
- Ensure registry outputs stay machine-generated and deterministic.

Registry location
- User registry table: `command_registry_user` in `context_compass/system/storage/sqlite/user.db`
- System registry table: `command_registry_system` in `context_compass/system/storage/sqlite/system.db`
- Schema: `context_compass/system/schemas/command_registry.tables.json`

Execution model
- ToolCommandAPI resolves registry entries and runs hooks for non-SQL tools.
- Use `tool_execute.py` (CLI) or `execute_command(...)` (python) to run commands with hooks.
- Direct tool execution bypasses hooks and is a last resort.
- SQL CRUD/query scripts are DB-only and are not executed through ToolCommandAPI.

Rules
- Registries are machine-owned and stored in SQLite.
- Do not edit registry rows by hand; use the generator tool.
- The user registry is a subset of the system registry.
- Report command availability based on feature flags and work_mode.

Generator tool
- `python context_compass/system/ai_restricted/system_management/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id> [--manifest-path <path>]`
- The tool writes both registry tables in SQLite.
- Default manifest: `context_compass/system/ai_restricted/system_management/command_manifest.json`

Describe tool (path-safe)
- `python context_compass/system/ai_restricted/system_management/command_registry_describe.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope <system|user> --command-name <command_name> --work-id <work_id>`
- Returns minified JSON plus structured command descriptors.
- Script paths are redacted by default.

Path lookup tool (single command)
- `python context_compass/system/ai_restricted/system_management/command_registry_path.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope <system|user> --command-name <command_name> --work-id <work_id>`
- Returns minified JSON with script_path and entrypoint for one command.
- Use only when a path is explicitly required.

How to respond to users
- If asked "what commands can I run?", query the user registry table and summarize by category.
- If asked about agent-only tooling, query the system registry table.
- If a command is blocked by feature flags or repo_state, state that explicitly.
- Use command_registry_describe for detailed, path-safe command metadata.
- Only use command_registry_path when a single path is required.

References
- `context_compass/onboarding/agent/general/skills/feature_flags.md`
- `context_compass/onboarding/user/commands.md`
