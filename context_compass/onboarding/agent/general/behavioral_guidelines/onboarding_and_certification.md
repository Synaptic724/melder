# onboarding_and_certification

Purpose
- Describe the exact steps an agent follows when it first enters the repo.

Preconditions
- The working directory is the context_compass root.
- No tool execution or file edits before certification is complete.
- Exception: onboarding preflight wrappers may run as a read-only preflight.
- If preflight reports python unavailable, stop and request python install or an explicit context_compass/onboarding/AGENTS.md change.

Story steps
1) Resolve context_compass root and policy sources
    - Confirm the working directory is the context_compass root.
    - If present, read `AGENTS.override.md` under context_compass.
    - Read `context_compass/onboarding/AGENTS.md` for policy.

2) Read context_compass configuration and report it
    - Load SQLite system.db `config_context_compass_*` tables.
    - Summarize enabled/disabled features for the user at session start.
    - Report work_mode (hard/soft) and what it requires for tool usage.
    - If skills are disabled, state which ones are skipped and why.
    - If config tables are missing, run build/seed steps to apply defaults.

3) Load operational skills and examples (mandatory pre-cert)
    - Read the required user docs before explaining the system:
        - context_compass/onboarding/user/README.md
        - context_compass/onboarding/user/getting_started.md
        - context_compass/onboarding/user/environment_prereqs.md
        - context_compass/onboarding/user/configuration.md
        - context_compass/onboarding/user/commands.md
        - context_compass/onboarding/user/security_and_secrets.md
    - Read every skill listed in `context_compass/onboarding/agent/SKILLS.md` in order.
    - For Python edits, read `context_compass/onboarding/agent/general/skills/python/*.md` and mirror `context_compass/onboarding/agent/general/examples/python/*`.
    - For testing work, read `context_compass/onboarding/agent/general/skills/testing/*.md`.
    - After the shared baseline, ask the user to select a career (default to developer when no preference is provided).
    - Read `context_compass/onboarding/agent/careers/<career>/SKILLS.md` and the matching examples.

4) Establish agent identity (mandatory for certification)
    - Use a user-defined agent_id supplied by the user.
    - If the agent_id is missing or uncertain (e.g., after context compaction), stop and ask the user before running tools.
    - Only generate an agent id when the user explicitly requests it:
        - ToolCommandAPI command `agent_id`
    - After the career is chosen, create the agent profile:
        - ToolCommandAPI command `agent_onboarding_start`

5) Certification gate (mandatory)
    - Read `context_compass/onboarding/agent/general/skills/self_certification.md` and output the filled template.
    - Confirm the template lists all skills read from `context_compass/onboarding/agent/SKILLS.md`.
    - Ask for approval using `context_compass/onboarding/agent/general/skills/user_approved_certification.md`.
    - Wait for exact token: `CERTIFY: APPROVED`.
    - Run: `python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.
    - Exception: the onboarding bundle collector (read-only) may run before certification to gather docs.

6) Select branch runtime
    - Initialize branch state with ToolCommandAPI command `branch_init`.
    - Switch active branch (if already initialized) with ToolCommandAPI command `branch_switch`.

7) Assess repo state
    - If repo_state is missing, run an initial assessment with ToolCommandAPI command `repo_state_assess`.
    - Keep scans disabled until the repo is mature or the user requests scans.

8) Check in and mark active
    - If agent files are missing, create them with ToolCommandAPI command `agent_manage`.
    - Use ToolCommandAPI command `agent_checkin`.
    - Tool usage does not update agent profiles automatically.

9) Record environment state
    - Use ToolCommandAPI command `environment_check`.

10) Load operational skills and examples (only if scope changes)
    - Re-read any skills needed for new scope or tool changes.
    - Re-read examples if code style or test scope changes.

Artifacts touched
- SQLite user.db table: `agent_profile` (with certification and last command child tables).
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.
- SQLite system.db table: `environment_state`

Tools
- `context_compass/onboarding/system/certification/python_certified.py`
- ToolCommandAPI commands: `agent_id`, `agent_manage`, `agent_checkin`, `branch_init`,
  `branch_switch`, `repo_state_assess`, `environment_check`.

References
- `context_compass/onboarding/AGENTS.md`
- `context_compass/onboarding/agent/SKILLS.md`
- `context_compass/onboarding/agent/general/skills/self_certification.md`
- `context_compass/onboarding/agent/general/skills/user_approved_certification.md`
