<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Investigate Role-Local Example Doc Drift

## Metadata
- Task ID: TASK-2026-06-13-investigate-role-local-example-doc-drift
- Story: none
- Epic: none
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-13T22:51:40Z
- Updated: 2026-06-13T23:28:16Z

## Objective
Investigate whether the role-local example docs under
`agent_onboarding/default/*/examples/` have drifted behind the richer
top-level examples under `examples/`.

## Ticket Contract
- ENTRY_GATE: the top-level `examples/` lane is locally clean for the bounded
  seams already patched, and the user explicitly directed continued
  documentation work.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/default/platform_engineer/examples/platform_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/qa_engineer/examples/qa_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/security_engineer/examples/security_review_flow.md`
  - `codex/context_compass/agent_onboarding/default/researcher/examples/researcher_task_flow.md`
  - top-level comparison surfaces:
    - `codex/context_compass/examples/platform_task_flow.md`
    - `codex/context_compass/examples/qa_task_flow.md`
    - `codex/context_compass/examples/security_review_flow.md`
    - `codex/context_compass/examples/researcher_task_flow.md`
  - `codex/context_compass/attention_board.md`
  - this task
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-06-13_investigate_example_system_doc_drift_task.md`
  - the role-local example docs listed above
  - the matching top-level example docs listed above
- EXIT_GATE:
  - at least one concrete role-local example drift finding exists with
    evidence
  - the next bounded patch slice is explicit
  - no silent widening beyond the initial four role families
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  role-local example drift cannot be evaluated without changing the intended
  purpose of the role examples.

## Scope Boundaries
- In scope:
  - drift investigation for the initial platform/qa/security/researcher
    role-local example docs
  - comparison against the refreshed top-level examples
  - identifying the next bounded refresh slice
- Out of scope:
  - wider `agent_onboarding` doc maintenance
  - fiction/editor role-local examples until a separate bounded continuation
  - live `examples/` maintenance already covered by the sibling task

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to continue after the bounded
  top-level example lane became locally clean.

## Steps / Checklist
- [ ] Re-read the role-local example docs and note likely drift seams.
- [ ] Verify likely seams against the refreshed top-level examples.
- [ ] Record the first concrete drift finding in `## Notes`.
- [ ] Define the first bounded patch slice from those findings.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- evidence-backed role-local example drift inventory
- explicit next patch slice

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-06-13_investigate_role_local_example_doc_drift_task.md`
- `codex/context_compass/attention_board.md`
- role-local example docs if a bounded patch is justified

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: role-local example docs may intentionally stay lighter than top-level
  examples.
- Rollback: keep this lane investigation-first until one bounded patch is
  clearly justified.

## Applicable Anti-Patterns
- [ ] No role-local example rewrite before concrete drift is recorded.
- [ ] No widening past the initial four role families without a new note.
- [ ] No assuming top-level example richness is automatically required for all
      role-local examples.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - role-local example drift
  - top-level versus role-local example alignment
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-13T22:51:40Z
  TYPE: PLAN
  CLAIM: The next bounded docs lane is role-local example drift. The top-level
    `examples/` lane is locally clean for the seams already patched, so the
    safest continuation is to investigate whether the source role examples have
    fallen behind those refreshed public examples.
  EVIDENCE:
  - user_instruction: `continue please`
  - codex/context_compass/tickets/tasks/2026-06-13_investigate_example_system_doc_drift_task.md
  IMPACT: This keeps the docs program moving without silently widening back
    into already-cleaned example files.
  NEXT: compare the initial platform/qa/security/researcher role-local example
    docs against their refreshed top-level counterparts and record the first
    concrete seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:52:34Z
  TYPE: FACT
  CLAIM: The initial role-local example quartet is concretely behind the
    refreshed top-level examples. The platform/qa/security/researcher
    role-local docs still use the older concise example form, while the
    top-level examples now carry current entry-gate and deliverable framing.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/platform_engineer/examples/platform_task_flow.md:2-20
  - codex/context_compass/agent_onboarding/default/qa_engineer/examples/qa_task_flow.md:2-22
  - codex/context_compass/agent_onboarding/default/security_engineer/examples/security_review_flow.md:2-20
  - codex/context_compass/agent_onboarding/default/researcher/examples/researcher_task_flow.md:1-19
  - codex/context_compass/examples/platform_task_flow.md:1-39
  - codex/context_compass/examples/qa_task_flow.md:1-35
  - codex/context_compass/examples/security_review_flow.md:1-31
  - codex/context_compass/examples/researcher_task_flow.md:1-37
  IMPACT: The canonical role-local examples now under-teach the current
    repo-grounded operating posture compared to the public example set.
  NEXT: patch the initial four role-local example docs to match the modern
    example shape while preserving each role's domain-specific scenario.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:54:04Z
  TYPE: MEASURE
  CLAIM: The initial role-local example quartet is now aligned to the richer
    top-level example posture. The platform, QA, security, and researcher
    role-local examples now expose the current entry-gate framing and fuller
    deliverable structure instead of the older minimal form.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/platform_engineer/examples/platform_task_flow.md:1-31
  - codex/context_compass/agent_onboarding/default/qa_engineer/examples/qa_task_flow.md:1-32
  - codex/context_compass/agent_onboarding/default/security_engineer/examples/security_review_flow.md:1-26
  - codex/context_compass/agent_onboarding/default/researcher/examples/researcher_task_flow.md:1-30
  - validation_result: `rg -n "AGENT_NAME|CERTIFY: APPROVED|Entry gate|Expected output format|Expected pass conditions|Risk/rollback|Residual risks \\+ approval needs|research_open_risks" codex/context_compass/agent_onboarding/default/platform_engineer/examples/platform_task_flow.md codex/context_compass/agent_onboarding/default/qa_engineer/examples/qa_task_flow.md codex/context_compass/agent_onboarding/default/security_engineer/examples/security_review_flow.md codex/context_compass/agent_onboarding/default/researcher/examples/researcher_task_flow.md`
  IMPACT: The first bounded role-local example slice is complete and no longer
    lags the refreshed top-level examples.
  NEXT: if the docs program continues, open a separate bounded lane for the
    fiction/editor role-local example set rather than widening this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:28:16Z
  TYPE: DECISION
  CLAIM: By explicit user direction to continue, the next bounded role-local
    slice now moves into a sibling task for the fiction/editor example set
    rather than widening this task beyond its initial four-role boundary.
  EVIDENCE:
  - user_instruction: `continue please`
  - codex/context_compass/tickets/tasks/2026-06-13_investigate_fiction_editor_role_local_example_doc_drift_task.md
  IMPACT: This keeps the initial role-local task truthful to its boundary while
    preserving forward progress in the docs program.
  NEXT: continue execution from the new fiction/editor role-local task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task follows the top-level example-doc cleanup. It is intentionally
bounded to the first four role-local example docs so drift can be assessed
without widening into all onboarding examples at once.
