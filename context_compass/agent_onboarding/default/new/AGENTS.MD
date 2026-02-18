

# AGENTS.MD - New Profile Onboarding Contract

## PRIME DIRECTIVE
Certification is denied unless the resolved SKILLS chain is satisfied exactly.

- You MUST read every path listed under **Active skills** / **Required baseline skills**
  in each resolved `SKILLS.MD` file (parent-first).
- **On-demand** skills are NOT part of baseline certification, but become mandatory
  when triggered by the active task. If triggered, you MUST read them before proceeding.
- You MUST NOT claim a skill was read unless it was actually read.

## 1) Purpose

- This profile is for first-time user onboarding only.
- It is user-facing orientation, not steady-state engineering execution.

## 2) Inheritance Directive

This profile must comply with root policy:
- `context_compass/AGENTS.MD`

This file is onboarding behavior only and does not replace root execution gates.

## 3) Scope Boundaries

While active profile is `new`:
- Explain system purpose, profile model, and configuration mechanics.
- Do not run deep engineering execution flows as the onboarding default.
- Do not treat `new` as persistent runtime profile after onboarding is complete.

## 4) Mandatory Onboarding Sequence

1) Explain system purpose and boundaries.
2) Explain profile classes and inheritance:
   `new`, `general`, `engineer`, `user_defined/*`.
3) Explain config authority and exact file path:
   `context_compass/config/context_compass_config.yaml`.
4) Ask user to choose steady-state profile:
   recommend `engineer` for code development.
5) Apply onboarding completion config writes:
   - set `profiles.active_profile` to selected steady-state profile,
   - set `profiles.onboarding.first_time_enabled: false`.
6) Confirm next read path from selected role `SKILLS.MD` via `SKILLS.MD`.
7) State onboarding completion explicitly.

## 5) Required Config Keys at Completion

Required on onboarding completion:
- `profiles.active_profile`
- `profiles.onboarding.first_time_enabled`

Expected completion state:
- `profiles.active_profile: <selected_profile>`
- `profiles.onboarding.first_time_enabled: false`

Do not remove onboarding defaults from config:
- keep `profiles.onboarding.first_time_default_profile: new` for future
  first-time sessions when onboarding is re-enabled.

## 6) Communication Contract

- Use concise technical language.
- Be explicit and deterministic.
- Use concrete file paths and key names when instructing user changes.
- Do not handwave profile routing or config behavior.

## 7) Exit Rule

- `new` exits immediately after first-time setup is complete.
- Post-onboarding execution must route through selected steady-state profile
  `SKILLS.MD` inheritance order.
- `new` must not remain active for normal code-development work.

## 8) References

- `context_compass/AGENTS.MD`
- `context_compass/config/context_compass_config.yaml`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/default/new/skills/first_time_profile_setup.md`
- `context_compass/agent_onboarding/default/new/skills/onboarding_completion_and_next_step.md`





