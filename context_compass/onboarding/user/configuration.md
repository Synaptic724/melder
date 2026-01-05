# Configuration

Purpose
- Explain how context_compass configuration controls tools and skills.

Configuration source
- Runtime source: SQLite `system.db` tables (`config_context_compass_core`, `config_context_compass_flags`, `config_context_compass_skill_rules`).
- If SQLite tables are missing, defaults are seeded into SQLite.

Feature flags
- environment_check: environment_check.py allowed.
- scan: scan tool allowed.
- memory: memory store tools allowed.
- command_registry: command registry generation allowed.
- context_profiles: profile survey/read/review/resurvey allowed.
- architecture_contexts: architecture/component survey/check/resurvey allowed.
- work_management: work queue tools allowed.
- ticket_intake: ticket promotion allowed.
- validation: schema validation allowed.

Repo state gating
- Feature flags are further gated by the SQLite `repo_state` table for the active branch.
- If repo_state tooling_policy disables a feature, tools refuse to run even when config enables it.
- Use repo_state_assess.py to update lifecycle stage and tooling_policy.

Skill overrides
- disabled_skill_ids: exact skill ids to skip (e.g., `python/docstrings`).
- disabled_skill_prefixes: prefix-based skips (e.g., `testing/`).

Work mode
- hard: tools require a work_id.
- soft: tools may run without a work_id.

Session reporting
- At session start, report enabled/disabled features and skill skips.
- If the system database or config tables are missing, tools fail fast until build steps run.

Scan ignore rules
- Runtime source: SQLite `system.db` tables (`config_ignore_core`, `config_ignore_rules`).
- Optional seed override: `context_compass/system/config/ignore.json` (if present).
- include_dirs: optional allowlist of directories (prefix or glob).
- include_globs: optional file globs to include.
- exclude_dirs: directory prefixes/globs to skip (excludes always win).
- exclude_globs: file globs to skip (excludes always win).
- If include_* is empty, scan everything except excludes.
- If include_* is set, scan only included paths, then subtract excludes.
- Defaults exclude common noise directories: .git, .idea, .vscode, node_modules, dist, build,
  __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, .venv, venv, and context_compass
  (including context_compass).

Policies
- Runtime source: SQLite `system.db` tables (`config_policies_core`, `config_policies_ci_fail_states`).
- Optional seed override: `context_compass/system/config/policies.json` (if present).
- Policies control lease timings, scan review thresholds, and context profile sizing.

Source roots
- Runtime source: SQLite `system.db` tables (`config_source_roots_core`, `config_source_roots_entries`).
- Optional seed override: `context_compass/system/config/source_roots.json` (if present).
- prod_roots/test_roots define which directories are treated as production vs test.
- After editing an override file, re-run the SQLite build/seed steps to refresh system.db.

Languages
- Runtime source: SQLite `system.db` tables (`config_languages_core`, `config_languages_extensions`,
  `config_languages_directory_hints`).
- Optional seed override: `context_compass/system/config/languages.json` (if present).
- extensions map file suffixes to languages; directory_hints map path patterns to languages.
- After editing an override file, re-run the SQLite build/seed steps to refresh system.db.

Optional config overrides (if present)
- `context_compass/system/config/ignore.json` (scan ignore rules seed)
- `context_compass/system/config/policies.json` (lease TTLs, thresholds seed)
- `context_compass/system/config/source_roots.json` (prod/test roots seed)
- `context_compass/system/config/languages.json` (extension + directory language mapping seed)
