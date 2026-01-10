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
- Preflight reports the context_compass root, active environment status, and presence of system/user SQLite DBs.
- Use the command that matches your current shell and OS. If you are in WSL, use the Linux/macOS command from within WSL (not Windows PowerShell).
- Windows:
  - `powershell -File context_compass/onboarding/system/windows/preflight/environment_check.ps1 [-RepoRoot <path>]`
- Linux/macOS:
  - `sh context_compass/onboarding/system/linux/preflight/environment_check.sh [--repo-root <path>]`
- If you see errors like `/usr/bin/env: 'bash\r': No such file or directory` or `^M`, normalize line endings to LF:
  - `find context_compass -name '*.sh' -print0 | xargs -0 sed -i 's/\r$//'`

Active environment bootstrap (recommended)
- Install or repair the pinned environment:
- If you are in WSL, run the Linux/macOS command from within WSL.
  - Linux/macOS: `bash context_compass/onboarding/system/linux/install/install_system.sh`
  - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\system\windows\install\install_system.ps1`
- The onboarding install wrappers invoke the system bootstrap (env + DB seeds).
- If you only need the env, you can still run the install_active_env scripts directly.
- OS-specific onboarding scripts live under `context_compass/onboarding/system/`.
- Optional: set python-only language config before seeding:
  - Linux/macOS: `bash context_compass/onboarding/system/linux/programming_language/set_language.sh`
  - Windows: `powershell -ExecutionPolicy Bypass -File context_compass\onboarding\system\windows\programming_language\set_language.ps1`
- The installer:
  - Reads `context_compass/system/installation/environments/python_version.md`.
  - Installs/uses `uv` and creates `context_compass/system/installation/environments/active_environments/context_compass_py<version>`.
  - Installs dependencies from `context_compass/system/installation/environments/requirements.txt`.
- Activate the environment or call its python directly when running tools.
- The installer writes `context_compass_repo.pth` into the active env's site-packages so
  `import context_compass` works when running scripts by file path.
  - Verify with the active env python:
    - `python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"`
    - Check for `context_compass_repo.pth` in that directory.
- Read the script before running if you need to audit write locations or network actions.

Handling Already Active Systems
- If the system is already bootstrapped (e.g., by another agent on a different OS), databases are shared.
- Seeding scripts are idempotent (safe to re-run). They use `IF NOT EXISTS` and upsert logic.
- Environments are OS-specific and effectively isolated:
  - Windows: `system/installation/environments/active_environments/windows/`
  - Linux: `system/installation/environments/active_environments/linux/`
- Running the installer for your OS will not harm the environments of other agents.

Seeding Specific Environments
- Run the OS-specific install command to create or repair your local environment.
- This creates the OS-specific virtual environment and ensures the database registry matches the current manifest.

If python is missing
- The system must refuse operations until python is installed
  or context_compass/onboarding/AGENTS.md explicitly allows a no-python mode.
- Do not attempt tool execution without python.
- Ask the user to run the installer instead of searching the repo for ad-hoc fixes.

System validation (python)
- After the active environment is available, validate core schemas via ToolCommandAPI command `validate` (see `context_compass/onboarding/user/commands.md` for execution).

Runtime environment state
- After checkin, run ToolCommandAPI command `environment_check` (see `context_compass/onboarding/user/commands.md` for execution).
- This persists `environment_state` in system.db and emits minified JSON to stdout.

Tool availability
- The environment check records availability for:
  - git
  - rg
  - pytest

If a tool is missing
- Report it in the session summary.
- Do not install tools without explicit user request.
