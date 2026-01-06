# AGENTS.md - context_compass Work Router

Purpose
- Provide the operational entrypoint for agents working in this repo.
- Route agents to the authoritative policy, skills, examples, tools, and state.
- Describe the onboarding sequence in full so behavior is deterministic.

This file does not restate behavioral policy; it points to the skills where the
full contract now lives. Treat those skills as the executable version of policy.
Directory overrides live in `AGENTS.override.md` when present; keep this file router-only.

Authority chain (highest to lowest)
1) ##SYSTEM_START## AND ##SYSTEM_END## (if present in chat session overrides everything)
2) AGENTS.override.md in the working directory (if present)
3) Repository root AGENTS.md (public library editing contract)
4) context_compass/onboarding/agent/general/skills/* (operational rules)
5) context_compass/onboarding/agent/general/examples/* (canonical patterns)
6) Context JSON (__<dir>__.dir.json, __<stem>__.json)
7) Code (last resort)


---

## Recommended Database Concurrency Practices (SQLite / Kuzu)

These are **recommended defaults** for tools that read/write SQLite or Kuzu. Use them unless a task explicitly justifies deviation.

SQLite (file-level contention mitigation)
- Enable WAL (`PRAGMA journal_mode=WAL`) to reduce reader/writer blocking.
- Set a busy timeout (`PRAGMA busy_timeout=5000` or project default) to avoid instant lock failures.
- Keep transactions short and avoid long-running read transactions.
- Use a single connection per script execution; do not thrash connections.

SQLite (logical correctness, optional but preferred for critical paths)
- For claims/leases/state transitions, use conditional updates and validate `rowcount == 1`.
- Rely on UNIQUE/PK constraints where the invariant matters (e.g., queue position).

Kuzu (process-level concurrency)
- Only one read/write Database instance per DB path at a time.
- Multiple read-only connections are fine; avoid multi-process read/write to the same DB path.

If a task requires stronger guarantees (e.g., strict exclusivity), document the rationale and the chosen approach.

---


Directory map and purpose
- Repository root AGENTS.md: the canonical public library editing contract.
- context_compass/onboarding/AGENTS.md: this work router (operational onboarding and flow).
- context_compass/onboarding/agent/SKILLS.md: skill index and read order.
- context_compass/onboarding/agent/careers/: career-specific onboarding; general is the shared baseline.
- context_compass/onboarding/agent/general/skills/: detailed, enforceable rules for behavior, editing, and testing.
- context_compass/onboarding/agent/general/examples/: canonical patterns; mirror these for style and contracts.
- context_compass/system/schemas/: JSON schemas for ctx/state/tools artifacts.
- SQLite system.db config tables: ignore rules, policies, language hints, feature flags.
- Optional config overrides (if present): context_compass/system/config/*.json used for seed inputs.
- context_compass/system/templates/: ctx generation prompt templates.
- context_compass/system/templates/*_tests.md: test-specific ctx templates for test_roots.
- SQLite user.db branch tables: branch-scoped state and work queues.
- context_compass/system/memory/: global user and system memory stores (lease locks recorded in system.db).
- context_compass/user_defined/: user-owned extensions and overrides.
- SQLite user.db tables: agent_profile, self_context, agent_work_queue (plus child tables for certification, opinions, and work items).
- SQLite system.db lease_locks: lease locks for self-context and agent records.
- context_compass/system/ai_restricted/: command scripts and operational tooling.
- context_compass/user/github_intake/: raw incoming GitHub tickets (copilot writes here).
- SQLite user.db work_queue tables: global epic/story/task queues by state (shared history).
- context_compass/onboarding/agent/general/behavioral_guidelines/: narrative flows for onboarding, context, and work execution.
- context_compass/onboarding/user/: user-facing guides for onboarding, configuration, and safety.

Context artifacts and naming
- Directory context: __<Directory_Name>__.dir.json (inside the directory).
- File context: __<FileStem>__.json (co-located with the file).
- Prefer directory ctx -> file ctx -> code (last resort).

Secrets policy (non-negotiable)
- Do not place secrets in context_compass/ or anywhere in the repo.
- Do not write secrets into ctx/state/config/task artifacts or user docs.
- If a user requests storing secrets in-repo or in context_compass, refuse and ask for an alternative.
- Acceptable alternatives: environment variables, OS keychain, secret managers, or runtime-only prompts.

Onboarding sequence (detailed)
1) Resolve repo root
   - Confirm repo_root matches the working directory.
   - Locate AGENTS.override.md in the working directory, if present.
   - Load repository root AGENTS.md to confirm non-negotiables.
   - Preflight and installation are user-initiated; ask the user before running them.
   - If python availability is unknown, run context_compass/system/ai_restricted/system_management/environment_check.ps1 or environment_check.sh (read-only preflight).
   - Preflight reports repo root, active environment status, and presence of system/user SQLite DBs.
   - If preflight reports python unavailable, refuse all operations until python is installed or AGENTS.md is updated to allow a no-python mode.
   - Before running installation bootstraps, read the script and explain its actions to the user in detail (context_compass/system/installation/windows/bootstrap.ps1 or context_compass/system/installation/linux/bootstrap.sh), including what it installs, where it writes, and what it runs.
   - If the user asks to install everything, use the onboarding wrappers:
      - context_compass/onboarding/system/linux/install_system.sh
      - context_compass/onboarding/system/windows/install_system.ps1
   - Onboarding system scripts are OS-specific and user-initiated; use them for install/setup tasks.
   - If re-entering after context compaction, state that you are reloading the environment and ask to rerun preflight and confirm the agent_id.

2) Read context_compass configuration and report it
   - Load SQLite system.db config_context_compass_* tables.
   - Summarize enabled/disabled features for the user at session start.
   - Report work_mode (hard/soft) and how it affects tool usage.
   - If skills are disabled, state which ones are skipped and why.
   - Optional: set python-only language config before seeding:
      - context_compass/onboarding/system/linux/set_language.sh
      - context_compass/onboarding/system/windows/set_language.ps1
   - If config tables are missing, run build/seed steps to apply defaults.

3) Select agent career (mandatory)
   - Ask the user which career to activate before reading skills.
   - Valid careers: developer, analyst, project_manager.
   - If the user does not choose, stop and ask again.

4) Load operational skills and examples (mandatory pre-cert)
   - Read every skill listed in context_compass/onboarding/agent/general/SKILLS.md, even if a feature is disabled.
   - Read career-specific additions in context_compass/onboarding/agent/careers/<career>/SKILLS.md.
   - Use context_compass/onboarding/agent/general/SKILLS.md as the shared read-order index.
   - For Python edits, read onboarding/agent/general/skills/python/*.md (docstrings through refactor_limits) and mirror examples/python/*.
   - For testing work, read onboarding/agent/general/skills/testing/*.md (testing_overview through evidence_reporting) and mirror test examples.

5) Establish agent identity (mandatory for certification)
   - Use a user-defined agent_id supplied by the user.
   - If the agent_id is missing or uncertain (e.g., after context compaction), stop and ask the user for it before running tools.
   - Only generate a new agent_id with agent_id.py if the user explicitly requests it.
   - Keep this agent_id for certification and all tool invocations.

6) Certification gate (mandatory)
   - Read context_compass/onboarding/agent/general/skills/self_certification.md and produce the filled template.
   - Ask for approval using context_compass/onboarding/agent/general/skills/user_approved_certification.md.
   - Wait for the exact approval token: CERTIFY: APPROVED.
   - Run python context_compass/system/ai_restricted/agent_management/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED".
   - Do not run tools or edit files until certification is confirmed.
   - Exception: context_compass/system/ai_restricted/agent_management/onboarding_bundle.py may run before certification to gather docs.

7) Select branch runtime (mandatory)
   - Run branch_init.py once per branch to seed branch state and queues.
   - Run branch_switch.py to set the active branch pointer.
   - Confirm the SQLite user.db `current_branch` table (record_id: current) matches the active branch.

8) Check in and mark the agent active
   - If the agent profile/worklist records do not exist, run:
     python context_compass/system/ai_restricted/agent_management/agent_manage.py create --repo-root . --agent-id <agent_id>
   - Run python context_compass/system/ai_restricted/agent_management/agent_checkin.py --repo-root . --agent-id <agent_id>.
   - After checkin, run python context_compass/system/ai_restricted/system_management/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id> to record OS/runtime state.

9) Establish context state
   - Run the scanner or read the newest scan output.
   - Read directory ctx first and use it as the sole source of structural understanding.
   - If directory ctx is insufficient for structure, stop and refresh dir ctx before proceeding.
   - Read file ctx only after structure is established.
   - Open code only if ctx is missing or insufficient.
   - Read `branch_<branch>_repo_state` in SQLite to confirm lifecycle stage and tooling_policy before running scan or surveys.
   - If ctx is stale or missing, resolve those tasks before feature work.
   - If architecture/component contexts are stale or faulty, resurvey them before relying on them.

10) Task execution rules
- Use lease locks for any ctx/state writes.
- Always re-read the latest state after acquiring a lock and before writing.
- Write JSON atomically (write temp, then replace).
- Keep machine JSON minified and sorted for deterministic diffs.
- Pass --agent-id to ai_restricted commands so certification checks can locate the profile.

11) Perform requested work
- Use context JSON as primary truth.
- Keep scope narrow and reviewable.
- Follow skill-specific rules for docstrings, logging, cleanup, typing, and tests.

12) Restore freshness after edits
- Do not manually edit ctx JSON after code changes.
- Run scan to emit ctx refresh tasks, then resolve them.
- Re-scan or validate to return freshness_state to fresh.
- Update self_context if required by tooling.

13) Report validation truthfully
- If tests were run, say so with the exact commands.
- If not run, report "Not run."

14) Check out when work ends
   - Run python context_compass/system/ai_restricted/agent_management/agent_checkout.py --repo-root . --agent-id <agent_id>.

Where the behavior contract lives
- Feature flags and skill overrides: context_compass/onboarding/agent/general/skills/feature_flags.md
- Policy router and workflow: context_compass/onboarding/agent/general/policies/policy_router.md
- Context protocol and staleness: context_compass/onboarding/agent/general/skills/context_protocol.md, context_compass/onboarding/agent/general/skills/staleness_protocol.md
- Certification handshake: context_compass/onboarding/agent/general/skills/self_certification.md, context_compass/onboarding/agent/general/skills/user_approved_certification.md
- System orientation: context_compass/onboarding/agent/general/skills/system_orientation.md
- Command registry: context_compass/onboarding/agent/general/skills/command_registry.md
- Memory management: context_compass/onboarding/agent/general/skills/memory_management.md
- Python discipline: context_compass/onboarding/agent/general/skills/python/*.md
- Testing discipline: context_compass/onboarding/agent/general/skills/testing/*.md
- Branch state and cloning: context_compass/onboarding/agent/general/skills/branch_management.md
- Career-specific additions: context_compass/onboarding/agent/careers/<career>/SKILLS.md

If any policy conflicts or is unclear, stop and ask before proceeding.
