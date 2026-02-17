# first_time_profile_setup

Purpose
- Define first-time onboarding steps before steady-state profile execution.
- Centralize setup guidance for user orientation, profile selection, and
  default class assignment.

First-time setup sequence
1) Start from `AGENTS.MD` bootstrap rules.
2) Read `context_compass/SKILLS.md` and configuration authority in
   `config/context_compass_config.yaml`.
3) Explain the system purpose and onboarding model using:
   - `system_overview_for_user.md`
   - `profile_model_explained.md`
   - `configuration_map_guide.md`
4) Offer default class selection for post-onboarding:
   - `general` for system/process execution baseline.
   - `engineer` for code-development execution (inherits `general` and is
     recommended).
5) Confirm first-time completion and switch to selected default profile path
   map.

Profile intent summary
- `general`:
  shared system behavior, ticketing, policy, and execution workflow baseline.
- `engineer`:
  programming/testing/architecture/code-construction specialization layered on
  top of `general`.

User-facing recommendation
- This system is designed for code development and supports any language.
- It enhances Codex and other AI workflows by enforcing durable context.
- Recommended mode in this repo is Codex with Extra High reasoning.
- Other reasoning modes are currently untested in this repo.

Rules
- Keep README reads scoped to first-time setup (`new` profile).
- Do not require README reads for non-new profile onboarding paths.
- Treat config YAML as authoritative for profile selection/onboarding.
- Treat skill-map headers as authoritative for inheritance order.

References
- `context_compass/AGENTS.MD`
- `context_compass/config/context_compass_config.yaml`
- `context_compass/SKILLS.md`
- `agent_onboarding/default/general/SKILLS.MD`
- `agent_onboarding/default/engineer/SKILLS.MD`
- `agent_onboarding/default/new/SKILLS.MD`
- `agent_onboarding/default/new/policies/new_onboarding_policy.md`
- `agent_onboarding/default/new/behavioral_guidelines/user_onboarding_flow.md`
