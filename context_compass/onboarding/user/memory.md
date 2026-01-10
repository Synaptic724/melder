# Memory

Purpose
- Define how user and system memory is stored and used.
- Keep memory advisory and explicit (never implicit control over policy).

Stores
- User memory: `context_compass/system/memory/user_memory.json`
- System memory: `context_compass/system/memory/system_memory.json`
- Schema: `context_compass/system/schemas/memory_store.schema.json`

Ownership
- User memory is written only when the user explicitly requests it.
- System memory is written by agents to capture operational facts.
- Both stores are advisory; you must call a memory tool to read them.

Safety
- Never store secrets in memory (see `security_and_secrets.md`).
- Memory entries never override repo policy or `context_compass/onboarding/AGENTS.md`.

Commands
- Add memory with ToolCommandAPI command `memory_add`.
- Update memory with ToolCommandAPI command `memory_update`.
- Remove memory with ToolCommandAPI command `memory_remove`.
- Read memory with ToolCommandAPI command `memory_read`.

Notes
- Use tags for searchability and scoping.
- Use --recent for brief, top-of-mind summaries.
