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
- File: `context_compass/config/context_compass_configuration.json`
- Schema: `context_compass/schemas/context_compass_configuration.schema.json`
- If the file is missing or invalid, assume defaults (all features enabled).
- Config is machine-owned and stored as minified JSON.

Feature flags (tools must enforce)
- environment_check: allow or block `context_compass/tools/environment_check.py`.
- scan: allow or block `context_compass/tools/scan.py`.
- context_profiles: allow or block context profile survey/read/review/resurvey tools.
- work_management: allow or block work queue tools and any task emission into work queues.
- ticket_intake: allow or block `context_compass/tools/ticket_promote.py`.
- validation: allow or block `context_compass/tools/validate.py`.

Skill overrides (agent behavior)
- disabled_skill_ids: exact skill ids to skip (e.g., `python/docstrings`).
- disabled_skill_prefixes: prefix-based skips (e.g., `python/`, `testing/`).

Work mode (task enforcement)
- work_mode: hard | soft
- hard: tools require a work_id for execution (blocks tool runs without an active task).
- soft: tools may run without a work_id (best for early bootstrapping).
- Default: hard.

Rules
- If a feature is disabled, do not run the tool; report that it is disabled.
- If a skill is disabled, do not enforce that skill's requirements in this session.
- Root `AGENTS.md` and any `AGENTS.override.md` remain authoritative unless explicitly overridden.
- Always tell the user which skills are skipped due to configuration.
- If environment preflight reports python unavailable, refuse operations until python is installed or AGENTS.md changes the requirement.

Required session report (example)
- Config path: `context_compass/config/context_compass_configuration.json`
- Enabled features: environment_check, scan, context_profiles, work_management, ticket_intake, validation
- Disabled features: (none)
- Disabled skill ids: (none)
- Disabled skill prefixes: (none)

Implementation notes
- Tools must call the feature guard before doing work.
- Task-emitting tools must additionally check work_management if tasks will be written.
