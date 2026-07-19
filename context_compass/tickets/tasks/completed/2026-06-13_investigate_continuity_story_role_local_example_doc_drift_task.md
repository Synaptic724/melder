<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Investigate Continuity/Story Role-Local Example Doc Drift

## Metadata
- Task ID: TASK-2026-06-13-investigate-continuity-story-role-local-example-doc-drift
- Story: none
- Epic: none
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-13T23:28:16Z
- Updated: 2026-06-13T23:32:09Z

## Objective
Investigate and refresh the remaining continuity/story role-local example docs
under `agent_onboarding/default/*/examples/` so they do not lag the refreshed
top-level example flows.

## Ticket Contract
- ENTRY_GATE: the fiction/editor role-local slice is already aligned, and the
  user explicitly directed continued documentation work.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md`
  - top-level comparison surfaces:
    - `codex/context_compass/examples/continuity_fact_checker_task_flow.md`
    - `codex/context_compass/examples/story_designer_task_flow.md`
    - `codex/context_compass/examples/story_novel_artist_task_flow.md`
  - `codex/context_compass/attention_board.md`
  - this task
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-06-13_investigate_fiction_editor_role_local_example_doc_drift_task.md`
  - the role-local and top-level example docs listed above
- EXIT_GATE:
  - at least one concrete continuity/story role-local drift finding exists with
    evidence
  - the bounded three-file patch slice is explicit
  - no widening beyond these three files
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  the continuity/story role-local examples cannot be refreshed without changing
  their intended role-local purpose.

## Scope Boundaries
- In scope:
  - drift investigation and refresh for the three continuity/story role-local
    example docs listed above
  - comparison against the already refreshed top-level examples
  - validating the refreshed role-local trio
- Out of scope:
  - wider `agent_onboarding` doc maintenance
  - top-level `examples/` maintenance already handled elsewhere

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to continue and the remaining
  continuity/story role-local example set is the next bounded slice.

## Steps / Checklist
- [ ] Re-read the three role-local continuity/story example docs.
- [ ] Verify their seams against the refreshed top-level examples.
- [ ] Record the concrete drift findings in `## Notes`.
- [ ] Patch the bounded three-file slice.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- refreshed continuity/story role-local example docs
- evidence-backed note trail for the bounded slice

## Files / Paths Impacted
- `codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md`
- `codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md`
- `codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md`
- `codex/context_compass/tickets/tasks/2026-06-13_investigate_continuity_story_role_local_example_doc_drift_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: the role-local examples may intentionally remain lighter than top-level
  examples in some spots.
- Rollback: keep the edits scoped to richer entry-gate/workflow/output framing
  and do not invent new role semantics.

## Applicable Anti-Patterns
- [ ] No role-local rewrite before concrete drift is recorded.
- [ ] No widening beyond the bounded three-file slice.
- [ ] No importing top-level wording wholesale when the role-local source needs
      its own domain-specific scenario.

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
  - continuity/story role-local example drift
  - top-level versus role-local flow alignment
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-13T23:28:16Z
  TYPE: PLAN
  CLAIM: The next bounded slice is the remaining continuity/story role-local
    example set. The earlier role-local slices are aligned, so the cleanest
    continuation is to patch the three continuity/story role-local examples as
    their own bounded task.
  EVIDENCE:
  - user_instruction: `continue please`
  - codex/context_compass/tickets/tasks/2026-06-13_investigate_fiction_editor_role_local_example_doc_drift_task.md
  IMPACT: This preserves bounded scope while continuing the docs program.
  NEXT: record the concrete drift finding and patch the three role-local docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:28:16Z
  TYPE: FACT
  CLAIM: The remaining continuity/story role-local example set is still behind
    the refreshed top-level examples. The three role-local docs use the older
    concise example form and omit the richer entry-gate framing already present
    in the top-level versions.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md:1-19
  - codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md:1-19
  - codex/context_compass/examples/continuity_fact_checker_task_flow.md:1-34
  - codex/context_compass/examples/story_designer_task_flow.md:1-36
  - codex/context_compass/examples/story_novel_artist_task_flow.md:1-36
  IMPACT: The role-local example set is still internally inconsistent after the
    earlier role-local patches.
  NEXT: patch the three role-local docs to add the richer gate/workflow/output
    framing while preserving their role-specific scenarios.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:32:09Z
  TYPE: MEASURE
  CLAIM: The continuity/story role-local trio is now aligned to the richer
    top-level example posture. The continuity fact checker, story designer, and
    story novel artist role-local examples now expose the current entry-gate
    framing and fuller deliverable/pass-condition structure instead of the
    older minimal form.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md:1-30
  - codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md:1-31
  - codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md:1-32
  - validation_result: `rg -n "AGENT_NAME|CERTIFY: APPROVED|Entry gate|Expected pass conditions|fact_check_log|design_risk_register|cover_direction_brief" codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md`
  IMPACT: The final bounded role-local example slice no longer lags the
    refreshed top-level examples.
  NEXT: the role-local example set is locally clean for the bounded seams
    investigated in this program; wait for user direction before opening a new
    docs lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is intentionally bounded to the continuity/story role-local trio so
the remaining role-local drift can be resolved without widening beyond the last
obvious slice.
