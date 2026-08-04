# Epic: Build Synaptic Finishing Developer Role
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the finishing role was registered, documented,
  example-backed, and wired into Context Compass onboarding surfaces.

## Metadata
- Epic ID: EPIC-2026-04-25-synaptic-finishing-developer-role-foundation
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T21:57:49Z
- Updated: 2026-04-26T15:08:08Z
- Target Window: 2026-Q2
- Related Program/Initiative: context_compass role system

## Problem / Opportunity
Context Compass currently has strong general engineering and QA role surfaces,
plus the user-defined `synaptic_python_developer` overlay, but it does not
have a role whose primary mission is slow, system-aware finishing work for
public-library documentation and tests.

That gap matters because high-value docstrings and tests in this repository are
not local-only polish. They depend on:
- ownership and lifecycle truth from architecture docs
- collaborator and boundary truth from components docs
- wiring truth from the readable source graph
- disciplined unit/component/integration depth instead of shallow one-shot
  coverage or filler assertions

## MRP Alignment (Most Reasonable Product)
This epic builds the smallest coherent role that is still trustworthy enough to
be used for real finishing work. The role must not be a thin alias or a prompt
stub. It must be a fully wired profile with:
- config and role-map registration
- a real onboarding read chain
- focused documentation skills
- focused testing skills
- explicit behavior and policy deltas for slow, deep finishing work

## Ticket Contract
- ENTRY_GATE: role-creation mechanics, current overlay structure, and current
  documentation/testing skill surfaces are investigated and documented with
  evidence before implementation deltas are finalized.
- EXECUTION_BOUNDARY:
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.md`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/**`
  - `context_compass/system_docs/patches/active/synaptic_finishing_developer_role_foundation/**`
  - workflow tickets and board state required for this lane
- DEPENDENCIES:
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - current `synaptic_python_developer` overlay
  - `engineer` role baseline
  - current architecture/components/graph docs
- EXIT_GATE: role is fully wired, required skill docs exist, patch artifacts are
  linked, and the new role behavior is reread and summarized.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementing the new role
  requires changing current default profile behavior or broadening shared
  baseline policy instead of staying in a user-defined overlay.

## Goals (Outcomes)
- Add a new user-defined role named `synaptic_finishing_developer`.
- Make the role inherit `engineer` directly.
- Require the role baseline to read:
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/graph_details_document.md`
  - `system_docs/readable_src_graph.json`
- Define rich documentation skills focused on:
  - system-aware public-library docstrings
  - contract-preserving comments
  - documentation/test alignment
- Define rich testing skills focused on:
  - unit tests
  - component tests
  - integration tests
  - mocking, regression, and truthful evidence reporting
- Encode a role posture that prefers multi-turn task execution, depth, and
  maximum value over speed.

## Non-Goals (Explicit Exclusions)
- Switching `profiles.active_profile` automatically.
- Rewriting `engineer` or `qa_engineer` shared baselines to absorb this role.
- Changing production runtime code outside the context-compass role system.
- Converting this role into a generic code-writing profile.

## Scope Boundaries
- In scope:
  - new role wiring
  - new role docs and skills
  - patch artifacts and workflow state for this lane
- Out of scope:
  - runtime source changes in `src/melder/**`
  - default profile switching
  - unrelated context-compass cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested immediate investigation plus
  implementation of a new finishing-focused role, so the epic needs active
  workflow state now.

## Success Metrics
- `synaptic_finishing_developer` appears in config profile lists and top-level
  role routing.
- The role resolves through `engineer` and loads a dedicated finishing overlay.
- The role baseline directly includes architecture/components/graph context.
- The role provides deeper documentation and testing skills than the existing
  `synaptic_python_developer` overlay in those areas.

## Requirements (Functional + Non-Functional)
- Functional:
  - new role folder and `SKILLS.MD`
  - config registration
  - top-level role-map registration
  - documentation skill pack
  - testing skill pack
- Non-functional:
  - explicit, non-superficial prose
  - task-based execution emphasis
  - public-library contract quality bar
  - truthful validation/reporting language

## Constraints / Assumptions
- Role remains a user-defined overlay.
- The current default active profile stays unchanged unless explicitly asked.
- Engineer baseline remains parent-first.
- System docs are intentionally mandatory baseline reads for this role.

## Dependencies / External References
- `PROFILE_CLASS_CREATION_GUIDE.md`
- `agent_onboarding/default/engineer/SKILLS.MD`
- `agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD`
- `agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md`
- `agent_onboarding/user_defined/synaptic_python_developer/skills/python/comments.md`
- `agent_onboarding/user_defined/synaptic_python_developer/skills/testing/testing_overview.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation artifacts and role design are explicit.
- [ ] Milestone 2: Role is registered and all role docs/skills are authored.
- [ ] Milestone 3: Workflow artifacts and role reread summary are complete.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-25-investigate-synaptic-finishing-developer-inputs
  - map current role mechanics and source skill surfaces
- [ ] Story: STORY-2026-04-25-implement-synaptic-finishing-developer-role
  - wire and author the new role

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete the investigation story and capture the role-design inputs.
- [ ] Task: Complete the implementation story and all child tasks.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The new role exists and is selectable via config and top-level role map.
- The role inherits `engineer` and keeps the shared baseline intact.
- The role has dedicated documentation skills and dedicated testing skills.
- The role baseline includes the required system docs and graph surfaces.
- The role behavior explicitly favors depth, accuracy, and multi-turn execution.

## Risks / Mitigations
- Risk: the role turns into a shallow copy of `synaptic_python_developer`.
  Mitigation: create new finishing-focused docs instead of only renaming the
  old overlay files.
- Risk: the role accidentally changes current default onboarding behavior.
  Mitigation: register it without switching `active_profile`.
- Risk: the role duplicates parent paths and becomes brittle.
  Mitigation: keep parent inheritance in `SKILLS.MD` and list only deltas.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Re-read the created role docs and config wiring.
- Confirm the role appears in:
  - config profile lists
  - top-level role map
  - user-defined role directory
- Do not claim runtime test execution unless it actually runs.

## Rollout / Adoption Plan
- Register the role for future selection.
- Leave current active profile unchanged.
- Summarize when to choose this role vs `synaptic_python_developer` or
  `qa_engineer`.

## Open Questions
- Should this role eventually gain dedicated examples separate from the
  `synaptic_python_developer` examples, or reuse those by reference?
- Should component-test placement/rules eventually be mirrored into a broader
  shared testing role, or stay finishing-role-specific?

## Decision Log
- The new role will remain a user-defined overlay and will not replace shared
  defaults.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/synaptic_finishing_developer_role_foundation/architecture_patch.md
  - system_docs/patches/active/synaptic_finishing_developer_role_foundation/component_patch_role_registration.md
  - system_docs/patches/active/synaptic_finishing_developer_role_foundation/component_patch_finishing_documentation_skills.md
  - system_docs/patches/active/synaptic_finishing_developer_role_foundation/component_patch_finishing_testing_skills.md
  - system_docs/patches/active/synaptic_finishing_developer_role_foundation/code_description_patch_role_onboarding_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decide after the role lane is accepted and canonical role
  behavior is stable.

## Notes
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: Context Compass profile creation is explicit and file-backed: create a
    `user_defined/<profile>/` folder, add a child `SKILLS.MD` with parent
    inheritance, and register the profile in config profile lists and role map.
  EVIDENCE:
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:83-170
  - context_compass/config/context_compass_config.yaml:3-67
  IMPACT: The new role cannot be a loose doc drop. It must be wired into the
    profile system and inherit cleanly from `engineer`.
  NEXT: create the epic/story/task set and the new role skeleton around that
    wiring contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: The current `synaptic_python_developer` overlay already centralizes
    documentation and testing skills, which makes it the right structural
    source to copy and deepen for a finishing-focused role.
  EVIDENCE:
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:9-40
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md:8-55
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/testing/testing_overview.md:8-120
  IMPACT: The new role should reuse the proven overlay shape but narrow its
    mission toward docstring/comment/test finishing work.
  NEXT: split the new role into investigation plus implementation stories and
    author a deeper finishing-specific skill pack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the creation of a new user-defined finishing role dedicated to
system-aware docstrings, comments, and tests. Investigation is required first
to ground the role in current role mechanics, current overlay structure, and
the architecture/components/graph surfaces the role must consume.
