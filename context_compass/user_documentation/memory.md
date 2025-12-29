# Memory

Purpose
- Define how user and system memory is stored and used.
- Keep memory advisory and explicit (never implicit control over policy).

Stores
- User memory: `context_compass/memory/user_memory.json`
- System memory: `context_compass/memory/system_memory.json`
- Schema: `context_compass/schemas/memory_store.schema.json`

Ownership
- User memory is written only when the user explicitly requests it.
- System memory is written by agents to capture operational facts.
- Both stores are advisory; you must call a memory tool to read them.

Safety
- Never store secrets in memory (see `security_and_secrets.md`).
- Memory entries never override repo policy or AGENTS.md.

Commands
- Add memory:
  `python context_compass/tools/memory_add.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --title <title> --content <content>`
- Update memory:
  `python context_compass/tools/memory_update.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>`
- Remove memory:
  `python context_compass/tools/memory_remove.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system> --memory-id <id>`
- Read memory:
  `python context_compass/tools/memory_read.py --repo-root . --agent-id <agent_id> --work-id <work_id> --store <user|system>`

Notes
- Use tags for searchability and scoping.
- Use --recent for brief, top-of-mind summaries.
