# memory

Purpose
- Host memory-related tooling and schemas as the system evolves toward Kuzu-backed memory.
- Keep memory-specific structure separate from core state storage.

Structure
- tools/: memory tooling and scripts (Kuzu-backed memory workflows).
- schemas/: schema descriptions for memory data stored in Kuzu.

Notes
- Operational state and queues are expected to live in SQLite under storage.
- Memory/knowledge graphs live in Kuzu under storage.
