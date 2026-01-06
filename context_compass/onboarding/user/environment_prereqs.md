# Environment Prerequisites

Purpose
- Define runtime requirements for using context_compass tooling.
- Explain how to verify OS and python availability.

Required
- Python installed and accessible on PATH.
- Read/write access to the repo working directory.
- Network access is required if you run the uv-based installer (downloads Python and deps).

Preflight checks
- Preflight is user-initiated; ask before running scripts.
- Preflight reports repo root, active environment status, and presence of system/user SQLite DBs.
- Windows:
  - `powershell -File context_compass/system/ai_restricted/system_management/environment_check.ps1 [-RepoRoot <path>]`
- Linux/macOS:
  - `sh context_compass/system/ai_restricted/system_management/environment_check.sh [--repo-root <path>]`

Active environment bootstrap (recommended)
- Install or repair the pinned environment:
  - Linux/macOS: `bash context_compass/onboarding/install_system.sh`
  - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\install_system.ps1`
- The onboarding install wrappers invoke the system bootstrap (env + DB seeds).
- If you only need the env, you can still run the install_active_env scripts directly.
- The installer:
  - Reads `context_compass/system/installation/environments/python_version.md`.
  - Installs/uses `uv` and creates `context_compass/system/installation/environments/active_environments/context_compass_py<version>`.
  - Installs dependencies from `context_compass/system/installation/environments/requirements.txt`.
- Activate the environment or call its python directly when running tools.
- Read the script before running if you need to audit write locations or network actions.

If python is missing
- The system must refuse operations until python is installed
  or the repo AGENTS.md explicitly allows a no-python mode.
- Do not attempt tool execution without python.
- Ask the user to run the installer instead of searching the repo for ad-hoc fixes.

System validation (python)
- After the active environment is available, validate core schemas with:
  `python context_compass/system/ai_restricted/system_management/validate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

Runtime environment state
- After checkin, run:
  `python context_compass/system/ai_restricted/system_management/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- This persists `environment_state` in system.db and emits minified JSON to stdout.

Tool availability
- The environment check records availability for:
  - git
  - rg
  - pytest

If a tool is missing
- Report it in the session summary.
- Do not install tools without explicit user request.
