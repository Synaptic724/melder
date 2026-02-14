# Context Compass Profiles

Purpose
- Store repository-specific overlays on top of `core/` mechanics.
- Keep profile rules explicit so they can be swapped or tuned without changing core docs.

Profile content checklist
- Repository naming and path conventions.
- Code quality bars and review expectations.
- Scope and approval gates.
- Testing/validation expectations.
- Performance or architecture priorities.

How to use
1. Start from `profiles/default_general_profile.md`.
2. Add project-specific overrides in a new profile file.
3. Select active profile in `config/context_compass_config.yaml`.
