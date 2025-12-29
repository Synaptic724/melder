# context_protocol

Purpose
- Make context JSON the primary source of truth so code is a last resort.

When to use
- Before any code edits, investigations, or architectural changes.

Canonical Contract (verbatim from context_compass/AGENTS.md)
Required flow
- Run the scanner first (or read the newest scan output).
- Resolve stale or missing context tasks before feature work.
- Prefer knowledge order: directory ctx -> file ctx -> code last.
- Acquire a lease lock and write JSON atomically for any ctx/state file.
- Re-read the latest state after acquiring a lock and before writing.
- If code changes, do not manually update ctx JSON; run scan to emit refresh tasks.

Deterministic JSON rule
- All machine-owned JSON must be minified with sorted keys using:
  json.dumps(obj, separators=(",", ":"), ensure_ascii=False, sort_keys=True, allow_nan=False)

Rules
- Always read directory ctx first, then file ctx, then code.
- If ctx is stale or missing, regenerate it before feature work.
- Prefer targeted refreshes over repo-wide scans.
- After code edits, run scan to emit refresh tasks; resolve those tasks before continuing.
- Preserve computed.* ownership; only update agent.* content directly.

Context regeneration triggers
- Code hash mismatch or missing ctx file.
- Review counter indicates needs_review.
- Blocked state resolved.

Noise control
- Do not rewrite ctx JSON unless state or semantic content changes.
- Preserve computed.* fields when updating agent.* content.

Workflow
1) Read __<dir>__.dir.json for the target directory.
2) Read __<stem>__.json for the target file.
3) Open code only if ctx is missing or insufficient.
4) Run scan to emit ctx refresh tasks if you changed code.
5) Resolve the scan tasks using the ctx templates (do not hand-edit ctx while coding).
   - For test_roots, use file_ctx_prompt_tests.md and dir_ctx_prompt_tests.md.

Examples
- context_compass/examples/dir_ctx.pretty.json
- context_compass/examples/file_ctx.pretty.json
