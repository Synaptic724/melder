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
   - Linux/macOS: `bash context_compass/onboarding/system/linux/install_system.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\system\windows\install_system.ps1`
2) Seed config tables if system.db is missing or after config overrides:
   - `python context_compass/system/installation/build_runner.py`
3) Certify and check in (agent_id, python_certified, agent_manage, agent_checkin).
4) Initialize/switch branch and assess repo_state (enable scan when ready).
5) Generate or describe commands when needed.

Step-by-step onboarding
1) Preflight (optional but recommended)
   - Ask the user before running preflight; this step is user-initiated.
   - Run `context_compass/system/ai_restricted/system_management/environment_check.ps1` (Windows) or
     `context_compass/system/ai_restricted/system_management/environment_check.sh` (Linux/macOS).
   - Preflight reports repo root, active environment status, and presence of system/user SQLite DBs.
   - If python is missing, install the active environment before proceeding.
   - If you are re-entering after context compaction, state that you are reloading the environment and ask to rerun preflight.

2) Install/verify the active environment (if needed)
   - Ask the user before running installation; this step is user-initiated.
   - Linux/macOS: `bash context_compass/onboarding/system/linux/install_system.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\system\windows\install_system.ps1`
   - These wrappers invoke the system installation bootstrap (env + DB seeds).
   - If you only need the env, you can still run the install_active_env scripts directly.
   - OS-specific onboarding scripts live under `context_compass/onboarding/system/`.

3) Read configuration
   - Source: SQLite `system.db` tables (`config_context_compass_core`, `config_context_compass_flags`,
     `config_context_compass_skill_rules`).
   - Optional: set python-only language config before seeding:
      - Linux/macOS: `bash context_compass/onboarding/system/linux/set_language.sh`
      - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\system\windows\set_language.ps1`
   - If config tables are missing or overrides changed, run:
     `python context_compass/system/installation/build_runner.py`
   - Report enabled/disabled features and work_mode (hard/soft).
   - After the environment is ready, optionally validate core schemas (user-initiated):
     `python context_compass/system/ai_restricted/system_management/validate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

4) Agent identity
   - The user must provide the agent_id; do not invent one.
   - If the agent_id is missing or uncertain (e.g., after context compaction), stop and ask the user before running tools.
   - Only generate an agent id when the user explicitly requests it:
     `python context_compass/system/ai_restricted/agent_management/agent_id.py --prefix agent`

5) Certification handshake
   - Fill `context_compass/onboarding/agent/general/skills/self_certification.md`.
   - Ask for approval using `context_compass/onboarding/agent/general/skills/user_approved_certification.md`.
   - Wait for `CERTIFY: APPROVED`.
   - Run: `python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`.

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
     `python context_compass/workspace/tools/general/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id> [--manifest-path <path>]`
   - Default manifest: `context_compass/system/ai_restricted/system_management/command_manifest.json`
   - Describe commands without SQL:
     `python context_compass/workspace/tools/general/command_registry_describe.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope user`
   - Describe ToolCommandAPI registry entries (full details):
     `python context_compass/workspace/tools/general/tool_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope both`
   - Describe SQL registries (full details):
     `python context_compass/workspace/tools/sql/crud/sql_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
     `python context_compass/workspace/tools/sql/query/sql_query_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
   - Optional: add `--export-json` to emit JSON files under `context_compass/commands/`.
   - Execute a command with hooks via:
     `python context_compass/workspace/tools/general/tool_execute.py --command-name <name> --payload-json '{}' --repo-root . --agent-id <agent_id> [--work-id <work_id>]`
   - Use workspace SQL facades for CRUD/query execution when needed.

Notes
- If any step is unclear, stop and ask.
- No file edits or tool runs before certification is complete.
