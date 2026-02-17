# Router

Purpose
- Define active profile roles and their `SKILLS.MD` entry points.
- Use direct profile-to-skills routing.

Active role path map
- `new`:
  `agent_onboarding/default/new/SKILLS.MD`
- `general`:
  `agent_onboarding/default/general/SKILLS.MD`
- `engineer`:
  `agent_onboarding/default/engineer/SKILLS.MD`
- `synaptic_python_developer`:
  `agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`

Role selection directive
1) When this router is read, list all active roles above to the user.
2) Ask the user which role to take on for this session.
3) If user already explicitly selected a role in the request, confirm and use
   that role.
4) Read the selected role's `SKILLS.MD`.
5) Follow the role's inheritance chain parent-first.
6) Treat all paths listed in each resolved `SKILLS.MD` as active skills.

Notes
- Router defines role routing only.
- Skill activation lives in each role's `SKILLS.MD`.
