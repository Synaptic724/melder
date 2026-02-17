# Context Compass Core

Purpose
- Hold reusable, repository-agnostic process mechanics.
- Keep these docs portable so they can be copied into another repo with minimal changes.

What belongs in `core/`
- Universal workflow definitions (ticket flow, evidence model, compaction gates).
- Generic note schemas and state-transition rules.
- Config contract docs for policy toggles.

What does not belong in `core/`
- Repository names, module-specific paths, or codebase-specific priorities.
- Team-specific interpersonal preferences that are not broadly reusable.

Quick start
1. Read `core/ticket_microcycle.md`.
2. Set profile defaults in `profiles/`.
3. Set runtime switches in `config/context_compass_config.yaml`.
