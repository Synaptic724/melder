# agent_id_policy

Purpose
- Ensure a stable, user-defined agent identity across onboarding and tool usage.
- Prevent silent agent_id changes after context compaction or handoffs.

Rules
- Use the agent_id supplied by the user; never invent or assume one.
- If the agent_id is missing or uncertain (for example after context compaction), stop and ask the user before running tools.
- Only generate a new agent_id when the user explicitly requests it.
- Keep the same agent_id for certification and all tool invocations.

Compaction handling
- If you detect context compaction or a session reset, tell the user you are reloading the environment.
- Ask the user to restate the agent_id before continuing.

Optional storage (user-managed)
- The user may persist an agent_id in a file or environment variable and provide it at session start.
- Do not write or change persisted identity without explicit user request.
