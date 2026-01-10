# Repo State

Purpose
- Capture a durable assessment of repository maturity.
- Use the SQLite `repo_state` table to gate tooling when surveys are low value.

Where it lives
- Branch-scoped row in SQLite user.db table: `repo_state` (keyed by branch_name)
- Schema: `context_compass/system/schemas/repo_state.schema.json`
- Created by `branch_init.py` or `repo_state_assess.py`

Lifecycle stage
- new: early scaffolding; surveys are low signal.
- active_dev: structure exists but churn is high.
- stable: structure is stable; scans are valuable.
- production: changes are controlled; scans are allowed but cautious.
- maintenance: mostly fixes; keep surveys lean.
- experimental: high churn; avoid heavy surveys.
- archived: no new work expected; avoid scans.

Assessment signals (examples)
- new: few files, no tests, changing layout, missing boundaries.
- active_dev: modules exist, tests emerging, frequent edits across core files.
- stable: module boundaries hold, tests exist, changes are incremental.
- production: release process or change control is present.
- maintenance: mostly bugfixes, small deltas.
- experimental: refactors, renames, large file churn.
- archived: no commits expected.

Tooling policy
- mode: normal | restricted
- disabled_features: list of feature flags to block (scan, context_profiles, etc.)
- notes: rationale for restrictions
- updated_at: timestamp

Tooling gating rules
- New repos default to restricted with scan/context_profiles disabled.
- Tools refuse to run if repo_state disables their feature.
- To fully disable tools, set tooling_policy.mode to restricted and disable all features listed in SQLite config_context_compass_* tables.

What blocks scans
- repo_state.tooling_policy.mode is restricted.
- repo_state.tooling_policy.disabled_features includes scan.
- If either is true, scan and scan-dependent tools refuse to run even if feature flags are enabled.

Workflow
1) Initialize branch state:
   Use ToolCommandAPI command `branch_init`.
2) Assess lifecycle:
   Use ToolCommandAPI command `repo_state_assess`.
3) Enable scans when ready:
   Use ToolCommandAPI command `repo_state_assess`.
4) Re-enable scans after a restricted phase:
   Use ToolCommandAPI command `repo_state_assess`.

Rules
- Do not edit repo_state records manually; use repo_state_assess.
- If tooling is restricted, request explicit user approval before enabling scans.
