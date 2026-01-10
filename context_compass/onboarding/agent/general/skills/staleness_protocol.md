# staleness_protocol

Purpose
- Define required actions for freshness state transitions and task emission.

Canonical Contract (verbatim from context_compass/onboarding/AGENTS.md)
Required flow
- Resolve stale or missing context tasks before feature work.

States and required actions
- missing: generate ctx immediately.
- stale: refresh ctx to match current code or subtree.
- needs_review: confirm architecture and update agent.* if needed.
- fresh: no action.
- blocked: emit error record and a resolve task.

Staleness reasons
- code_hash_mismatch, subtree_hash_mismatch
- missing_ctx, review_due
- schema_invalid, tool_error, permission_error

Noise control
- Update ctx JSON only when state or semantic content changes.
- Avoid rewriting ctx files on no-op scans.

Task mapping
- missing -> generate_* task
- stale -> refresh_* task
- needs_review -> review_* task
- blocked -> resolve_blocked_ctx task with error record

Enforcement rule
- Do not hand-edit ctx JSON in response to code changes; run scan so tasks drive refresh.

Scanner tooling
- Use ToolCommandAPI command `scan` to detect staleness and emit tasks.
- The scanner relies on ignore_rules, hashing, and paths helpers for deterministic output.
- SQLite `repo_state` (branch_name key) is updated via ToolCommandAPI command `update_state` (scan subcommand).

Example transitions
- missing -> fresh after ctx generation.
- stale -> fresh after refresh.
- fresh -> needs_review after review counter threshold.
- blocked -> stale after dependency fix.

Review due workflow
1) Read current dir ctx.
2) Confirm architecture and invariants.
3) Update agent.* only if truth changed.
4) Reset review counters.

Examples
- context_compass/onboarding/agent/general/examples/tasks.pretty.json
- context_compass/onboarding/agent/general/examples/scan.pretty.json
