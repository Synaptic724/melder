# agents

Purpose
- Store user-defined agent profiles, onboarding supplements, and role guidance.
- Keep user-facing agent docs separate from system-owned agent state.

Notes
- Do not store SQLite state here; system DBs remain under `context_compass/system/`.
- Keep artifacts human-readable and versionable.
