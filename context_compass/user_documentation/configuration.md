# Configuration

Purpose
- Explain how context_compass configuration controls tools and skills.

Configuration file
- `context_compass/config/context_compass_configuration.json`
- Schema: `context_compass/schemas/context_compass_configuration.schema.json`
- Machine-owned, minified JSON.

Feature flags
- environment_check: environment_check.py allowed.
- scan: scan tool allowed.
- context_profiles: profile survey/read/review/resurvey allowed.
- work_management: work queue tools allowed.
- ticket_intake: ticket promotion allowed.
- validation: schema validation allowed.

Skill overrides
- disabled_skill_ids: exact skill ids to skip (e.g., `python/docstrings`).
- disabled_skill_prefixes: prefix-based skips (e.g., `testing/`).

Work mode
- hard: tools require a work_id.
- soft: tools may run without a work_id.

Session reporting
- At session start, report enabled/disabled features and skill skips.
- If the configuration file is missing or invalid, default to all features enabled.

Related config files
- `context_compass/config/ignore.json` (scan ignore rules)
- `context_compass/config/policies.json` (lease TTLs, thresholds)
- `context_compass/config/source_roots.json` (prod/test roots)
