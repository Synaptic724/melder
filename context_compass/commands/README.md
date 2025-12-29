# commands

Purpose
- Store machine-generated command registries for context_compass tools.
- Separate user-facing commands from the full system registry.

Files
- `commands_user.json`: user-facing commands.
- `commands_system.json`: full system command list.
- Both follow `context_compass/schemas/command_registry.schema.json`.

Rules
- Registries are machine-owned and stored as minified JSON.
- Do not edit registries by hand.
- Regenerate via:
  - `python context_compass/tools/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

Notes
- The user registry is a curated subset of the system registry.
- Commands may still be blocked by feature flags or repo_state.
