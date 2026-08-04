# Task: Add role workflow manifests to onboarding readsets

## Metadata
- Task ID: TASK-2026-05-31-add-role-workflow-manifests-to-onboarding-readsets
- Story: none
- Status: done
- Owner: codex
- Agent Name: tester_0
- Priority: p1
- Created: 2026-05-31T11:13:02Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Make role-local workflows part of normal onboarding visibility by adding
workflow manifest reads to the role `SKILLS.MD` chain and by making the active
general workflows baseline-readable.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested that role-based workflows be added
  into onboarding read lists for each role.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/**/SKILLS.MD`
  - `codex/context_compass/tickets/tasks/2026-05-31_add_role_workflow_manifests_to_onboarding_readsets_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD`
  - `codex/context_compass/agent_onboarding/default/engineer/WORKFLOWS.MD`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD`
  - `codex/context_compass/agent_onboarding/default/general/skills/role_local_workflows.md`
- EXIT_GATE:
  - targeted role `SKILLS.MD` files include their workflow manifest paths
  - `general/SKILLS.MD` includes workflow governance plus active general
    workflow docs
  - the task and board state truthfully summarize the repair
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the workflow manifest model
  conflicts with the current active/on-demand distinction and the baseline read
  policy cannot stay coherent.

## Scope Boundaries
- In scope:
  - role `SKILLS.MD` onboarding readset updates
  - task + board routing for this lane
- Out of scope:
  - changing workflow semantics
  - changing workflow file contents
  - changing non-role onboarding docs unless strictly required for consistency

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a repo-wide onboarding
  manifest repair so workflow docs stop being omitted from normal role reads.

## Steps / Checklist
- [ ] Confirm the current workflow manifest model and inheritance path.
- [ ] Patch `general/SKILLS.MD` to include workflow governance and active
      general workflow docs.
- [ ] Patch each role `SKILLS.MD` to include that role's `WORKFLOWS.MD`.
- [ ] Re-read the touched manifests for consistency.
- [ ] Summarize the resulting onboarding behavior change.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further expansion.

## Deliverables
- one coherent onboarding readset repair across role `SKILLS.MD` files
- one task ticket recording the workflow-manifest baseline decision

## Files / Paths Impacted
- `codex/context_compass/agent_onboarding/**/SKILLS.MD`
- `codex/context_compass/tickets/tasks/2026-05-31_add_role_workflow_manifests_to_onboarding_readsets_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "WORKFLOWS\\.MD|role_local_workflows|workflows/" codex/context_compass/agent_onboarding`

## Risks / Rollback Notes
- Risk: on-demand workflows could be accidentally promoted into baseline reads
  if the manifest distinction is ignored.
- Rollback: restrict baseline additions to workflow manifests plus the active
  general workflow docs only.

## Applicable Anti-Patterns
- [ ] No workflow semantic drift beyond the existing manifest model.
- [ ] No promotion of on-demand workflows into the baseline readset without
      explicit reason.
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: workflow-manifest visibility, role-chain inheritance, and
  baseline versus on-demand read boundaries.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-31T11:13:02Z
  TYPE: FACT
  CLAIM: The workflow system already exists as a first-class role artifact
    model, but the normal role `SKILLS.MD` readsets do not currently force
    those workflow manifests into onboarding. `general/WORKFLOWS.MD` already
    lists active workflow docs and on-demand workflow docs, and
    `role_local_workflows.md` already states that active workflows are
    baseline-readable for the role. The gap is therefore onboarding visibility,
    not missing workflow semantics.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD:1-23
  - codex/context_compass/agent_onboarding/default/general/skills/role_local_workflows.md:1-28
  - codex/context_compass/agent_onboarding/default/general/SKILLS.MD:1-41
  - codex/context_compass/agent_onboarding/default/engineer/SKILLS.MD:1-39
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:1-34
  IMPACT: The repair should target role `SKILLS.MD` manifests rather than
    inventing a second workflow registry or changing workflow semantics.
  NEXT: patch the role `SKILLS.MD` chain so workflow manifests are baseline
    onboarding inputs and the active general workflow docs are explicitly read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T11:18:06Z
  TYPE: MEASURE
  CLAIM: The onboarding readset repair is landed across the role chain.
    `general/SKILLS.MD` now reads the workflow-governance skill, the general
    workflow manifest, and the currently active general workflow docs.
    `new/SKILLS.MD` now reads the workflow-governance skill plus its role
    manifest. Every other role `SKILLS.MD` now reads its role-local
    `WORKFLOWS.MD`, which makes workflow manifests part of normal onboarding
    visibility without promoting the general on-demand workflow docs into the
    baseline readset.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/SKILLS.MD:39-48
  - codex/context_compass/agent_onboarding/default/new/SKILLS.MD:24-28
  - codex/context_compass/agent_onboarding/default/engineer/SKILLS.MD:24-27
  - codex/context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:24-27
  - codex/context_compass/agent_onboarding/default/platform_engineer/SKILLS.MD:24-27
  - codex/context_compass/agent_onboarding/default/qa_engineer/SKILLS.MD:24-27
  - codex/context_compass/agent_onboarding/default/security_engineer/SKILLS.MD:24-27
  - codex/context_compass/agent_onboarding/default/continuity_fact_checker/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/developmental_editor/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/draft_writer/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/line_copy_editor/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/proofreader/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/researcher/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/story_designer/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/default/story_novel_artist/SKILLS.MD:18-20
  - codex/context_compass/agent_onboarding/user_defined/data_engineer/SKILLS.MD:8-10
  - codex/context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/SKILLS.MD:14-17
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:16-19
  IMPACT: Normal onboarding now exposes the workflow registry layer for every
    role, and general-role onboarding also reads the currently active general
    workflows directly instead of leaving them as unconsumed tree artifacts.
  NEXT: get user acceptance on the readset policy change or adjust if you want
    on-demand workflow docs promoted or demoted differently.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The user wants workflow awareness promoted from “docs sitting in the tree” to
“normal onboarding readset.” The existing manifest model is already present and
should be surfaced through role `SKILLS.MD` rather than replaced.

