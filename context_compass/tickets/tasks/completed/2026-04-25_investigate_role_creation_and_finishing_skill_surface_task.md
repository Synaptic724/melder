# Task: Investigate Role Creation And Finishing Skill Surface
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the current role-creation surface and
  finishing-focused skill gaps were investigated and captured for
  implementation.

## Metadata
- Task ID: TASK-2026-04-25-investigate-role-creation-and-finishing-skill-surface
- Story: STORY-2026-04-25-investigate-synaptic-finishing-developer-inputs
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T21:57:49Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Audit the current role-creation mechanics, the current `engineer` baseline, and
the current `synaptic_python_developer` documentation/testing skills so the new
finishing role can be built without guessing.

## Ticket Contract
- ENTRY_GATE: epic and investigation story exist and current role-doc evidence
  is available.
- EXECUTION_BOUNDARY:
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - `config/context_compass_config.yaml`
  - `agent_onboarding/default/engineer/SKILLS.MD`
  - `agent_onboarding/user_defined/synaptic_python_developer/**`
  - this task ticket
- DEPENDENCIES:
  - current user request
  - current role docs and current overlay skills
- EXIT_GATE: the role-creation contract, skill-source contract, and mandatory
  readset delta are explicit enough to stage implementation docs.
- FAILURE_ESCALATION: raise `BLOCKER` if the current role system cannot cleanly
  express the requested finishing-role behavior.

## Scope Boundaries
- In scope:
  - role-creation guide
  - current config and role map
  - current synaptic doc/test skill surface
  - current engineer baseline/on-demand split
- Out of scope:
  - editing the new role docs
  - config writes
  - patch doc authoring

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an investigation story and
  asked that implementation be grounded in renewed understanding.

## Steps / Checklist
- [ ] Read the role-creation guide and current config registration pattern.
- [ ] Read the current synaptic docstring/comment/testing skills.
- [ ] Record the first evidence-backed role-design findings in `## Notes`.
- [ ] Define the implementation split.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed role-creation contract
- evidence-backed source-skill inventory
- evidence-backed implementation split for the new role

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_investigate_role_creation_and_finishing_skill_surface_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/PROFILE_CLASS_CREATION_GUIDE.md`
  - `Get-Content codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`

## Risks / Rollback Notes
- Risk: finishing-role scope drifts into generic engineering behavior.
  Rollback: keep only evidence-backed deltas that support documentation/test
  finishing work.

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
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: Creating a new user-defined profile requires three structural moves:
    create the user-defined folder and child `SKILLS.MD`, inherit from the
    parent profile explicitly, and register the profile in config profile
    lists and role map.
  EVIDENCE:
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:83-170
  - context_compass/config/context_compass_config.yaml:3-67
  IMPACT: The new role implementation has to touch config, top-level role
    routing, and a new user-defined folder in one coherent slice.
  NEXT: map the existing documentation/testing overlay that should feed the new role.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: The current `synaptic_python_developer` overlay already splits Python
    finishing concerns into documentation and testing skill families, which is
    the right structural model for the new role.
  EVIDENCE:
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:17-40
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md:15-55
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/testing/testing_overview.md:17-120
  IMPACT: The new role should copy the family split and then deepen it around
    system-aware documentation and test depth.
  NEXT: confirm the engineer/system-doc baseline delta that the new role needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: `engineer` treats architecture/components/graph docs as on-demand
    reads, so the new finishing role must list those system docs directly in
    its active skill set if the role should always read them.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:11-23
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:45-59
  IMPACT: The finishing role cannot rely on inherited `engineer` behavior
    alone if architecture/components/graph context is mandatory baseline.
  NEXT: create the implementation story, tasks, and patch artifacts around
    that baseline-read decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task proves how to create the new role and what current sources should
feed it. The key design delta is that the new role must make system-doc reads
baseline instead of leaving them on-demand like `engineer`.
