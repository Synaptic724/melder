# context_compass User Documentation

Purpose
- Provide a user-facing explanation of how the context_compass system works.
- Describe onboarding, configuration, work management, and safety rules.
- Serve as the canonical guide for humans operating the system.

Quick navigation
- getting_started.md: onboarding sequence, certification, and agent checkin.
- environment_prereqs.md: OS and python requirements plus environment checks.
- configuration.md: feature flags, work mode, and skill overrides.
- context_and_scan.md: ctx artifacts, scan workflow, and staleness handling.
- work_management.md: queues, tickets, and agent work assignment.
- branching_and_state.md: branch-scoped state and global self_context.
- security_and_secrets.md: strict secret handling policy and refusal rules.

Non-negotiables (summary)
- No secrets in context_compass/ or anywhere in the repo.
- No tool execution or file edits before certification is complete.
- Context JSON is updated only by scan tasks after code edits.
- All machine-owned JSON is minified and written atomically with locks.

If any policy conflicts with repo rules, the repo root AGENTS.md wins.
