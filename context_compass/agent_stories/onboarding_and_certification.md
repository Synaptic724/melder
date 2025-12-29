# onboarding_and_certification

Purpose
- Describe the exact steps an agent follows when it first enters the repo.

Preconditions
- Repo root is the current working directory.
- No tool execution or file edits before certification is complete.
- Exception: environment_check.ps1/sh may run as a read-only preflight.
- If preflight reports python unavailable, stop and request python install or an explicit AGENTS.md change.

Story steps
1) Resolve repo root and policy sources
   - Confirm the working directory is the repo root.
   - If present, read `AGENTS.override.md` in the working directory.
   - Read repository root `AGENTS.md` for the public library contract.

2) Read context_compass configuration and report it
   - Load `context_compass/config/context_compass_configuration.json`.
   - Summarize enabled/disabled features for the user at session start.
   - Report work_mode (hard/soft) and what it requires for tool usage.
   - If skills are disabled, state which ones are skipped and why.
   - If the config file is missing, assume defaults (all features enabled).

3) Certification gate (mandatory)
   - Read `context_compass/skills/self_certification.md` and output the filled template.
   - Ask for approval using `context_compass/skills/user_approved_certification.md`.
   - Wait for exact token: `CERTIFY: APPROVED`.
   - Run: `python python_certified.py --approval-token "CERTIFY: APPROVED"`.
   - Exception: `context_compass/tools/onboarding_bundle.py` may run before certification to gather docs.

4) Establish agent identity
   - If needed, generate an agent id:
     - `python context_compass/tools/agent_id.py --prefix agent`
   - Create agent profile/worklist:
     - `python context_compass/tools/agent_manage.py create --repo-root . --agent-id <agent_id>`

5) Select branch runtime
   - Initialize branch state:
     - `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`
   - Switch active branch (if already initialized):
     - `python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

6) Check in and start heartbeat
   - `python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id>`
   - Tool usage must update heartbeat automatically.

7) Record environment state
   - `python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id>`

8) Load operational skills and examples
   - Use `context_compass/SKILLS.md` to follow read order.
   - For Python edits, read `context_compass/skills/python/*.md` and mirror `context_compass/examples/python/*`.

Artifacts touched
- `context_compass/self_context/certification_state.json`
- `context_compass/self_context/active_agents.json`
- `context_compass/self_context/agents/<agent_id>.profile.json`
- `context_compass/self_context/agents/<agent_id>.work.json`
- `context_compass/branch_management/<branch>/state/environment.json`

Tools
- `python_certified.py`
- `context_compass/tools/agent_id.py`
- `context_compass/tools/agent_manage.py`
- `context_compass/tools/branch_init.py`
- `context_compass/tools/branch_switch.py`
- `context_compass/tools/agent_checkin.py`
- `context_compass/tools/environment_check.py`

References
- `context_compass/AGENTS.md`
- `context_compass/SKILLS.md`
- `context_compass/skills/self_certification.md`
- `context_compass/skills/user_approved_certification.md`
