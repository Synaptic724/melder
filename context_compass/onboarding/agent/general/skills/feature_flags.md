# feature_flags

Purpose
- Define how context_compass feature gates and skill overrides are configured.
- Allow the repo to disable specific tools/skills while the system is in flux.
- Make the active configuration explicit at the start of each session.

When to use
- At the start of every session (before certification).
- Before running any context_compass tool that writes state or emits tasks.
- When deciding which skills are mandatory for the current run.

Configuration source
- SQLite `system.db` tables (`config_context_compass_core`, `config_context_compass_flags`,
  `config_context_compass_skill_rules`).
- If SQLite tables are missing, run the build/seed steps to apply defaults.
- Override files are machine-owned and minified JSON; SQLite is the source of truth.

Feature flags (tools must enforce)
- environment_check: allow or block ToolCommandAPI command `environment_check`.
- repo_state: allow or block repo_state assessment tooling.
- scan: allow or block ToolCommandAPI command `scan`.
- memory: allow or block memory store tools.
- command_registry: allow or block command registry generation.
- context_profiles: allow or block context profile survey/read/review/resurvey tools.
- architecture_contexts: allow or block architecture/component context survey/check/resurvey tools.
- work_management: allow or block work queue tools and any task emission into work queues.
- ticket_intake: allow or block ToolCommandAPI command `ticket_promote`.
- validation: allow or block ToolCommandAPI command `validate`.

Skill overrides (agent behavior)
- disabled_skill_ids: exact skill ids to skip (e.g., `python/docstrings`).
- disabled_skill_prefixes: prefix-based skips (e.g., `python/`, `testing/`).

Work mode (task enforcement)
- work_mode: hard | soft
- hard: tools require a work_id for execution (blocks tool runs without an active task).
- soft: tools may run without a work_id (best for early bootstrapping).
- Default: soft.

Rules
- If a feature is disabled, do not run the tool; report that it is disabled.
- If a skill is disabled, do not enforce that skill's requirements in this session.
- `context_compass/onboarding/AGENTS.md` and any `AGENTS.override.md` under context_compass remain authoritative unless explicitly overridden.
- Always tell the user which skills are skipped due to configuration.
- If environment preflight reports python unavailable, refuse operations until python is installed or context_compass/onboarding/AGENTS.md changes the requirement.
- If repo_state tooling_policy disables a feature, refuse the tool until repo_state is updated.

Required session report (example)
- Config source: SQLite system.db `config_context_compass_*` tables
- Enabled features: environment_check, repo_state, scan, context_profiles, architecture_contexts, work_management, ticket_intake, validation
- Disabled features: (none)
- Disabled skill ids: (none)
- Disabled skill prefixes: (none)

Implementation notes
- Tools must call the feature guard before doing work.
- Task-emitting tools must additionally check work_management if tasks will be written.
