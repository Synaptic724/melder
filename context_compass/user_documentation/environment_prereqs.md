# Environment Prerequisites

Purpose
- Define runtime requirements for using context_compass tooling.
- Explain how to verify OS and python availability.

Required
- Python installed and accessible on PATH.
- Read/write access to the repo working directory.

Preflight checks
- Windows:
  - `powershell -File context_compass/tools/environment_check.ps1`
- Linux/macOS:
  - `sh context_compass/tools/environment_check.sh`

If python is missing
- The system must refuse operations until python is installed
  or the repo AGENTS.md explicitly allows a no-python mode.
- Do not attempt tool execution without python.

Runtime environment state
- After checkin, run:
  `python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- This records `context_compass/branch_management/<branch>/state/environment.json`
  and emits minified JSON to stdout.

Tool availability
- The environment check records availability for:
  - git
  - rg
  - pytest

If a tool is missing
- Report it in the session summary.
- Do not install tools without explicit user request.
