# general

Purpose
- Provide workspace-owned facades for ToolCommandAPI entrypoints.
- Keep CLI signatures aligned with the system tools in ai_restricted.

Scripts
- command_registry_generate.py -> context_compass/system/ai_restricted/system_management/command_registry_generate.py
- command_registry_describe.py -> context_compass/system/ai_restricted/system_management/command_registry_describe.py
- command_registry_path.py -> context_compass/system/ai_restricted/system_management/command_registry_path.py
- tool_execute.py -> context_compass/system/ai_restricted/system_management/tool_execute.py
- tool_registry_describe.py -> context_compass/system/ai_restricted/system_management/tool_registry_describe.py

Usage
- Generate registries:
  `python context_compass/workspace/tools/general/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id> [--manifest-path <path>]`
- Describe registry entries (path-safe):
  `python context_compass/workspace/tools/general/command_registry_describe.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope <system|user> --command-name <command_name> --work-id <work_id>`
- Resolve a single command path:
  `python context_compass/workspace/tools/general/command_registry_path.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope <system|user> --command-name <command_name> --work-id <work_id>`
- Execute a registered command:
  `python context_compass/workspace/tools/general/tool_execute.py --command-name <name> --payload-json '{}' --repo-root . --agent-id <agent_id> --work-id <work_id>`
- Inspect the ToolCommandAPI registry:
  `python context_compass/workspace/tools/general/tool_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope both`

Notes
- These scripts are facades only; do not add business logic here.
- Certification and work_mode enforcement happens in the system tools.
