# onboarding_completion_and_next_step

Purpose
- Define how to finish `new` onboarding cleanly and transition to steady-state.

Completion sequence
1) Confirm user understands:
   - system purpose,
   - profile class model,
   - configuration authority.
2) Present default class options:
   - `general`
   - `engineer` (recommended)
3) Recommend `engineer` explicitly for code-development work.
4) Confirm selected class and align config guidance.
5) State next action:
   - continue onboarding via selected class path map.

Recommended wording
- "Onboarding is complete. Default class options are `general` or `engineer`.
  For code development, `engineer` is recommended. Do you want to set
  `profiles.active_profile: engineer` now?"

Exit criteria
- Selected default class is explicit.
- User is informed how to change class later in config.
- Next read path is clear and deterministic.

References
- `agent_onboarding/default/new/skills/configuration_map_guide.md`
- `config/context_compass_config.yaml`
- `router.md`
