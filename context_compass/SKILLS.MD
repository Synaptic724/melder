
# SKILLS Role Map

Purpose
- Define active profile roles and their `SKILLS.MD` entry points.
- Use direct profile-to-skills routing from this top-level `SKILLS.MD` file.

Available roles
- `new`
- `general`
- `engineer`
- `user_defined/*`

Available path map
- `new`: `agent_onboarding/default/new/SKILLS.MD`
- `general`: `agent_onboarding/default/general/SKILLS.MD`
- `engineer`: `agent_onboarding/default/engineer/SKILLS.MD`
- `user_defined/*`: `agent_onboarding/user_defined/<name>/SKILLS.MD`

Role selection directive (non-negotiable)
1) When this `SKILLS.MD` map is read, list the available roles.
2) Ask the user which role to take on (unless the user already selected one).
3) Resolve the selected role to its `SKILLS.MD` path from this map.
4) Read the resolved role `SKILLS.MD`.
5) Treat the resolved role `SKILLS.MD` chain as the routing manifest:
   - You MUST read every path listed under **Active skills** / **Required baseline skills**
     in each resolved `SKILLS.MD` file (parent-first).
   - **On-demand** skills are conditional: do NOT read them for certification unless a trigger condition is met.
   - If an on-demand trigger is met, those on-demand paths become mandatory and MUST be read
     before proceeding in that scope.

Notes
- This file is a routing manifest, not a license to read the whole repo.
- Baseline/on-demand triggers are defined in the resolved role `SKILLS.MD` files and enforced
  by `AGENTS.MD` and `compaction_requirements.md`.

