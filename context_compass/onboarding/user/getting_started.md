# Getting Started

Purpose
- Walk a user or agent through the first session flow.
- Explain certification, checkin, and branch setup in clear steps.

Prerequisites
- Python installed and available on PATH.
- Repo root is the current working directory.
- Read the repo root AGENTS.md for the public library contract.

Step-by-step onboarding
1) Preflight (optional but recommended)
   - Run `context_compass/system/ai_restricted/system_management/environment_check.ps1` (Windows) or
     `context_compass/system/ai_restricted/system_management/environment_check.sh` (Linux/macOS).
   - If python is missing, stop and install python before proceeding.

2) Read configuration
   - Source: SQLite `system.db` tables (`config_context_compass_core`, `config_context_compass_flags`,
     `config_context_compass_skill_rules`).
   - Report enabled/disabled features and work_mode (hard/soft).

3) Agent identity
   - Generate an agent id if needed:
     `python context_compass/system/ai_restricted/agent_management/agent_id.py --prefix agent`

4) Certification handshake
   - Fill `context_compass/onboarding/agent/general/skills/self_certification.md`.
   - Ask for approval using `context_compass/onboarding/agent/general/skills/user_approved_certification.md`.
   - Wait for `CERTIFY: APPROVED`.
   - Run: `python context_compass/system/ai_restricted/agent_management/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.

5) Agent files and checkin
   - Create agent profile/worklist:
     `python context_compass/system/ai_restricted/agent_management/agent_manage.py create --repo-root . --agent-id <agent_id> --agent-role <role>`
   - Check in:
     `python context_compass/system/ai_restricted/agent_management/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-role <role> --agent-kind <kind> --model-name <model> --runtime <runtime>`

6) Branch setup
   - Initialize branch state:
     `python context_compass/system/ai_restricted/system_management/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
   - Switch active branch:
     `python context_compass/system/ai_restricted/system_management/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

7) Assess repo state
   - If the repo is new or unstable, keep scans disabled:
     `python context_compass/system/ai_restricted/system_management/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "early scaffolding"`
   - When the repo matures, enable scans:
     `python context_compass/system/ai_restricted/system_management/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage active_dev --tooling-mode normal --clear-disabled`

8) Record environment
   - `python context_compass/system/ai_restricted/system_management/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

9) Load skills and start work
   - Use `context_compass/onboarding/agent/SKILLS.md` to follow read order.
   - Use context JSON before opening code.

10) Review available commands (optional)
   - Generate registries:
     `python context_compass/system/ai_restricted/system_management/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
   - Query `command_registry_user` in `context_compass/system/storage/sqlite/user.db` for user-facing tools.
   - Optional: add `--export-json` to emit JSON files under `context_compass/commands/`.

Notes
- If any step is unclear, stop and ask.
- No file edits or tool runs before certification is complete.
