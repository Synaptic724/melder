# Repo State

Purpose
- Capture a durable assessment of repository maturity.
- Use repo_state.json to gate tooling when surveys are low value.

Where it lives
- Branch-scoped: `context_compass/branch_management/<branch>/state/repo_state.json`
- Schema: `context_compass/schemas/repo_state.schema.json`
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
- To fully disable tools, set tooling_policy.mode to restricted and disable all features listed in context_compass_configuration.json.

Workflow
1) Initialize branch state:
   `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
2) Assess lifecycle:
   `python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "early scaffolding"`
3) Enable scans when ready:
   `python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage active_dev --tooling-mode normal --clear-disabled`

Rules
- Do not edit repo_state.json manually.
- If tooling is restricted, request explicit user approval before enabling scans.
