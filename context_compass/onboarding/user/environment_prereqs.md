# Environment Prerequisites

Purpose
- Define runtime requirements for using context_compass tooling.
- Explain how to verify OS and python availability.

Required
- Python installed and accessible on PATH.
- Read/write access to the repo working directory.

Preflight checks
- Windows:
  - `powershell -File context_compass/system/ai_restricted/system_management/environment_check.ps1`
- Linux/macOS:
  - `sh context_compass/system/ai_restricted/system_management/environment_check.sh`

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
