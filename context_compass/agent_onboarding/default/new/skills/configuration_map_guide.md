

# configuration_map_guide

Purpose
- Explain where configuration lives and how class/profile routing is controlled.

Configuration file
- `config/context_compass_config.yaml`

Key sections
- `profiles`
  - active class, available classes, onboarding transitions.
- `roles_map`
  - role-to-`SKILLS.MD` mappings for default and user-defined classes.
  - `SKILLS.MD` headers define inheritance order.
- `workflow`
  - ticket microcycle and note behavior controls.
- `artifacts`
  - artifact board and lifecycle controls.

Most important keys for onboarding
- `profiles.active_profile`
  - Current active class/profile.
- `profiles.onboarding.first_time_default_profile`
  - First-time entry class (typically `new`).
- `profiles.onboarding.allowed_post_onboarding_profiles`
  - Which classes user can choose immediately after onboarding.
- `profiles.onboarding.fallback_post_onboarding_profile`
  - Safe fallback if no explicit choice is made.
- `roles.new`
  - New-role `SKILLS.MD` file path.

Class assignment basics
1) Confirm class exists in `profiles.available_profiles`.
2) Ensure its `SKILLS.MD` path exists in `roles`.
3) Set `profiles.active_profile` to the chosen class.
4) Validate `SKILLS.MD` inheritance chain
   (`INHERITS_SKILLS_FROM: ...`).

Recommended default after onboarding
- `engineer` (inherits `general` and enables code-development pathing).

Validation checks
- `rg -n \"active_profile|available_profiles|user_defined_profiles|onboarding\" context_compass/config/context_compass_config.yaml`
- `Get-Content context_compass/agent_onboarding/default/new/SKILLS.MD`
- `Get-Content context_compass/agent_onboarding/default/general/SKILLS.MD`
- `Get-Content context_compass/agent_onboarding/default/engineer/SKILLS.MD`

References
- `SKILLS.MD`
- `agent_onboarding/default/new/skills/profile_model_explained.md`
- `PROFILE_CLASS_CREATION_GUIDE.md`