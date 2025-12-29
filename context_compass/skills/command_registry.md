# command_registry

Purpose
- Define how to present and maintain the command registry.
- Provide a canonical list of tools a user or agent can run.
- Ensure registry JSON stays machine-generated and deterministic.

Registry location
- Docs: `context_compass/commands/README.md`
- User registry: `context_compass/commands/commands_user.json`
- System registry: `context_compass/commands/commands_system.json`
- Schema: `context_compass/schemas/command_registry.schema.json`

Rules
- Registries are machine-owned and must be minified JSON.
- Do not edit registry JSON by hand; use the generator tool.
- The user registry is a subset of the system registry.
- Report command availability based on feature flags and work_mode.

Generator tool
- `python context_compass/tools/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- The tool rewrites both registries atomically.

How to respond to users
- If asked "what commands can I run?", read the user registry and summarize by category.
- If asked about agent-only tooling, read the system registry.
- If a command is blocked by feature flags or repo_state, state that explicitly.

References
- `context_compass/skills/feature_flags.md`
- `context_compass/user_documentation/commands.md`
