# Getting Started

Purpose
- Walk a user or agent through the first session flow.
- Explain certification, checkin, and branch setup in clear steps.

Prerequisites
- Python installed and available on PATH.
- Repo root is the current working directory.
- Read the repo root AGENTS.md for the public library contract.
- If the repo root AGENTS.md is missing, stop and request it before proceeding.

Quick start (experienced operators)
1) Install the active environment if python or deps are missing:
   - Linux/macOS: `bash context_compass/system/installation/environments/linux/install_active_env.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\system\installation\environments\windows\install_active_env.ps1`
2) Seed config tables if system.db is missing or after config overrides:
   - `python context_compass/system/installation/build_runner.py`
3) Certify and check in (agent_id, python_certified, agent_manage, agent_checkin).
4) Initialize/switch branch and assess repo_state (enable scan when ready).
5) Generate or describe commands when needed.

Step-by-step onboarding
1) Preflight (optional but recommended)
   - Run `context_compass/system/ai_restricted/system_management/environment_check.ps1` (Windows) or
     `context_compass/system/ai_restricted/system_management/environment_check.sh` (Linux/macOS).
   - If python is missing, install the active environment before proceeding.

2) Install/verify the active environment (if needed)
   - Linux/macOS: `bash context_compass/system/installation/environments/linux/install_active_env.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\system\installation\environments\windows\install_active_env.ps1`

3) Read configuration
   - Source: SQLite `system.db` tables (`config_context_compass_core`, `config_context_compass_flags`,
     `config_context_compass_skill_rules`).
   - If config tables are missing or overrides changed, run:
     `python context_compass/system/installation/build_runner.py`
   - Report enabled/disabled features and work_mode (hard/soft).

4) Agent identity
   - Generate an agent id if needed:
     `python context_compass/system/ai_restricted/agent_management/agent_id.py --prefix agent`

5) Certification handshake
   - Fill `context_compass/onboarding/agent/general/skills/self_certification.md`.
   - Ask for approval using `context_compass/onboarding/agent/general/skills/user_approved_certification.md`.
   - Wait for `CERTIFY: APPROVED`.
   - Run: `python context_compass/system/ai_restricted/agent_management/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.

6) Agent files and checkin
   - Create agent profile/worklist:
     `python context_compass/system/ai_restricted/agent_management/agent_manage.py create --repo-root . --agent-id <agent_id> --agent-role <role>`
   - Check in:
     `python context_compass/system/ai_restricted/agent_management/agent_checkin.py --repo-root . --agent-id <agent_id> --agent-role <role> --agent-kind <kind> --model-name <model> --runtime <runtime>`

7) Branch setup
   - Initialize branch state:
     `python context_compass/system/ai_restricted/system_management/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
   - Switch active branch:
     `python context_compass/system/ai_restricted/system_management/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

8) Assess repo state
   - If the repo is new or unstable, keep scans disabled:
     `python context_compass/system/ai_restricted/system_management/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage new --assessment "early scaffolding"`
   - When the repo matures, enable scans:
     `python context_compass/system/ai_restricted/system_management/repo_state_assess.py --repo-root . --agent-id <agent_id> --work-id <work_id> --stage active_dev --tooling-mode normal --clear-disabled`

9) Record environment
   - `python context_compass/system/ai_restricted/system_management/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

10) Load skills and start work
    - Use `context_compass/onboarding/agent/SKILLS.md` to follow read order.
    - Use context JSON before opening code.

11) Review available commands (optional)
    - Generate registries:
      `python context_compass/system/ai_restricted/system_management/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id> [--manifest-path <path>]`
    - Default manifest: `context_compass/system/ai_restricted/system_management/command_manifest.json`
    - Describe commands without SQL:
      `python context_compass/system/ai_restricted/system_management/command_registry_describe.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope user`
    - Optional: add `--export-json` to emit JSON files under `context_compass/commands/`.

Notes
- If any step is unclear, stop and ask.
- No file edits or tool runs before certification is complete.
