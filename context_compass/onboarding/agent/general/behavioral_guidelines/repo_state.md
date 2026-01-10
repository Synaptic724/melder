# repo_state

Purpose
- Describe the agent flow for assessing repo maturity and gating tooling.

Story steps
1) Confirm branch context
   - Ensure SQLite user.db table `current_branch` points to the active branch.
   - Locate repo_state in SQLite user.db table `repo_state` keyed by branch_name.

2) Seed repo_state (if missing)
   - Run ToolCommandAPI command `repo_state_assess`.

3) Assess lifecycle stage
   - Use repo size, stability, and test maturity to choose a stage.
   - Record a short assessment and confidence score.

4) Gate tooling based on maturity
   - For new or experimental repos, keep scan/context_profiles disabled.
   - Enable scans only when the user requests it or the repo is stable.
   - If full lockout is required, disable all features listed in SQLite config_context_compass_* tables.

5) Reassess as the repo changes
   - Re-run repo_state_assess when repo structure stabilizes or shifts.

Artifacts touched
- SQLite user.db table `repo_state` (branch_name key).

Tools
- ToolCommandAPI command `repo_state_assess`.

References
- `context_compass/onboarding/agent/general/skills/repo_state.md`
- `context_compass/onboarding/user/repo_state.md`
