

# profile_model_explained

Purpose
- Explain profile classes, inheritance, and how profile routing works.

Profile classes
- `new`
  - First-time onboarding path.
  - Focuses on user orientation and setup.
- `general`
  - Shared system mechanics and workflow behavior.
  - Baseline class for all work.
- `engineer`
  - Code-development specialization layered on top of `general`.
  - Includes architecture/components creation and engineering quality skills.
- `user_defined/<profile_name>`
  - Optional overlay class for personal or team preferences.
  - Should extend defaults instead of replacing them.

Inheritance model
- `engineer` extends `general`.
- User-defined classes typically extend `engineer`.
- Read order is parent first, child last.
- Child maps should not duplicate parent paths.

Class selection model
- First-time entry uses `new`.
- After onboarding, user chooses steady-state default class.
- Recommended default class for development workflows: `engineer`.

Where this is configured
- `config/context_compass_config.yaml`
  - `profiles.active_profile`
  - `profiles.available_profiles`
  - `profiles.user_defined_profiles`
  - `profiles.onboarding.*`
- `roles.*`

Where inheritance is defined
- Inheritance is declared in `SKILLS.MD` headers, not in YAML inheritance
  blocks.
- Header format:
  - `INHERITS_SKILLS_FROM: <skills_path|none>`
- Parent `SKILLS.MD` paths are loaded before child `SKILLS.MD` paths.

Rules for custom classes
- Keep shared process in `general`.
- Keep engineering mechanics in `engineer`.
- Keep personal/team bias in `user_defined`.
- Avoid overlap with inherited parent paths.

References
- `agent_onboarding/default/new/skills/configuration_map_guide.md`
- `PROFILE_CLASS_CREATION_GUIDE.md`