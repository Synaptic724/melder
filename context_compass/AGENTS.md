# AGENTS.md - context_compass Work Router

Purpose
- Provide the operational entrypoint for agents working in this repo.
- Route agents to the authoritative policy, skills, examples, tools, and state.
- Describe the onboarding sequence in full so behavior is deterministic.

This file does not restate behavioral policy; it points to the skills where the
full contract now lives. Treat those skills as the executable version of policy.

Authority chain (highest to lowest)
1) AGENTS.override.md in the working directory (if present)
2) Repository root AGENTS.md (public library editing contract)
3) context_compass/skills/* (operational rules)
4) context_compass/examples/* (canonical patterns)
5) Context JSON (__<dir>__.dir.json, __<stem>__.json)
6) Code (last resort)

Directory map and purpose
- Repository root AGENTS.md: the canonical public library editing contract.
- context_compass/AGENTS.md: this work router (operational onboarding and flow).
- context_compass/SKILLS.md: skill index and read order.
- context_compass/skills/: detailed, enforceable rules for behavior, editing, and testing.
- context_compass/examples/: canonical patterns; mirror these for style and contracts.
- context_compass/schemas/: JSON schemas for ctx/state/tools artifacts.
- context_compass/config/: ignore rules, policies, language hints, feature flags.
- context_compass/config/source_roots.json: prod/test root mapping for surveys and templates.
- context_compass/templates/: ctx generation prompt templates.
- context_compass/templates/*_tests.md: test-specific ctx templates for test_roots.
- context_compass/branch_management/: branch-scoped state and work queues.
- context_compass/memory/: global user and system memory stores plus locks.
- context_compass/commands/: command registry JSON plus usage notes.
- context_compass/self_context/: agent identity, certification, active agent registry, and profiles.
- context_compass/tools/: scanner, leasing, validation, and self_context utilities.
- context_compass/tools/cleanup_agents/: cleanup modules run by agent_cleanup and tool heartbeat.
- context_compass/archive/: archived agent records for audit.
- context_compass/github_intake/: raw incoming GitHub tickets (copilot writes here).
- context_compass/work_management/: global epic/story/task queues by state (shared history).
- context_compass/agent_stories/: narrative flows for onboarding, context, and work execution.
- context_compass/user_documentation/: user-facing guides for onboarding, configuration, and safety.

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
   - If python availability is unknown, run context_compass/tools/environment_check.ps1 or environment_check.sh (read-only preflight).
   - If preflight reports python unavailable, refuse all operations until python is installed or AGENTS.md is updated to allow a no-python mode.

2) Read context_compass configuration and report it
   - Load context_compass/config/context_compass_configuration.json.
   - Summarize enabled/disabled features for the user at session start.
   - Report work_mode (hard/soft) and how it affects tool usage.
   - If skills are disabled, state which ones are skipped and why.
   - If the config file is missing, assume all features enabled (defaults).

3) Select branch runtime (mandatory)
   - Run branch_init.py once per branch to seed branch state and queues.
   - Run branch_switch.py to set the active branch pointer.
   - Confirm context_compass/branch_management/current_branch.json matches the active branch.

4) Certification gate (mandatory)
   - Read context_compass/skills/self_certification.md and produce the filled template.
   - Ask for approval using context_compass/skills/user_approved_certification.md.
   - Wait for the exact approval token: CERTIFY: APPROVED.
   - Run python python_certified.py --approval-token "CERTIFY: APPROVED".
   - Do not run tools or edit files until certification is confirmed.
   - Exception: context_compass/tools/onboarding_bundle.py may run before certification to gather docs.

4) Check in and start heartbeat tracking
   - If you need a session id, run python context_compass/tools/agent_id.py --prefix agent.
   - Run python context_compass/tools/agent_checkin.py --repo-root . --agent-id <agent_id>.
   - Cleanup scripts run automatically on each tool invocation.
   - Staleness thresholds are configured in context_compass/config/policies.json.
   - Every context_compass tool invocation must update the agent heartbeat.
   - After checkin, run python context_compass/tools/environment_check.py --repo-root . --agent-id <agent_id> --work-id <work_id> to record OS/runtime state.

5) Load operational skills and examples
   - Use context_compass/SKILLS.md as the read-order index.
   - For Python edits, read skills/python/*.md (docstrings through refactor_limits) and mirror examples/python/*.
   - For testing work, read skills/testing/*.md (testing_overview through evidence_reporting) and mirror test examples.

6) Establish context state
   - Run the scanner or read the newest scan output.
   - Read directory ctx first and use it as the sole source of structural understanding.
   - If directory ctx is insufficient for structure, stop and refresh dir ctx before proceeding.
   - Read file ctx only after structure is established.
   - Open code only if ctx is missing or insufficient.
   - Read repo_state.json to confirm lifecycle stage and tooling_policy before running scan or surveys.
   - If ctx is stale or missing, resolve those tasks before feature work.
   - If architecture/component contexts are stale or faulty, resurvey them before relying on them.

7) Task execution rules
   - Use lease locks for any ctx/state writes.
   - Always re-read the latest state after acquiring a lock and before writing.
   - Write JSON atomically (write temp, then replace).
   - Keep machine JSON minified and sorted for deterministic diffs.
   - Pass --agent-id to context_compass tools so heartbeat state is recorded.

8) Perform requested work
   - Use context JSON as primary truth.
   - Keep scope narrow and reviewable.
   - Follow skill-specific rules for docstrings, logging, cleanup, typing, and tests.

9) Restore freshness after edits
   - Do not manually edit ctx JSON after code changes.
   - Run scan to emit ctx refresh tasks, then resolve them.
   - Re-scan or validate to return freshness_state to fresh.
   - Update self_context and active_agents if required by tooling.

10) Report validation truthfully
   - If tests were run, say so with the exact commands.
   - If not run, report "Not run."

11) Check out when work ends
    - Run python context_compass/tools/agent_checkout.py --repo-root . --agent-id <agent_id>.

Where the behavior contract lives
- Feature flags and skill overrides: context_compass/skills/feature_flags.md
- Policy router and workflow: context_compass/skills/policy_router.md
- Context protocol and staleness: context_compass/skills/context_protocol.md, context_compass/skills/staleness_protocol.md
- Certification handshake: context_compass/skills/self_certification.md, context_compass/skills/user_approved_certification.md
- System orientation: context_compass/skills/system_orientation.md
- Command registry: context_compass/skills/command_registry.md
- Memory management: context_compass/skills/memory_management.md
- Python discipline: context_compass/skills/python/*.md
- Testing discipline: context_compass/skills/testing/*.md
- Branch state and cloning: context_compass/skills/branch_management.md

If any policy conflicts or is unclear, stop and ask before proceeding.
