# onboarding_and_certification

Purpose
- Describe the exact steps an agent follows when it first enters the repo.

Preconditions
- Repo root is the current working directory.
- No tool execution or file edits before certification is complete.
- Exception: environment_check.ps1/sh may run as a read-only preflight.
- If preflight reports python unavailable, stop and request python install or an explicit AGENTS.md change.

Story steps
1) Resolve repo root and policy sources
    - Confirm the working directory is the repo root.
    - If present, read `AGENTS.override.md` in the working directory.
    - Read repository root `AGENTS.md` for the public library contract.

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
        - `python context_compass/system/ai_restricted/agent_management/agent_id.py --prefix agent`
    - After the career is chosen, create the agent profile:
        - `python context_compass/system/ai_restricted/agent_management/agent_onboarding_start.py --repo-root . --agent-id <agent_id> --agent-role <career>`

5) Certification gate (mandatory)
    - Read `context_compass/onboarding/agent/general/skills/self_certification.md` and output the filled template.
    - Confirm the template lists all skills read from `context_compass/onboarding/agent/SKILLS.md`.
    - Ask for approval using `context_compass/onboarding/agent/general/skills/user_approved_certification.md`.
    - Wait for exact token: `CERTIFY: APPROVED`.
    - Run: `python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.
    - Exception: `context_compass/system/ai_restricted/agent_management/onboarding_bundle.py` may run before certification to gather docs.

6) Select branch runtime
    - Initialize branch state:
        - `python context_compass/system/ai_restricted/system_management/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
    - Switch active branch (if already initialized):
        - `python context_compass/system/ai_restricted/system_management/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

7) Assess repo state
    - If repo_state is missing, run an initial assessment:
        - `python context_compass/system/ai_restricted/system_management/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "initial assessment"`
    - Keep scans disabled until the repo is mature or the user requests scans.

8) Check in and mark active
    - If agent files are missing, create them:
        - `python context_compass/system/ai_restricted/agent_management/agent_manage.py create --repo-root . --agent-id <agent_id> --agent-role <role>`
    - `python context_compass/system/ai_restricted/agent_management/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-role <role> --agent-kind <kind> --model-name <model> --runtime <runtime>`
    - Tool usage does not update agent profiles automatically.

9) Record environment state
    - `python context_compass/system/ai_restricted/system_management/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

10) Load operational skills and examples (only if scope changes)
    - Re-read any skills needed for new scope or tool changes.
    - Re-read examples if code style or test scope changes.

Artifacts touched
- SQLite user.db table: `agent_profile` (with certification and last command child tables).
- SQLite user.db tables `agent_work_queue` and `agent_work_items`.
- SQLite system.db table: `environment_state`

Tools
- `context_compass/onboarding/system/certification/python_certified.py`
- `context_compass/system/ai_restricted/agent_management/agent_id.py`
- `context_compass/system/ai_restricted/agent_management/agent_manage.py`
- `context_compass/system/ai_restricted/system_management/branch_init.py`
- `context_compass/system/ai_restricted/system_management/branch_switch.py`
- `context_compass/system/ai_restricted/system_management/repo_state_assess.py`
- `context_compass/system/ai_restricted/agent_management/agent_checkin.py`
- `context_compass/system/ai_restricted/system_management/environment_check.py`

References
- `context_compass/onboarding/AGENTS.md`
- `context_compass/onboarding/agent/SKILLS.md`
- `context_compass/onboarding/agent/general/skills/self_certification.md`
- `context_compass/onboarding/agent/general/skills/user_approved_certification.md`
