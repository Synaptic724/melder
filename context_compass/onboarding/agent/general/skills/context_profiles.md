# context_profiles

Purpose
- Provide agent-curated bundles of ctx JSON so the agent can load high-value context quickly and deterministically.

When to use
- After onboarding and certification, before digging through the repo.
- When you need targeted context without scanning directories manually.
- After major repo changes, re-run the survey to refresh the bundles.

What a context profile is
- A named bundle of ctx JSON paths stored in SQLite user.db table `context_profiles` (branch_name key).
- Machine-owned; edit only through tools (never by hand).
- Each profile tracks usage counts and review grades to keep the bundle useful.
- Each profile records freshness state so stale bundles trigger resurvey tasks.
- Profiles can be scoped by prod/test roots stored in SQLite (`config_source_roots_*`).
- Optional seed override: `context_compass/system/config/source_roots.json` (if present).

Ownership lanes
- Tool-owned fields: profiles list, usage_count, grades, timestamps, rules_version.
- Agent-owned intent lives in the ctx JSON referenced by the profile, not in the profile itself.

Workflow (required)
1) Survey profiles (build or refresh):
   - `python -m context_compass.tools.context_profiles_survey --agent-id <id> --work-id <work_id>`
2) Read a profile to load context:
   - `python -m context_compass.tools.context_profiles_read --agent-id <id> --profile repo_overview --work-id <work_id>`
3) Review the profile after use:
   - `python -m context_compass.tools.context_profiles_review --agent-id <id> --profile repo_overview --grade good --work-id <work_id>`
4) Resurvey tasks (optional helper):
   - `python -m context_compass.tools.context_profiles_resurvey --agent-id <id> --work-id <work_id>`

Usage counts
- `context_profiles_read` increments usage_count and last_used_at.
- Usage counts drive task emission for optimize/prune.

Review grades
- Allowed grades: excellent, good, ok, poor, bad.
- Review updates:
  - grade, last_review_at, last_reviewed_by, last_review_notes
  - review_counts[grade] increments
  - score recalculates from usage + path count

Freshness state
- freshness_state: fresh | stale | needs_review | blocked
- staleness_reasons: ctx_missing, ctx_stale, ctx_needs_review, hash_mismatch, ctx_blocked, ctx_parse_error, code_missing
- inputs_hash: stable hash of ctx inputs (expected vs actual hashes)
- last_checked_at: last time the profile inputs were evaluated
- Targeted hash checks compare ctx checksums to live code/subtree hashes without running a full scan.

Task emission rules
- If grade is poor/bad:
  - usage_count >= threshold -> emit optimize_context_profile
  - usage_count < threshold -> emit prune_context_profile
- If freshness_state changes to stale/needs_review/blocked:
  - emit resurvey_context_profile so the bundle is rebuilt
- Tasks land in SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set, bucket=ready, work_kind=task).

Feature flags
- Requires context_profiles feature enabled in SQLite `config_context_compass_*` tables.
- Task emission also requires work_management to be enabled.

Policies used
- context_profiles_max_items_per_profile
- context_profiles_max_bytes_per_profile
- context_profiles_popular_usage_threshold

Prod/test profiles
- `prod_overview`: ctx paths under prod_roots.
- `tests_overview`: ctx paths under test_roots.
- Update SQLite `config_source_roots_*` tables (seed script or CRUD) to change roots.

Tools
- `context_profiles_survey.py`: rebuilds profiles from ctx JSON + work queues.
- `context_profiles_read.py`: outputs consolidated ctx JSON and increments usage_count.
- `context_profiles_review.py`: records grade + notes and emits optimize/prune tasks.

References
- Schema: `context_compass/system/schemas/context_profiles.schema.json`
- State: SQLite user.db tables `context_profiles`, `context_profile_items`, `context_profile_item_paths`,
  and `context_profile_item_staleness_reasons`.
