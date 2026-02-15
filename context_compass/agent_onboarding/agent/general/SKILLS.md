# SKILLS.md — General Career (Shared Baseline)

Index of onboarding skills and when to apply them for this repository.

Read order (baseline)
1) context_compass/SOCIAL_CONTRACT.md
2) agent_onboarding/agent/general/skills/compaction_requirements.md
3) agent_onboarding/agent/general/policies/policy_router.md
4) agent_onboarding/agent/general/skills/agent_stance.md
5) agent_onboarding/agent/general/skills/technical_expertise.md
6) agent_onboarding/agent/general/skills/mrp_policy.md
7) agent_onboarding/agent/general/skills/documentation_standards.md
8) agent_onboarding/agent/general/skills/context_gold.md
9) agent_onboarding/agent/general/skills/security_and_secrets.md
10) agent_onboarding/agent/general/skills/system_orientation.md
11) agent_onboarding/agent/general/skills/repo_topology_and_git.md
12) agent_onboarding/agent/general/skills/context_protocol.md
13) agent_onboarding/agent/general/skills/architecture_contexts.md
14) agent_onboarding/agent/general/skills/ticketing.md
15) agent_onboarding/agent/general/skills/memory_management.md
16) agent_onboarding/agent/general/skills/reactive_documentation.md
17) agent_onboarding/agent/general/skills/active_documentation.md
18) agent_onboarding/agent/general/skills/context_window_budget.md
19) agent_onboarding/agent/general/skills/active_pointerboard.md
20) agent_onboarding/agent/general/skills/ticket_closure_attention_sync.md
21) agent_onboarding/agent/general/skills/testing/testing_overview.md
22) agent_onboarding/agent/general/skills/python/docstrings.md
23) agent_onboarding/agent/general/skills/python/comments.md
24) agent_onboarding/agent/general/skills/python/typing.md
25) agent_onboarding/agent/general/skills/python/interfaces.md
26) agent_onboarding/agent/general/skills/python/init_and_ownership.md
27) agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md
28) agent_onboarding/agent/general/skills/python/logging.md
29) agent_onboarding/agent/general/skills/python/error_model.md
30) agent_onboarding/agent/general/skills/python/module_scope.md
31) agent_onboarding/agent/general/skills/python/banned_patterns.md
32) agent_onboarding/agent/general/skills/python/hot_path_attribute_aliasing.md
33) agent_onboarding/agent/general/skills/python/refactor_limits.md
34) agent_onboarding/agent/general/skills/staleness_protocol.md
35) agent_onboarding/agent/general/skills/self_certification.md
36) agent_onboarding/agent/general/skills/user_approved_certification.md

Parallel reading allowance
- The order above is canonical for reference, but parallel reading is allowed.
- All items must still be completed before certification.
- Marker-only reread output (for example, `$null = Get-Content ...` + `REREAD:` lines) is not valid completion evidence.
- Parallel/bulk reads must include substantive read integrity (concrete rule callouts) before certification.

Canonical onboarding bootstrap (default)
- Canonical readset manifest:
  `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
- Full readset completion is mandatory before certification.
- Manual source-document reading is canonical; onboarding dump artifacts are non-canonical.
- Re-onboarding attestations can keep `FILES_REREAD` compact (active ticket paths only)
  and reference onboarding docs via `ONBOARDING_READSET`.

Certification timing
- Do not request certification until every skill above has been read.
- Require the approval message to include `CERTIFY: APPROVED` and the execution environment (`active` or `inactive`).

When to read what
- Any session start: read `AGENTS.MD`, then `context_compass/SOCIAL_CONTRACT.md`, then complete the full readset, then certify.
- Any compaction or handoff re-entry: start again at `compaction_requirements.md`, complete full re-onboarding, then certify.
- Repo orientation: repo_topology_and_git, system_orientation.
- Architecture/component work: architecture_contexts, context_protocol, documentation_standards.
- Failure triage/debugging: technical_expertise + banned_patterns before proposing fixes.
- Planning and work intake: ticketing, memory_management, reactive_documentation, active_documentation, context_window_budget, policy_router.
- Active investigations and long traces: reactive_documentation + active_documentation + context_window_budget + ticket handoff sections.
- Active ticket routing and re-entry: active_pointerboard + ticket_closure_attention_sync + ticket handoff sections.
- Python code edits: policy_router + python/*.md
- Test work: testing/*.md (plus policy_router)

Policy and workflow
- agent_onboarding/agent/general/policies/policy_router.md
- agent_onboarding/agent/general/skills/ticketing.md
- agent_onboarding/agent/general/skills/ticket_closure_attention_sync.md
- agent_onboarding/agent/general/skills/context_protocol.md
- agent_onboarding/agent/general/skills/staleness_protocol.md

Python discipline
- agent_onboarding/agent/general/skills/python/docstrings.md
- agent_onboarding/agent/general/skills/python/comments.md
- agent_onboarding/agent/general/skills/python/typing.md
- agent_onboarding/agent/general/skills/python/interfaces.md
- agent_onboarding/agent/general/skills/python/init_and_ownership.md
- agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md
- agent_onboarding/agent/general/skills/python/logging.md
- agent_onboarding/agent/general/skills/python/error_model.md
- agent_onboarding/agent/general/skills/python/module_scope.md
- agent_onboarding/agent/general/skills/python/banned_patterns.md
- agent_onboarding/agent/general/skills/python/hot_path_attribute_aliasing.md
- agent_onboarding/agent/general/skills/python/refactor_limits.md

Testing discipline
- agent_onboarding/agent/general/skills/testing/testing_overview.md
- agent_onboarding/agent/general/skills/testing/pytest_unit.md
- agent_onboarding/agent/general/skills/testing/pytest_integration.md
- agent_onboarding/agent/general/skills/testing/mocking.md
- agent_onboarding/agent/general/skills/testing/regression_tests.md
- agent_onboarding/agent/general/skills/testing/evidence_reporting.md
