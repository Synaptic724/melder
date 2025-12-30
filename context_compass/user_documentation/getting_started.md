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
   - Run `context_compass/tools/environment_check.ps1` (Windows) or
     `context_compass/tools/environment_check.sh` (Linux/macOS).
   - If python is missing, stop and install python before proceeding.

2) Read configuration
   - File: `context_compass/config/context_compass_configuration.json`
   - Report enabled/disabled features and work_mode (hard/soft).

3) Agent identity
   - Generate an agent id if needed:
     `python context_compass/tools/agent_id.py --prefix agent`

4) Certification handshake
   - Fill `context_compass/skills/self_certification.md`.
   - Ask for approval using `context_compass/skills/user_approved_certification.md`.
   - Wait for `CERTIFY: APPROVED`.
   - Run: `python python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.

5) Agent files and checkin
   - Create agent profile/worklist:
     `python context_compass/tools/agent_manage.py create --repo-root . --agent-id <agent_id>`
   - Check in:
     `python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-kind <kind> --model-name <model> --runtime <runtime>`

6) Branch setup
   - Initialize branch state:
     `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
   - Switch active branch:
     `python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

7) Assess repo state
   - If the repo is new or unstable, keep scans disabled:
     `python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "early scaffolding"`
   - When the repo matures, enable scans:
     `python context_compass/tools/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage active_dev --tooling-mode normal --clear-disabled`

8) Record environment
   - `python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

9) Load skills and start work
   - Use `context_compass/SKILLS.md` to follow read order.
   - Use context JSON before opening code.

10) Review available commands (optional)
   - Generate registries:
     `python context_compass/tools/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
   - Read `context_compass/commands/commands_user.json` for user-facing tools.

Notes
- If any step is unclear, stop and ask.
- No file edits or tool runs before certification is complete.
