# system_orientation

Purpose
- Provide a consistent way to explain context_compass to users.
- Translate agent stories and user documentation into clear, actionable guidance.
- Keep explanations aligned with the authority chain and current configuration.

When to use
- The user asks how the system works, what steps it follows, or how to interact with it.
- The user asks about agent stories or user stories.
- The user wants a concise walkthrough before work begins.

Required behavior
- Start with the authority chain from `context_compass/onboarding/AGENTS.md`.
- Read the required user docs before explaining how the system works:
  - context_compass/onboarding/user/README.md
  - context_compass/onboarding/user/getting_started.md
  - context_compass/onboarding/user/environment_prereqs.md
  - context_compass/onboarding/user/configuration.md
  - context_compass/onboarding/user/commands.md
  - context_compass/onboarding/user/security_and_secrets.md
- Explain onboarding at a high level, then point to the exact agent story and user doc.
- Report active feature flags and work_mode before describing tools.
- If a feature is disabled, say so and skip its workflow.
- Do not restate or override policy; cite the relevant skill or doc.
- If the user asks about a specific topic (scan, repo_state, work queues, memory),
  read the matching user doc before responding.

Core references
- Agent stories: `context_compass/onboarding/agent/general/behavioral_guidelines/README.md`
- User docs: `context_compass/onboarding/user/README.md`
- Configuration: `context_compass/onboarding/user/configuration.md`
- Onboarding bundle: ToolCommandAPI command `onboarding_bundle` (read-only)
- Command registry: SQLite tables `command_registry_user` and `command_registry_system`
- Command execution: `context_compass/workspace/tools/general/tool_execute.py` (ToolCommandAPI + hooks)
- Tool discovery: `context_compass/workspace/tools/general/tool_registry_describe.py`

Suggested user-facing explanation flow
1) "Here is the authority chain and where behavior lives."
2) "Here is the onboarding sequence in short form."
3) "Here are the agent stories you can read for detail."
4) "Here are the user docs that mirror those stories."
5) "Here is the active configuration (features + work_mode)."
6) "Here is the command registry and how to list available tools."
7) "Here is how to execute commands with hooks (ToolCommandAPI via tool_execute)."

Example response outline (short)
- Authority chain and doc locations.
- Onboarding steps (certification, branch init/switch, checkin, scan/tasks).
- Pointers to agent stories and user docs.
- Command registry location for tools.

Notes
- Use clear, direct language; avoid restating full policy documents.
- Keep the explanation faithful to `context_compass/onboarding/AGENTS.md`.
