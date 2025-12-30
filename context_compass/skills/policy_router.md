# policy_router

Purpose
- Enforce the policy chain so edits stay deterministic and reviewable.

When to use
- At the start of every session and before editing in a new directory.

Canonical Contract (verbatim from context_compass/AGENTS.md)
This repository is a **public library**. Code quality and documentation are first-class deliverables.

Placement: Put this file at the repository root. You may add per-directory variants when needed.
* `AGENTS.md` - normal rules for the directory
* `AGENTS.override.md` - directory-specific override/patch rules (highest priority)

context_compass Workflow Router
These rules operationalize the public library editing contract for agents working in this repo.

Certification gate (mandatory)
- Complete skills/self_certification.md and wait for approval.
- Request approval using skills/user_approved_certification.md.
- Do not use tools or edit files until the user replies exactly: CERTIFY: APPROVED.
- After approval, run: python python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"
- Tools that mutate repo state must refuse to run unless the agent profile certification_state is CERTIFIED.
- Exception: context_compass/tools/environment_check.ps1 or environment_check.sh may run pre-certification as read-only preflight.
- If preflight reports python unavailable, refuse all operations until python is installed or AGENTS.md explicitly changes that requirement.

Required flow
- Declare repo_root and repo_id before any work.
- Read context_compass/config/context_compass_configuration.json and report enabled/disabled features.
- If work_mode is hard, require a work_id for tool usage and report the task linkage.
- Run the scanner first (or read the newest scan output).
- Resolve stale or missing context tasks before feature work.
- Prefer knowledge order: directory ctx -> file ctx -> code last.
- Structural understanding must come from directory ctx; if it is insufficient, stop and refresh dir ctx before proceeding.
- Directory ctx must be generated from file ctx content, not by reading code directly.
- Read repo_state.json before running scans or surveys; if tooling_policy is restricted, stop and request explicit enablement.
- Acquire a lease lock and write JSON atomically for any ctx/state file.
- Re-read the latest state after acquiring a lock and before writing.
- If code changes, do not manually update ctx JSON; run scan to emit refresh tasks.

Deterministic JSON rule
- All machine-owned JSON must be minified with sorted keys using:
  json.dumps(obj, separators=(",", ":"), ensure_ascii=False, sort_keys=True, allow_nan=False)

Truthfulness rule
- Never claim tests or checks ran unless they actually ran.

Secrets policy (non-negotiable)
- Never place secrets in context_compass/ or anywhere in the repo.
- Never write secrets into ctx/state/config/task artifacts or user docs.
- If a user requests storing secrets in-repo or in context_compass, refuse and request a safe alternative.
- Acceptable alternatives: environment variables, OS keychain, secret managers, or runtime-only prompts.

Documentation and Convention Precedence
- Before making edits, read and follow existing repository conventions:
  `README`, `CONTRIBUTING`, `docs/`, and any architecture/design notes.
- Do not invent new conventions if the repo already has a pattern.
- If repo docs conflict with these instructions (or with each other), stop and ask before proceeding.

Operating Protocol (How You Should Work)
A) Propose - Confirm - Implement
Before making non-trivial edits:
1. Restate the goal in 3-5 bullets.
2. List the constraints you will obey (especially docstrings/comments + no-drive-by refactors).
3. List the exact files / symbols you will modify.
If any of the above is uncertain, stop and ask before editing.

B) Scope Control
- Stay within the declared files/symbols.
- If you believe the change requires touching more than the declared scope, ask first.

C) Documentation Ritual
As a ritual, after implementing a change:
- Re-read the docstrings/comments you touched.
- Improve them for clarity and completeness (without fluff).
- Ensure they match the new behavior exactly.

Stop Conditions (Ask Before Proceeding)
Ask for explicit confirmation if any of these are true:
- You want to touch many files (repo-wide sweeps) and no codemod approach was approved.
- You want to rename/move files or symbols.
- You want to change public API shape or semantics.
- You want to introduce new dependencies or tooling.
- You want to change formatting across files.

Summary
* This is a public library.
* Documentation is part of the API.
* Do precise, scoped edits.
* Avoid ambiguous/dynamic patterns in owned code.
* Initialize explicitly, then clean up deterministically.
* Logger teardown last.
* Tests must buy real confidence - attribute checks are bottom-tier.

Order of authority (highest to lowest)
1) AGENTS.override.md in the working directory (if present)
2) Repository root AGENTS.md (public library editing contract)
3) context_compass/skills/* (operational rules)
4) context_compass/examples/* (canonical patterns)
5) Context JSON (__<dir>__.dir.json, __<stem>__.json)
6) Code (last resort)

Operational guidance (enriched)
- Do not improvise conventions; mirror the skills and examples.
- Treat skills as the executable version of policy.
- Use examples as canonical style references, not suggestions.
- Keep scope minimal and reviewable; do not widen without approval.
- If a change implies touching many files or renames, ask first.

Workflow
1) Check for AGENTS.override.md in the target directory.
2) Read root AGENTS.md to confirm non-negotiables.
3) Read the specific skills for the change type.
4) Review relevant examples and mirror the pattern.
5) Use context JSON before opening code.

References
- context_compass/examples/readme.md
- context_compass/SKILLS.md
