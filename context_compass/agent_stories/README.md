# agent_stories

Purpose
- Provide narrative, step-by-step stories for how agents operate in this repo.
- Organize the flows so humans and agents can reason about the system consistently.

Source of truth
- Behavior rules live in `AGENTS.md` (root) and `context_compass/skills/*`.
- These stories are descriptive and must not override policy.

How to use
- Start with `onboarding_and_certification.md`.
- Then read the story that matches the work you are about to do.

Stories (index)
- `onboarding_and_certification.md`: repo entry, certification gate, and first checkin.
- `agent_lifecycle_and_heartbeat.md`: agent_id, checkin/checkout, heartbeat, cleanup, archive.
- `repo_state.md`: repo maturity assessment and tooling gating.
- `work_intake_and_execution.md`: GitHub intake to backlog, active work, and completion.
- `context_maintenance_and_scan.md`: ctx freshness, scanner, staleness tasks, and validation.
- `context_profiles_flow.md`: survey/read/review/resurvey of context bundles.
- `architecture_contexts.md`: architecture/component contexts, survey flow, and resurvey tasks.
- `command_registry.md`: command discovery and registry generation.
- `memory_management.md`: user/system memory usage and hygiene.
- `task_execution_and_validation.md`: executing tasks, locking, atomic writes, and truthful validation.
