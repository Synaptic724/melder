# policy_router

Purpose
- Enforce the policy chain so edits stay deterministic and reviewable.

When to use
- At the start of every session and before editing in a new directory.

Canonical Contract (from AGENTS.MD)
This repository is a **public library**. Code quality and documentation are first-class deliverables.

Placement
- Keep `AGENTS.MD` at the repository root.
- Per-directory variants are allowed when explicitly needed.

Certification gate (mandatory)
- Complete onboarding skills and request approval.
- Require the approval message to include the exact token `CERTIFY: APPROVED` and the execution environment (`active` or `inactive`).
- Do not use tools or edit files until the user provides both the approval token and the environment.
- Git commands are active-only; skip git workflows when the environment is `inactive`.

Required flow
- Read `AGENTS.MD` and directory-local `AGENTS.MD` (if present).
- Follow `agent_onboarding/agent/general/SKILLS.md` and career-specific additions.
- Read `agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md`
  and apply its active-partner + performance-engineering rules.
- Route active work from `attention_board.md` and keep detailed state in ticket `## Notes`.
- Use the Ticket Microcycle with meaningful-finding note gates during execution.
- Use `epics/`, `stories/`, and `tasks/` tickets for all planned work.
- Prefer knowledge order: architecture/components docs -> repo docs -> code.
- If documentation is stale, update docs before proceeding with feature changes.

Truthfulness rule
- Never claim tests or checks ran unless they actually ran.

Secrets policy (non-negotiable)
- Never place secrets in the repo or in tickets/docs.
- If a user requests storing secrets in-repo, refuse and request a safe alternative.

Cleanup Usage Rule
- If a class implements cleanup, assume the object is not used after cleanup completes.
- Prefer `self.check_cleaned()` and allow it to throw; that is the intended contract.
- Only use `if self._cleaned: return` when the method must be non-throwing by contract.
- Do NOT snapshot `self._field` into locals unless absolutely necessary and justified.
- Do NOT guard internal fields with `if x is None` when lifecycle guarantees they exist pre-cleanup.
- `None` checks are for external inputs or truly optional state only.

Documentation and Convention Precedence
- Before making edits, read and follow existing repository conventions:
  `README`, `CONTRIBUTING`, `docs/`, and any architecture/design notes.
- Do not invent new conventions if the repo already has a pattern.
- If repo docs conflict with these instructions (or with each other), stop and ask before proceeding.

Unknowns Gate (No Unverified Claims)
- Any statement not supported by evidence is UNKNOWN.
- UNKNOWN is the default claim state for new findings.
- Evidence means at least one of:
  - A specific source file reference (preferred: file + symbol/method/class name).
  - A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).
- If not evidenced => UNKNOWN.
- UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section).
- UNKNOWN items must be investigated by reading the relevant source(s).
- If investigation cannot be completed (missing source access, ambiguity, or time),
  the item must remain UNKNOWN and must not be promoted to fact.
- No reasonable assumptions. Do not infer behavior from naming, patterns,
  conventions, or typical frameworks. Only the code/docs count.
- When unsure:
  - Mark it UNKNOWN.
  - Identify the most likely evidence target (file + symbol).
  - Investigate, then update the doc (or leave it UNKNOWN).

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
2) AGENTS.MD
3) agent_onboarding/agent/general/skills/*
4) agent_onboarding/agent/general/examples/*
5) Repo documentation (README, docs/)
6) Code (last resort)

Operational guidance (enriched)
- Do not improvise conventions; mirror the skills and examples.
- Treat skills as the executable version of policy.
- Use examples as canonical style references, not suggestions.
- Keep scope minimal and reviewable; do not widen without approval.
- If a change implies touching many files or renames, ask first.

Workflow
1) Check for AGENTS.override.md in the target directory.
2) Read AGENTS.MD to confirm non-negotiables.
3) Read the specific skills for the change type.
4) Review relevant examples and mirror the pattern.
5) Use architecture/components docs before opening code.

References
- agent_onboarding/agent/general/examples/readme.md
- agent_onboarding/agent/SKILLS.md
