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

3) Certification handshake
   - Fill `context_compass/skills/self_certification.md`.
   - Ask for approval using `context_compass/skills/user_approved_certification.md`.
   - Wait for `CERTIFY: APPROVED`.
   - Run: `python python_certified.py --approval-token "CERTIFY: APPROVED"`.

4) Agent identity and checkin
   - Generate an agent id if needed:
     `python context_compass/tools/agent_id.py --prefix agent`
   - Create agent profile/worklist:
     `python context_compass/tools/agent_manage.py create --repo-root . --agent-id <agent_id>`
   - Check in:
     `python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id>`

5) Branch setup
   - Initialize branch state:
     `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
   - Switch active branch:
     `python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

6) Record environment
   - `python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

7) Load skills and start work
   - Use `context_compass/SKILLS.md` to follow read order.
   - Use context JSON before opening code.

Notes
- If any step is unclear, stop and ask.
- No file edits or tool runs before certification is complete.
