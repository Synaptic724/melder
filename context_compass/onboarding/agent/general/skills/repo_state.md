# repo_state

Purpose
- Provide a durable assessment of repo maturity and lifecycle stage.
- Use repo_state records to gate context tooling when scans are low value.

Where it lives
- Branch-scoped SQLite user.db table `repo_state` (branch_name key).
- Schema: `context_compass/system/schemas/repo_state.schema.json`

Ownership
- lifecycle.* is agent-owned (assessment and judgment).
- tooling_policy.* is tool-updated (use repo_state_assess.py).

Lifecycle assessment (agent-owned)
- stage: new | active_dev | stable | production | maintenance | experimental | archived
- assessment: short explanation of why the stage applies
- confidence: 0.0-1.0
- assessed_at: timestamp

Assessment guidance
- new: small repo, early scaffolding, low structure, low signal for scans.
- active_dev: structure exists but is changing frequently.
- stable: boundaries are stable, scans are valuable.
- production: changes are controlled; scans are allowed but cautious.
- maintenance: mostly fixes; keep surveys lean.
- experimental: high churn; avoid heavy surveys.
- archived: no new work expected; avoid scans.

Tooling policy (machine-owned, tool-updated)
- mode: normal | restricted
- disabled_features: list of feature flags to block (e.g., scan, context_profiles)
- notes: rationale for restrictions
- updated_at: timestamp

Rules
- For new repos, default to restricted tooling and disable scan/context_profiles until explicitly enabled.
- If tooling is restricted and the user wants scans/surveys, use ToolCommandAPI command `repo_state_assess` to enable.
- To fully disable tooling, set tooling_policy.mode to restricted and disable all features listed in SQLite config_context_compass_* tables.
- repo_state records are created by ToolCommandAPI commands `branch_init` or `repo_state_assess`.
- Do not edit repo_state records manually; use tooling.

Commands
- Update lifecycle and tooling policy:
  Use ToolCommandAPI command `repo_state_assess`.
- Restrict tooling explicitly:
  Use ToolCommandAPI command `repo_state_assess`.
- Clear disabled features:
  Use ToolCommandAPI command `repo_state_assess`.

References
- context_compass/onboarding/user/repo_state.md
