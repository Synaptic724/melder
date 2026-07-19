<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Investigate Fiction/Editor Role-Local Example Doc Drift

## Metadata
- Task ID: TASK-2026-06-13-investigate-fiction-editor-role-local-example-doc-drift
- Story: none
- Epic: none
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-13T23:28:16Z
- Updated: 2026-06-13T23:32:09Z

## Objective
Investigate and refresh the remaining fiction/editor role-local example docs
under `agent_onboarding/default/*/examples/` so they do not lag the refreshed
top-level example flows.

## Ticket Contract
- ENTRY_GATE: the initial role-local quartet is already aligned, and the user
  explicitly directed continued documentation work.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md`
  - `codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md`
  - top-level comparison surfaces:
    - `codex/context_compass/examples/draft_writer_task_flow.md`
    - `codex/context_compass/examples/developmental_editor_task_flow.md`
    - `codex/context_compass/examples/line_copy_editor_task_flow.md`
    - `codex/context_compass/examples/proofreader_task_flow.md`
  - `codex/context_compass/attention_board.md`
  - this task
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-06-13_investigate_role_local_example_doc_drift_task.md`
  - the role-local and top-level example docs listed above
- EXIT_GATE:
  - at least one concrete fiction/editor role-local drift finding exists with
    evidence
  - the bounded four-file patch slice is explicit
  - no widening into continuity/story roles without a separate task
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  the fiction/editor role-local examples cannot be refreshed without changing
  their intended role-local purpose.

## Scope Boundaries
- In scope:
  - drift investigation and refresh for the four fiction/editor role-local
    example docs listed above
  - comparison against the already refreshed top-level examples
  - validating the refreshed role-local quartet
- Out of scope:
  - continuity/story role-local examples
  - wider `agent_onboarding` doc maintenance
  - top-level `examples/` maintenance already handled elsewhere

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to continue and the remaining
  fiction/editor role-local example set is the next bounded slice.

## Steps / Checklist
- [ ] Re-read the four role-local fiction/editor example docs.
- [ ] Verify their seams against the refreshed top-level examples.
- [ ] Record the concrete drift findings in `## Notes`.
- [ ] Patch the bounded four-file slice.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- refreshed fiction/editor role-local example docs
- evidence-backed note trail for the bounded slice

## Files / Paths Impacted
- `codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md`
- `codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md`
- `codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md`
- `codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md`
- `codex/context_compass/tickets/tasks/2026-06-13_investigate_fiction_editor_role_local_example_doc_drift_task.md`
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
- [ ] No widening into continuity/story roles without a separate task.
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
  - fiction/editor role-local example drift
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
  CLAIM: The next bounded slice is the remaining fiction/editor role-local
    example set. The first role-local quartet is already aligned, so the
    cleanest continuation is to patch the four draft/developmental/line-copy/
    proofreader examples as a separate task rather than widening the previous
    lane.
  EVIDENCE:
  - user_instruction: `continue please`
  - codex/context_compass/tickets/tasks/2026-06-13_investigate_role_local_example_doc_drift_task.md
  IMPACT: This keeps the docs program moving while preserving bounded task
    scope and avoiding silent expansion.
  NEXT: record the concrete drift finding and patch the four role-local docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:28:16Z
  TYPE: FACT
  CLAIM: The remaining fiction/editor role-local example set is still behind
    the refreshed top-level examples. The four role-local docs use the older
    concise example form and omit the richer entry-gate framing already present
    in the top-level versions.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md:1-18
  - codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md:1-17
  - codex/context_compass/examples/draft_writer_task_flow.md:1-37
  - codex/context_compass/examples/developmental_editor_task_flow.md:1-35
  - codex/context_compass/examples/line_copy_editor_task_flow.md:1-35
  - codex/context_compass/examples/proofreader_task_flow.md:1-35
  IMPACT: The role-local example set is still internally inconsistent even
    after the first role-local patch lane.
  NEXT: patch the four role-local docs to add the richer gate/workflow/output
    framing while preserving their role-specific scenarios.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:28:16Z
  TYPE: MEASURE
  CLAIM: The fiction/editor role-local quartet is now aligned to the richer
    top-level example posture. The draft, developmental, line-copy, and
    proofreader role-local examples now expose the current entry-gate framing
    and fuller deliverable/pass-condition structure instead of the older
    minimal form.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md:1-30
  - codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md:1-30
  - codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md:1-29
  - codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md:1-28
  - validation_result: `rg -n "AGENT_NAME|CERTIFY: APPROVED|Entry gate|Expected pass conditions|scene_objectives|scene_cut_add_log|style_sheet|final_issue_waivers" codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md`
  IMPACT: The second bounded role-local slice no longer lags the refreshed
    top-level examples.
  NEXT: if the docs program continues, open a separate bounded lane for the
    remaining continuity/story role-local examples rather than widening this
    task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:32:09Z
  TYPE: DECISION
  CLAIM: The fiction/editor role-local slice is locally complete and the docs
    program has advanced into the final sibling continuity/story task instead
    of widening this four-file lane beyond its boundary.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-13_investigate_continuity_story_role_local_example_doc_drift_task.md
  IMPACT: This task remains a clean bounded record of the fiction/editor
    refresh slice rather than a container for the rest of the role-local set.
  NEXT: continue execution from the continuity/story sibling task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is intentionally bounded to the fiction/editor role-local example
quartet so it can be refreshed without widening into the remaining
continuity/story roles.
