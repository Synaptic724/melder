# Context and Scan Workflow

Purpose
- Describe ctx artifacts, scan behavior, and staleness handling.
- Explain how agents use context profiles to avoid full code reads.

Context artifacts
- Directory ctx: `__<Directory_Name>__.dir.json`
- File ctx: `__<FileStem>__.json`
- JSON is minified, sorted, and machine-owned where applicable.
- Architecture contexts (branch-scoped):
  - `architecture_context.json`
  - `component_contexts.json`
  - `test_architecture_context.json`
  - `test_component_contexts.json`

Preferred knowledge order
1) Directory ctx
2) File ctx
3) Code (last resort)

Structural rule (strict)
- Use directory ctx as the sole source of structural understanding.
- If directory ctx lacks required architectural detail, stop and refresh dir ctx before proceeding.
- Directory ctx must be generated from file ctx artifacts, not by reading code directly.

Scan-first rule
- Run scan at session start or read the latest scan output.
- Scan emits tasks for missing or stale ctx artifacts.
- If code changes, do not manually edit ctx JSON.
- Run scan to emit refresh tasks, then resolve them.
- If repo_state tooling_policy is restricted, scans are disabled until explicitly enabled.

Staleness states
- missing, stale, fresh, needs_review, blocked
- Tasks are emitted to generate or refresh ctx.

Context profiles
- Profiles bundle multiple ctx files for fast consumption.
- `context_profiles_survey.py` builds profiles and computes freshness.
- `context_profiles_read.py` emits ctx bundles and can emit resurvey tasks.
- `context_profiles_review.py` records human/agent review grades.

Architecture/component contexts
- Survey tools build architecture/component artifacts from directory ctx only.
- Scan checks their citation matrix and emits resurvey tasks when stale/faulty.

Test vs prod
- `context_compass/config/source_roots.json` defines prod/test roots.
- Test files use test-specific templates:
  - `context_compass/templates/file_ctx_prompt_tests.md`
  - `context_compass/templates/dir_ctx_prompt_tests.md`
