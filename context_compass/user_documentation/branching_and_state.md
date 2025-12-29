# Branching and State

Purpose
- Explain how branch-scoped state works and what remains global.

Branch-scoped
- `context_compass/branch_management/<branch>/state/`
- `context_compass/branch_management/<branch>/work_management/`
- `current_branch.json` points to the active branch.

State examples
- repo_state.json: lifecycle assessment and tooling gating.
- context_profiles.json: context profile bundles and freshness.

Global (not branch-scoped)
- `context_compass/self_context/` (agent profiles, worklists, certification).
- `context_compass/config/` (feature flags, policies, roots).
- `context_compass/memory/` (user/system memory stores).
- `context_compass/commands/` (command registries).

Branch initialization
- `python context_compass/tools/branch_init.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

Branch switching
- `python context_compass/tools/branch_switch.py --repo-root . --branch-name <branch> --agent-id <agent_id> --work-id <work_id>`

Why branch state exists
- Keeps task queues and scan results isolated per branch.
- Avoids accidental cross-branch task contamination.

Do not modify branch state manually
- Use tools that acquire locks and write JSON atomically.
