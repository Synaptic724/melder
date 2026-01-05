# Environment Prerequisites

Purpose
- Define runtime requirements for using context_compass tooling.
- Explain how to verify OS and python availability.

Required
- Python installed and accessible on PATH.
- Read/write access to the repo working directory.
- Network access is required if you run the uv-based installer (downloads Python and deps).

Preflight checks
- Windows:
  - `powershell -File context_compass/system/ai_restricted/system_management/environment_check.ps1`
- Linux/macOS:
  - `sh context_compass/system/ai_restricted/system_management/environment_check.sh`

Active environment bootstrap (recommended)
- Install or repair the pinned environment:
  - Linux/macOS: `bash context_compass/system/installation/environments/linux/install_active_env.sh`
  - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\system\installation\environments\windows\install_active_env.ps1`
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
