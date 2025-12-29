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
- Start with the authority chain from `context_compass/AGENTS.md`.
- Explain onboarding at a high level, then point to the exact agent story and user doc.
- Report active feature flags and work_mode before describing tools.
- If a feature is disabled, say so and skip its workflow.
- Do not restate or override policy; cite the relevant skill or doc.

Core references
- Agent stories: `context_compass/agent_stories/README.md`
- User docs: `context_compass/user_documentation/README.md`
- Configuration: `context_compass/user_documentation/configuration.md`
- Onboarding bundle: `context_compass/tools/onboarding_bundle.py`
- Command registry: `context_compass/commands/README.md`

Suggested user-facing explanation flow
1) "Here is the authority chain and where behavior lives."
2) "Here is the onboarding sequence in short form."
3) "Here are the agent stories you can read for detail."
4) "Here are the user docs that mirror those stories."
5) "Here is the active configuration (features + work_mode)."
6) "Here is the command registry and how to list available tools."

Example response outline (short)
- Authority chain and doc locations.
- Onboarding steps (certification, branch init/switch, checkin, scan/tasks).
- Pointers to agent stories and user docs.
- Command registry location for tools.

Notes
- Use clear, direct language; avoid restating full policy documents.
- Keep the explanation faithful to the repo root `AGENTS.md`.
