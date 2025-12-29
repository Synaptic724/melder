# repo_state

Purpose
- Describe the agent flow for assessing repo maturity and gating tooling.

Story steps
1) Confirm branch context
   - Ensure current_branch.json points to the active branch.
   - Locate repo_state.json under the branch state directory.

2) Seed repo_state.json (if missing)
   - Run:
     `python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "initial assessment"`

3) Assess lifecycle stage
   - Use repo size, stability, and test maturity to choose a stage.
   - Record a short assessment and confidence score.

4) Gate tooling based on maturity
   - For new or experimental repos, keep scan/context_profiles disabled.
   - Enable scans only when the user requests it or the repo is stable.
   - If full lockout is required, disable all features listed in context_compass_configuration.json.

5) Reassess as the repo changes
   - Re-run repo_state_assess when repo structure stabilizes or shifts.

Artifacts touched
- `context_compass/branch_management/<branch>/state/repo_state.json`

Tools
- `context_compass/tools/repo_state_assess.py`

References
- `context_compass/skills/repo_state.md`
- `context_compass/user_documentation/repo_state.md`
