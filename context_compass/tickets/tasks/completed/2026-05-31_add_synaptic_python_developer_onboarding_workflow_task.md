# Task: Add synaptic python developer onboarding workflow

## Metadata
- Task ID: TASK-2026-05-31-add-synaptic-python-developer-onboarding-workflow
- Story: none
- Status: done
- Owner: codex
- Agent Name: tester_0
- Priority: p1
- Created: 2026-05-31T11:29:07Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Create a reusable role-local workflow named
`synaptic_python_developer_onboarding` under the
`synaptic_python_developer` role and register it so future onboarding can use
that workflow directly.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested adding the quoted onboarding macro
  as a synaptic role workflow.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/`
  - `codex/context_compass/tickets/tasks/2026-05-31_add_synaptic_python_developer_onboarding_workflow_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `codex/context_compass/agent_onboarding/default/general/workflows/workflow_creation.md`
  - `codex/context_compass/agent_onboarding/default/general/skills/role_local_workflows.md`
  - `codex/context_compass/templates/workflow_advanced_template.md`
  - `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD`
- EXIT_GATE:
  - the workflow file exists
  - the synaptic workflow manifest registers it
  - the synaptic skills manifest reads it as part of onboarding
  - task and board state truthfully summarize the change
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested onboarding
  macro conflicts with the current certification/on-demand-read policy.

## Scope Boundaries
- In scope:
  - create the role-local workflow doc
  - register it in the synaptic workflow manifest
  - add it to the synaptic onboarding readset
- Out of scope:
  - changing global onboarding policy
  - changing unrelated role workflow manifests
  - changing runtime code

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new reusable synaptic role
  onboarding workflow.

## Steps / Checklist
- [ ] Read the workflow creation scaffolding docs and target role manifest.
- [ ] Define the workflow around the requested onboarding macro.
- [ ] Add the workflow file under the synaptic workflow folder.
- [ ] Register it in the synaptic `WORKFLOWS.MD` manifest.
- [ ] Add the workflow doc to the synaptic `SKILLS.MD` readset.
- [ ] Re-read the touched manifests for consistency.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further expansion.

## Deliverables
- one new synaptic role workflow doc
- one synced synaptic workflow manifest entry
- one synced synaptic skills readset entry

## Files / Paths Impacted
- `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md`
- `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD`
- `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`
- `codex/context_compass/tickets/tasks/2026-05-31_add_synaptic_python_developer_onboarding_workflow_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "synaptic_python_developer_onboarding|WORKFLOWS\\.MD" codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer`

## Risks / Rollback Notes
- Risk: the workflow could encode instructions that drift from the current
  certification/onboarding gates.
- Rollback: keep the workflow as a role-local macro that references the
  canonical onboarding docs and current role chain instead of replacing them.

## Applicable Anti-Patterns
- [ ] No workflow semantics that bypass current onboarding or certification.
- [ ] No silent manifest update without adding the actual workflow doc.
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
- Note focus: workflow trigger, manifest registration, and onboarding-readset
  alignment.
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
- DATETIME: 2026-05-31T11:29:07Z
  TYPE: PLAN
  CLAIM: The user wants the exact quoted synaptic onboarding macro turned into
    a real role-local workflow. The correct repo-native implementation is to
    create a workflow doc under the synaptic workflow folder, register it in
    the role `WORKFLOWS.MD`, and add the workflow doc to the synaptic role
    `SKILLS.MD` so the workflow is part of the role onboarding readset.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/workflows/workflow_creation.md:1-37
  - codex/context_compass/agent_onboarding/default/general/skills/role_local_workflows.md:1-28
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD:1-12
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:1-34
  IMPACT: The workflow can be added cleanly without changing global policy or
    inventing a second workflow registry.
  NEXT: scaffold the workflow doc from the advanced template and wire it into
    the synaptic manifest and skills readset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T11:31:30Z
  TYPE: MEASURE
  CLAIM: The new workflow is landed as
    `agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md`.
    The synaptic workflow manifest now registers it as an active workflow, and
    the synaptic role `SKILLS.MD` now reads it as part of the role onboarding
    readset. The workflow itself encodes the requested macro: start from
    `AGENTS.MD`, onboard as `synaptic_python_developer`, use `Get-Content`,
    avoid agents, and read `src_architecture.md`, `src_components.md`, and
    `readable_src_graph.json`.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md:1-156
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD:1-16
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:13-20
  IMPACT: The synaptic role now has a concrete reusable onboarding workflow
    that is both discoverable in the role workflow manifest and baseline-readable
    in the role onboarding chain.
  NEXT: get user acceptance on the workflow wording or adjust the workflow if
    you want a different onboarding/certification boundary encoded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:46:27Z
  TYPE: FACT
  CLAIM: The workflow trigger contract is now tightened so the workflow name
    alone is sufficient. The source-doc bundle
    (`src_architecture.md`, `src_components.md`, `readable_src_graph.json`)
    and the `Get-Content` / no-agent / up-to-30-thread posture are now
    explicitly embedded as implicit workflow behavior rather than additional
    user-supplied inputs.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md:3-43
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md:95-111
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/workflows/synaptic_python_developer_onboarding.md:147-151
  IMPACT: The user no longer needs to restate the architecture/components/readable-graph bundle to trigger the workflow correctly.
  NEXT: get user acceptance on the tightened trigger semantics or adjust only if
    a different shorthand should also map to this workflow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This lane exists only to add one new synaptic role-local workflow and wire it
into the role onboarding manifests cleanly.

