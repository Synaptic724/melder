# user

Purpose
- Hold first-class supported, user-facing content and user-defined extensions.
- Keep user tooling and artifacts separate from system-owned state.
- System databases and core state remain under `context_compass/system/`.

## Subfolders
- `agents/`: User-defined agent configs or onboarding supplements.
- `assets/`: Static assets used by user components.
- `config/`: User-facing configuration overlays or templates.
- `github_intake/`: GitHub issue intake artifacts and workflows.
- `memory/`: User-owned memory inputs (reserved for future Kuzu ingestion).
- `plans/`: Planning artifacts scoped to user workflows.
- `research/`: Research artifacts and lifecycle buckets.
- `strategies/`: High-level strategies for user-led workflows.
- `tactics/`: Tactical checklists and runbooks for user-led work.
