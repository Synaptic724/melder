# Router

Purpose
- Define active profile roles and their `SKILLS.MD` entry points.
- Use direct profile-to-skills routing.

Available roles
- `new`
- `general`
- `engineer`
- `synaptic_python_developer`

Available path map
- `new`:
  `agent_onboarding/default/new/SKILLS.MD`
- `general`:
  `agent_onboarding/default/general/SKILLS.MD`
- `engineer`:
  `agent_onboarding/default/engineer/SKILLS.MD`
- `synaptic_python_developer`:
  `agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`

Role selection directive
1) When this router is read, list all available roles above to the user unless a role was
already chosen then skip to step 3.
2) Ask the user which role to take on for this session.
3) Read the selected role's `SKILLS.MD`.
4) Follow the role's inheritance chain parent-first.
5) Treat all paths listed in each resolved `SKILLS.MD` as active skills.

Notes
- Router defines role routing only.
- Skill activation lives in each role's `SKILLS.MD`.
