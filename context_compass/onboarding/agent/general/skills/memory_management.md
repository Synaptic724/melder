# memory_management

Purpose
- Define how user and system memory stores are created, updated, and read.
- Ensure memory usage is explicit, advisory, and safe.

Memory stores
- User memory: `context_compass/system/memory/user_memory.json`
- System memory: `context_compass/system/memory/system_memory.json`
- Schema: `context_compass/system/schemas/memory_store.schema.json`

Ownership and authority
- User memory is written only on explicit user request.
- System memory is written by agents when recording operational facts.
- Both stores are advisory and must be invoked explicitly when needed.
- Memory entries never override repo policies or `AGENTS.md`.

Safety rules
- Never store secrets in memory (see `onboarding/agent/general/skills/security_and_secrets.md`).
- Memory writes require locks and atomic publish.
- Removal is a hard delete (entry removed from the list).

Tools
- Add: `context_compass/system/ai_restricted/memory/memory_add.py`
- Update: `context_compass/system/ai_restricted/memory/memory_update.py`
- Remove: `context_compass/system/ai_restricted/memory/memory_remove.py`
- Read: `context_compass/system/ai_restricted/memory/memory_read.py`

Usage rules
- Always specify store with --store user|system.
- When reading memory, filter by id or use --recent for the most recent entries.
- Treat memory as advisory; do not assume it is always current without verifying against context JSON or repo state.

References
- `context_compass/onboarding/user/memory.md`
