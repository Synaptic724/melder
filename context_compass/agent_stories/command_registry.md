# command_registry

Purpose
- Describe how an agent generates and uses command registries.

Story steps
1) Check configuration
   - Ensure command_registry feature is enabled.

2) Generate registries
   - `python context_compass/tools/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
   - This updates both user and system registries.

3) Use registries to respond
   - User asks for commands: read `commands_user.json` and summarize by category.
   - Agent needs full list: read `commands_system.json`.

Notes
- Registries are machine-owned; never edit by hand.
- Commands remain subject to feature flags and repo_state gating.
