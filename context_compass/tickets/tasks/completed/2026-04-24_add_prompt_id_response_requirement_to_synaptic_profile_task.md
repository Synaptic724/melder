# Task: Add Prompt Id Response Requirement To General Policy
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the `prompt_id` rule landed in the shared
  general baseline and the synaptic-only duplicate wording was removed.

## Metadata
- Task ID: TASK-2026-04-24-add-prompt-id-response-requirement-to-synaptic-profile
- Story:
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-24T22:37:53Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Add a shared general-layer response-tag requirement so every assistant response
carries a unique per-response `prompt_id`.

## Ticket Contract
- ENTRY_GATE: the user explicitly corrected the scope and requested the
  per-response `prompt_id` rule in the shared `general` layer instead of the
  user-defined overlay.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/default/general/AGENTS.MD`
  - `codex/context_compass/agent_onboarding/default/general/skills/agent_stance.md`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/behavioral_guidelines/synaptic_behavior_overrides.md`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `codex/context_compass/agent_onboarding/default/general/AGENTS.MD`
  - `codex/context_compass/agent_onboarding/default/general/skills/agent_stance.md`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/behavioral_guidelines/synaptic_behavior_overrides.md`
- EXIT_GATE: the shared general baseline explicitly requires a per-response
  unique `prompt_id`, the synaptic overlay no longer duplicates the rule, and
  the board routes the change cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the shared `prompt_id` rule
  needs a different formatting contract than `prompt_id: <value>`.

## Scope Boundaries
- In scope:
  - shared response-tag requirement
  - general policy/behavior docs
  - removal of duplicated overlay wording
  - routing/task state
- Out of scope:
  - unrelated communication-policy edits

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user corrected the requirement from synaptic-only to
  general baseline while keeping the field name `prompt_id`.

## Steps / Checklist
- [ ] Add the `prompt_id` response rule to the general policy docs.
- [ ] Remove the duplicated synaptic-only wording.
- [ ] Update routing state.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- general policy update for `prompt_id`
- removal of duplicated synaptic-only wording

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-24_add_prompt_id_response_requirement_to_synaptic_profile_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/agent_onboarding/default/general/AGENTS.MD
- codex/context_compass/agent_onboarding/default/general/skills/agent_stance.md
- codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD
- codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/behavioral_guidelines/synaptic_behavior_overrides.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/AGENTS.MD`
  - `Get-Content codex/context_compass/agent_onboarding/default/general/skills/agent_stance.md`

## Risks / Rollback Notes
- Risk: the rule remains duplicated across general and synaptic layers and
  drifts later.
  Rollback: keep the canonical wording in general only and strip overlay
  duplication immediately.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-24T22:37:53Z
  TYPE: FACT
  CLAIM: The original scope assumption was wrong. The user wants the response-
    tag rule in the shared `general` layer, not only in the
    `synaptic_python_developer` overlay. The field name remains `prompt_id`.
  EVIDENCE:
  - user_instruction: "if each response you make you apply a random string per convo that'd be good no repitition"
  - user_instruction: "read agents.md and ensure you add that into the script as a requirement"
  - user_instruction: "you can call it a prompt_id"
  - user_instruction: "oh not just synaptic_python_developer ,add it to general instead of the user_defined specifics please"
  - codex/context_compass/agent_onboarding/default/general/AGENTS.MD:156-221
  - codex/context_compass/agent_onboarding/default/general/skills/agent_stance.md:22-29
  IMPACT: The canonical rule belongs in the shared baseline, and the synaptic
    overlay should stop duplicating it.
  NEXT: move the rule into general and remove the synaptic duplicate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the `prompt_id` response-tag requirement. The canonical rule
should live in the shared `general` layer, and the synaptic overlay should not
carry a duplicate copy.
